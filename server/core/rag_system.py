import os
import textwrap
import logging
import time
import json
import sqlite3
import uuid
import asyncio

from typing import Optional, List, Dict, Any, Tuple
from openai import APIError, APIStatusError, RateLimitError

from .config import settings
from .openai_interaction import OpenAIInteraction
from .local_db import get_local_db 

# Ensure database utilities are available for direct DB access
from core.database import get_db_connection, close_db_connection

logger = logging.getLogger("rag_system")

class HybridRAGSystem:
    def __init__(self, openai_interaction: OpenAIInteraction):
        self.config = settings
        self.openai_interaction = openai_interaction
        self.local_db = get_local_db() # Get local_db instance for RAG context
        if self.local_db is None: logger.warning("HybridRAGSystem initialized WITHOUT a functional local database.")
        else: logger.info("HybridRAGSystem initialized WITH local database.")


    def add_user_document_for_session(self, session_id: str, file_path: str, original_filename: str, db_conn: sqlite3.Connection) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Handles uploading the document to OpenAI, creating a Vector Store,
        and persisting the OpenAI resource IDs (file_id, vector_store_id) to the database.
        Deletes the local temporary file after successful OpenAI upload.

        Args:
            session_id (str): The unique ID for the user's session/document.
            file_path (str): The local path to the temporary file to be uploaded.
            original_filename (str): The original name of the file.
            db_conn (sqlite3.Connection): An active database connection for persisting IDs.

        Returns:
            Tuple[bool, str, Optional[str], Optional[str]]:
                (success_status, message, openai_file_id, openai_vector_store_id)
                openai_file_id and openai_vector_store_id are returned if successful, None otherwise.
        """
        logger.info(f"Processing user document for session '{session_id}': '{original_filename}' from path '{file_path}'")
        
        cursor = db_conn.cursor() # Use the provided database connection
        file_id_openai = None
        vector_store_id_openai = None

        try:
            # 1. Upload file to OpenAI
            logger.info(f"Uploading file '{original_filename}' to OpenAI...")
            file_id_openai = self.openai_interaction.upload_file(file_path, purpose="assistants")
            if not file_id_openai:
                message = f"Failed to upload file {original_filename} to OpenAI for session {session_id}."
                logger.error(message)
                # Update DB status on failure immediately
                cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ("failed_upload", message, session_id))
                db_conn.commit()
                return False, message, None, None

            logger.info(f"File uploaded successfully. OpenAI File ID: {file_id_openai}")
            
            # 2. Create Vector Store with the uploaded file
            logger.info("Creating OpenAI Vector Store...")
            # Generate a unique name for the vector store
            vs_name = f"vs_{session_id}_{original_filename.replace(' ', '_')[:50]}_{uuid.uuid4().hex[:8]}" 
            vector_store_id_openai = self.openai_interaction.create_vector_store_with_files(name=vs_name, file_ids=[file_id_openai])
            if not vector_store_id_openai:
                message = f"Failed to create Vector Store for file ID {file_id_openai} (session {session_id})."
                logger.error(message)
                # Clean up uploaded file if VS creation failed
                try: self.openai_interaction.delete_file(file_id_openai)
                except Exception as e: logger.warning(f"Failed to delete OpenAI file {file_id_openai} after VS creation failure: {e}")
                
                # Update DB status on failure
                cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ("failed_vs_creation", message, session_id))
                db_conn.commit()
                return False, message, file_id_openai, None

            logger.info(f"Vector Store created successfully. VS ID: {vector_store_id_openai}")

            # 3. Persist OpenAI resource IDs to the database
            cursor.execute("""
                INSERT OR REPLACE INTO openai_resources (openai_resource_id, document_id, openai_file_id, openai_vector_store_id)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), session_id, file_id_openai, vector_store_id_openai)) # Generate a new UUID for the openai_resource_id
            
            db_conn.commit() # Commit the resource ID insertion
            logger.info(f"OpenAI resource IDs for session {session_id} saved to DB.")

            # 4. Delete the local temporary file IMMEDIATELY after successful OpenAI upload/VS creation.
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"[{session_id}] Deleted local temporary file '{file_path}' after successful OpenAI upload and VS creation.")
                except OSError as e:
                    logger.error(f"[{session_id}] Error deleting temporary file {file_path}: {e}")

            message = f"User document '{original_filename}' uploaded and Vector Store '{vector_store_id_openai}' created successfully."
            logger.info(message)
            
            return True, message, file_id_openai, vector_store_id_openai

        except sqlite3.Error as e:
            logger.error(f"Database error in add_user_document_for_session for session {session_id}: {e}", exc_info=True)
            db_conn.rollback() # Rollback any DB changes if error occurs within this function
            message = f"Database error during document processing: {e}"
            # Clean up partially created OpenAI resources if error before full commit
            if file_id_openai:
                 try: self.openai_interaction.delete_file(file_id_openai)
                 except Exception as e_clean: logger.warning(f"Failed to delete OpenAI file {file_id_openai} during DB error cleanup: {e_clean}")
            if vector_store_id_openai:
                 try: self.openai_interaction.delete_vector_store(vector_store_id_openai)
                 except Exception as e_clean: logger.warning(f"Failed to delete OpenAI VS {vector_store_id_openai} during DB error cleanup: {e_clean}")
            return False, message, None, None
        except Exception as e:
            logger.error(f"Unexpected error in add_user_document_for_session for session {session_id}: {e}", exc_info=True)
            message = f"Unexpected error during document processing: {e}"
            # Clean up partially created OpenAI resources
            if file_id_openai:
                 try: self.openai_interaction.delete_file(file_id_openai)
                 except Exception as e_clean: logger.warning(f"Failed to delete OpenAI file {file_id_openai} during unexpected error cleanup: {e_clean}")
            if vector_store_id_openai:
                 try: self.openai_interaction.delete_vector_store(vector_store_id_openai)
                 except Exception as e_clean: logger.warning(f"Failed to delete OpenAI VS {vector_store_id_openai} during unexpected error cleanup: {e_clean}")
            return False, message, None, None


    def _get_system_prompt(self, focus_area: str, original_filename: str, local_context_str: str, query: str, custom_instructions: Optional[str] = None) -> str:
        """
        Selects or generates the appropriate system prompt based on the focus area.
        Ensures an indicative, tentative, or suggestive tone while preserving directives.
        **Emphasizes generating comprehensive content based on document detail.**
        """
        base_intro = f"""
            **Framework Definitions (from COEQWAL Context - Four Equity Dimensions):**
            - **Recognitional Equity:** Concerns the fair and inclusive recognition of diverse groups, their unique identities, histories, and cultural values in policies, processes, and outcomes. It asks if all voices are seen and valued.
            - **Procedural Equity:** Focuses on fair and inclusive processes for decision-making. It examines whether all affected parties have meaningful opportunities to participate, influence, and access information.
            - **Distributional Equity:** Addresses the fair and just distribution of benefits and burdens. It questions whether resources, services, and environmental risks are equitably shared among all groups, avoiding disproportionate impacts on any particular community.
            - **Structural Equity:** Seeks to identify and address the underlying systemic barriers, institutional practices, and power imbalances that perpetuate inequities.

            --- START CONTEXT FROM COEQWAL DOCUMENT ---
            {local_context_str if local_context_str else 'No definitions or context from the COEQWAL document were retrieved from the COEQWAL Framework document.'}
            --- END CONTEXT FROM COEQWAL DOCUMENT ---

            **User Document Name:** {original_filename}
            **User Query:** {query}

            **IMPORTANT - Output Style & Tone:** Please write your analysis in clear, accessible language. Avoid overly academic or technical jargon.
            Crucially, your analysis should be presented in a **tentative, suggestive, or indicative tone**. Avoid definitive or authoritative statements. You might use phrases such as: "This could suggest...", "It may indicate...", "A possible interpretation is...", "It appears to...", "Could be seen as...", "There seems to be an indication that...", "The document seems to imply...", "It might be perceived as...", "It might suggest the presence of...".
            
            **Content Extent:** Provide a comprehensive response, extracting all relevant information from the document. **If the document does not explicitly provide information for a particular point, state that the document does not appear to provide sufficient detail or does not directly address that aspect, rather than hallucinating.** Elaborate thoroughly on each finding where content allows, aiming for multiple paragraphs for each section/point if supported by the document. Conclude your response with a bulleted summary of the key findings.
        """
        
        if focus_area == "custom" and custom_instructions:
            return textwrap.dedent(f"""
                **Your Task:** You are an equity analyst. Your goal is to analyze the uploaded 'User Document' based on a specific set of custom instructions provided by the user. You should strive to follow these instructions while using the COEQWAL Equity Framework as a guiding lens.

                {base_intro}

                **User's Custom Focus Instructions:**
                --- START OF USER INSTRUCTIONS ---
                {custom_instructions}
                --- END OF USER INSTRUCTIONS ---

                **Your Analysis Steps:**
                1.  Thoroughly consider the User's Custom Focus Instructions.
                2.  You may identify and extract all parts from the User Document that appear relevant to these instructions and the user's query.
                3.  Where applicable, you might consider how the COEQWAL dimensions (Recognition, Procedure, Distribution, Structure) could help illuminate the analysis as per the user's instructions.
                4.  Strive to provide a balanced view, discussing both potential strengths and possible weaknesses that you might identify.
                5.  Where possible, you may refer to instances or examples from the User Document that could support your observations.
                6.  If the document seems to lack the necessary information to follow the instructions, it may be appropriate to state this limitation.

                **Final Output:** Provide a detailed analysis that directly addresses the User's Custom Focus Instructions. Start with a clear overview, then offer the detailed analysis, and conclude with a bulleted summary of your key findings. Ensure comprehensive coverage based on available information.
            """).strip()

        elif focus_area == "vulnerable_groups":
            return textwrap.dedent(f"""
                **Your Task:** You are an equity analyst. Your primary goal is to analyze how the uploaded 'User Document' discusses or potentially impacts **vulnerable groups**. You should use the user's query and the COEQWAL Equity Framework to guide your analysis.

                {base_intro}

                **Instructions for Vulnerable Group Analysis:**
                1.  **Identify Vulnerable Groups:** You might look for any groups in the User Document that could be negatively affected or appear to have special needs (e.g., based on income, race, location, disability, language, etc.). Please elaborate comprehensively on any groups identified and their context.
                2.  **Recognition (Recognitional Equity):** Consider if the document seems to acknowledge these groups and their unique situations, or if they might be overlooked. Provide comprehensive detail on this aspect.
                3.  **Fair Process (Procedural Equity):** Does the document appear to describe a fair process for these groups to participate in decisions or potentially receive help? Detail the mechanisms or apparent lack thereof.
                4.  **Fair Outcomes (Distributional Equity):** Could the document suggest whether these groups might receive a fair share of benefits and appear protected from harm? Provide a thorough assessment of potential outcomes.
                5.  **Addressing Root Causes (Structural Equity):** Does the document seem to address any long-standing barriers or systems that might disadvantage these groups? Elaborate on the structural aspects that appear relevant.
                6.  **Suggest Evidence:** Where possible, you may refer to specific examples or quotes from the *User Document* that could support your observations.
                7.  **Present a Balanced View:** Discuss both the potential strengths (positive considerations) and possible weaknesses (potential concerns) that you might discern in the User Document comprehensively, providing ample detail.
                8.  **Handle Missing Information:** If the User Document appears to lack detail on this topic, it may be appropriate to state this clearly.

                **Final Output:** Provide a **thorough and comprehensive** analysis focused on vulnerable groups, supported by specific examples from the document. Start with a clear overview and ensure each point is well-developed with sufficient content based on the document.
                """).strip()

        elif focus_area == "severity_of_impact":
            return textwrap.dedent(f"""
                **Your Task:** You are an equity analyst. Your primary goal is to assess the **potential severity of impacts**—both positive and negative—that might be described or implied in the uploaded 'User Document'. You should use the user's query and the COEQWAL Equity Framework to guide your analysis of how these potential impacts are handled.

                {base_intro}

                **Instructions for Severity of Impact Analysis:**
                1.  **Identify Key Impacts:** You might try to identify the main potential consequences or outcomes (both positive and negative) that could be suggested by the actions or policies described in the User Document. Please elaborate on these impacts in detail.
                2.  **Assess Severity:** For each identified impact, consider how serious it might be. This could involve evaluating the potential number of people affected, the possible duration of the impact, and its apparent reversibility. Provide detailed insights and reasoning.
                3.  **Distribution of Severe Impacts (Distributional Equity):** Does the document seem to indicate if the most severe potential negative impacts might be unfairly concentrated on certain groups? Detail any disproportionate effects that appear.
                4.  **Acknowledgement of Severity (Recognitional Equity):** Could the document suggest whether it acknowledges that some groups might be potentially impacted more severely than others? Provide comprehensive detail on this recognition or its absence.
                5.  **Process for Addressing Severe Impacts (Procedural Equity):** Does the document appear to describe a fair process for evaluating and possibly dealing with severe impacts? Elaborate on these processes and their perceived fairness.
                6.  **Structural Link to Severity (Structural Equity):** Do the severe potential impacts seem to stem from deeper, systemic issues? Discuss any apparent structural connections and their implications.
                7.  **Suggest Evidence:** Where possible, you may refer to specific examples or data from the *User Document* that could support your observations.
                8.  **Present a Balanced View:** Discuss both significant potential positive outcomes and possible severe negative impacts comprehensively, ensuring ample detail based on the document.
                9.  **Handle Missing Information:** If the User Document appears to lack detail on the severity of impacts, it may be appropriate to state this clearly.
                
                **Final Output:** Provide a **thorough and comprehensive** analysis focused on the potential severity of impact, supported by specific examples from the document. Start with a clear overview and ensure each point is well-developed with sufficient content based on the document.
                """).strip()

        elif focus_area == "mitigation_strategies":
            return textwrap.dedent(f"""
                **Your Task:** You are an equity analyst. Your primary goal is to evaluate the **mitigation strategies** (plans to reduce harm) that might be discussed or implied in the uploaded 'User Document'. You should use the user's query and the COEQWAL Equity Framework to assess how fair and potentially effective these strategies appear to be.

                {base_intro}

                **Instructions for Mitigation Strategy Analysis:**
                1.  **Identify Mitigation Strategies:** You might look for any specific plans or actions in the User Document that appear to be designed to prevent, reduce, or address potential negative impacts. Provide a detailed list and description of these strategies.
                2.  **Evaluate Strategy Fairness and Effectiveness:**
                    *   **Recognition:** Do the strategies seem to consider the unique needs of the people who might be most affected? Elaborate comprehensively on this consideration.
                    *   **Fair Process:** Was the process for considering or creating these strategies seemingly fair and inclusive? Detail the procedural aspects and their apparent strengths or weaknesses.
                    *   **Fair Outcomes:** Could the strategies actually help those who might need it most, or do they appear to introduce new potential challenges? Provide a thorough assessment of potential outcomes and equity implications.
                    *   **Addressing Root Causes:** Do the strategies seem to address the underlying problem, or could they be perceived as more of a temporary measure? Elaborate on their systemic impact and potential for long-term change.
                3.  **Consider Unintended Consequences:** Does the User Document hint at potential new problems that the strategies themselves might inadvertently create? Discuss these potential issues in detail.
                4.  **Assess Sufficiency:** Do the strategies appear to be sufficiently robust to address the problem they are meant to target? Provide a comprehensive assessment of their perceived adequacy.
                5.  **Suggest Evidence:** Where possible, you may refer to specific details from the *User Document* that could support your evaluation.
                6.  **Present a Balanced View:** Discuss both the potential strengths and possible weaknesses of the suggested mitigation strategies comprehensively, ensuring ample detail for each based on the document.
                7.  **Handle Missing Information:** If the User Document appears to lack detail on mitigation strategies, it may be appropriate to state this clearly.

                **Final Output:** Provide a **thorough and comprehensive** analysis focused on mitigation strategies, supported by specific examples from the document. Start with a clear overview and ensure each point is well-developed with sufficient content based on the document.
            """).strip()

        else: # Default to the general COEQWAL analysis prompt
            return textwrap.dedent(f"""
                **Your Task:** You are an equity analyst. Your goal is to provide a balanced analysis of the uploaded 'User Document' based on the user's query, using the COEQWAL Equity Framework (Recognition, Procedure, Distribution, and Structure) as your guide. You might identify both potential strengths and possible areas of concern.

                {base_intro}

                **Instructions for General Analysis:**
                1.  **Search the User Document:** You may identify sections of the document that appear relevant to the user's query.
                2.  **Apply COEQWAL Framework:** For each relevant part, it might be useful to evaluate it using the four dimensions: Recognition, Procedure, Distribution, and Structure. Provide comprehensive details for each dimension, exploring various facets.
                3.  **Identify Strengths and Potential Concerns:** Consider whether certain points could be interpreted as positive alignments with equity or as potential areas of concern. Elaborate thoroughly on these findings with detailed reasoning.
                4.  **Suggest Evidence:** Where possible, you may refer to instances or examples from the *User Document* that could support your observations.
                5.  **Address Information Gaps:** If the User Document appears to lack detail on a specific aspect, it may be appropriate to note this limitation.

                **Final Output:** Provide a balanced analysis of the User Document. Start with a clear overview, then offer the detailed analysis, and conclude with a bulleted summary of your key potential strengths and concerns. Ensure comprehensive coverage for all aspects based on the document.
            """).strip()

    # Method main.py calls for chat queries
    async def answer_question(
        self,
        session_id: str,
        query: str,
        focus_area: str = "general",
        custom_instructions: Optional[str] = None,
        db_conn: sqlite3.Connection = None
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Answers a query using OpenAI's file search tool (RAG).
        Retrieves necessary OpenAI Vector Store ID and document metadata from the DB.
        """
        if not query:
            return "Please provide a query.", [], []

        logger.info(f"Answering query for session {session_id} with focus: {focus_area}")
        
        if not db_conn:
            logger.error("Database connection not provided to answer_question.")
            return "Error: Internal server issue (DB connection missing for RAG).", [], []

        user_vector_store_id = None
        original_filename = "N/A"
        document_analysis_status = "not_found" # Using 'analysis_status' from DB for RAG condition

        try:
            # Fetch document info and OpenAI VS ID from DB
            cursor = await asyncio.to_thread(db_conn.cursor)
            doc_data = await asyncio.to_thread(
                cursor.execute,
                """
                SELECT d.original_filename, d.analysis_status, o.openai_vector_store_id
                FROM documents d
                LEFT JOIN openai_resources o ON d.document_id = o.document_id
                WHERE d.document_id = ? AND d.source = 'user' -- Ensure it's a user document
                """,
                (session_id,)
            )
            doc_data = await asyncio.to_thread(cursor.fetchone)

            if not doc_data:
                logger.warning(f"No active user document found in DB for session {session_id}. Query will proceed without document-specific RAG.")
                user_vector_store_id = None
                original_filename = "Generic Document"
                document_analysis_status = "not_found"
            else:
                original_filename, document_analysis_status, user_vector_store_id = doc_data
                logger.debug(f"Document found for session {session_id}. Analysis Status: '{document_analysis_status}'. VS ID: '{user_vector_store_id}'")

            # --- Local DB context (for COEQWAL framework definitions) ---
            local_db_instance = self.local_db # Access the local_db instance stored in self
            local_chunks = local_db_instance.search(query, top_k=self.config.TOP_K_LOCAL) if local_db_instance else []
            local_context_str = self._format_local_context_for_prompt(local_chunks)

            # Generate the prompt for the LLM
            prompt_content_string = self._get_system_prompt(
                focus_area,
                original_filename,
                local_context_str,
                query,
                custom_instructions
            )

            tools = []
            # Add OpenAI file_search tool ONLY if a Vector Store ID is available
            # AND the document's analysis_status in DB is 'completed'
            if user_vector_store_id and document_analysis_status == "completed":
                tools.append({
                    "type": "file_search",
                    "vector_store_ids": [user_vector_store_id],
                    "max_num_results": self.config.MAX_NUM_RESULTS,
                })
            else:
                logger.warning(f"OpenAI file search disabled for session {session_id}. Document status: {document_analysis_status}, VS ID: {user_vector_store_id}. It needs to be 'completed'.")

            kwargs = {
                "model": self.config.RESPONSES_MODEL,
                "input": prompt_content_string,
                #"temperature": self.config.TEMPERATURE,
                "max_output_tokens": self.config.MAX_OUTPUT_TOKENS,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["include"] = ["file_search_call.results"]
            
            # --- MAKE OPENAI API CALL ---
            response_openai = await asyncio.to_thread(self.openai_interaction.client.responses.create, **kwargs)

            # Parse the OpenAI response to extract the final answer and any retrieved sources
            final_answer: Optional[str] = None
            for item in response_openai.output:
                if getattr(item, "type", None) == "message" and hasattr(item, "content"):
                    for content_item in item.content:
                        if getattr(content_item, "type", None) == "output_text":
                            if final_answer is None:
                                final_answer = getattr(content_item, "text", "").strip() or "Model returned empty answer."

            retrieved_chunks_from_openai_tool: List[str] = []
            for item in response_openai.output:
                if getattr(item, "type", None) == "file_search_call":
                    results = getattr(item, "results", None)
                    if results:
                        for res in results:
                            file_name = getattr(res, "file_name", None) or getattr(res, "filename", None) or "Unknown file"
                            chunk_text = getattr(res, "text", "")
                            snippet = chunk_text[:400] + "..." if len(chunk_text) > 400 else chunk_text
                            retrieved_chunks_from_openai_tool.append(
                                f"Source from {file_name}:\n<blockquote>{snippet}</blockquote>"
                            )

            if final_answer is None:
                final_answer = "No valid answer returned by the model."

            return final_answer, local_chunks, retrieved_chunks_from_openai_tool

        except sqlite3.Error as e:
            logger.error(f"Database error during query processing in rag_system for session {session_id}: {e}", exc_info=True)
            return "Error: Database issue accessing session data for RAG.", [], []
        except Exception as e:
            logger.error(f"Unexpected error during query processing in rag_system for session {session_id}: {e}", exc_info=True)
            return f"Error: An unexpected issue occurred during RAG response generation: {e}", [], []

    # This is a helper method, kept for consistency if it's called by _get_system_prompt
    def _format_local_context_for_prompt(self, local_results: List[Dict[str, Any]]) -> str:
        if not local_results: return ""
        context_parts = []
        for i, result in enumerate(local_results):
            text = result.get("text", "").strip()
            metadata = result.get("metadata", {})
            headings = metadata.get("headings", [])
            score = result.get("score")
            header_parts = [f"Local Source {i+1}/{len(local_results)}"]
            if score is not None: header_parts.append(f"Score: {score:.4f}")
            if headings: header_parts.append(f"Section: '{headings[-1]}'")
            else: header_parts.append("Section: N/A")
            pos_index = metadata.get("position_index", -1); pos_total = metadata.get("position_total", -1)
            if pos_index != -1 and pos_total != -1: header_parts.append(f"Position: {pos_index+1}/{pos_total}")
            header = f"-- {' | '.join(header_parts)} --"
            context_parts.append(f"{header}\n{text}")
        return "\n\n".join(context_parts)