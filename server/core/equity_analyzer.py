import os
import json
import logging
import shutil
import tempfile
import textwrap
import time
import asyncio
import sqlite3

from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI

try:
    from PyPDF2 import PdfReader
except ImportError:
    logging.warning("PyPDF2 is not installed. PDF title extraction might be limited.")
    PdfReader = None

# Imports from core
from .config import settings
from .openai_interaction import OpenAIInteraction
from .rag_system import HybridRAGSystem
from core.database import get_db_connection, close_db_connection 

logger = logging.getLogger("equity_analyzer")

# --- Global Constants and JSON Skeleton (from previous definition) ---
JSON_SKELETON = """
{
  "id": "...",
  "source": "user",
  "document": {
    "filename": "...",
    "title": "...",
    "size_kb": 0,
    "upload_date_utc": "..."
  },
  "test_fields": {
    "test_pic": "...",
    "test_subject": "25",
    "test_title": "40",
    "test_short_caption": "50",
    "test_long_caption": "120",
    "test_date": "...", 
    "test_scope": "..."
  },
  "overall_analysis_by_perspective": [
    {
      "group_name": "Policy Makers",
      "group_description": "the overall equity implications from the perspective of federal and state policymakers, considering their regulatory responsibilities and influence on equity outcomes. This assessment could indicate how effectively equity measures are embedded in their processes, or if there might be systematic gaps in addressing social or racial disparities.",
      "analyses": {
        "general_equity_assessment": {
          "title": "General Equity Assessment for Policy Makers",
          "summary": "200",
          "recognitional_equity": { "title": "Recognitional Equity", "findings": "150" },
          "procedural_equity": { "title": "Procedural Equity", "findings": "150" },
          "distributional_equity": { "title": "Distributional Equity", "findings": "150" },
          "structural_equity": { "title": "Structural Equity", "findings": "150" },
          "sources": []
        },
        "vulnerable_groups_analysis": {
          "title": "Vulnerable Groups Analysis for Policy Makers",
          "summary": "...",
          "identified_groups_and_impacts": "...",
          "equity_assessment_summary": "...",
          "conclusion": "...",
          "sources": []
        },
        "severity_impact_analysis": {
          "title": "Severity of Impact Analysis for Policy Makers",
          "summary": "...",
          "high_severity_impacts": "...",
          "moderate_severity_impacts": "...",
          "equity_implications_of_impacts": "...",
          "conclusion": "...",
          "sources": []
        },
        "mitigation_strategies_analysis": {
          "title": "Mitigation Strategies Analysis for Policy Makers",
          "summary": "...",
          "identified_strategies": "...",
          "equity_assessment": "...",
          "conclusion": "...",
          "sources": []
        }
      }
    },
    {
      "group_name": "Residents",
      "group_description": "the overall equity implications from the perspective of ordinary residents, especially those in vulnerable communities, regarding their access to clean and affordable water. The assessment might indicate if community voices appear to be sufficiently represented in decisions affecting their health and well-being.",
      "analyses": {
        "general_equity_assessment": {
          "title": "General Equity Assessment for Residents",
          "summary": "200",
          "recognitional_equity": { "title": "Recognitional Equity", "findings": "150" },
          "procedural_equity": { "title": "Procedural Equity", "findings": "150" },
          "distributional_equity": { "title": "Distributional Equity", "findings": "150" },
          "structural_equity": { "title": "Structural Equity", "findings": "150" },
          "sources": []
        },
        "vulnerable_groups_analysis": {
          "title": "Vulnerable Groups Analysis for Residents",
          "summary": "...",
          "identified_groups_and_impacts": "...",
          "equity_assessment_summary": "...",
          "conclusion": "...",
          "sources": []
        },
        "severity_impact_analysis": {
          "title": "Severity of Impact Analysis for Residents",
          "summary": "...",
          "high_severity_impacts": "...",
          "moderate_severity_impacts": "...",
          "equity_implications_of_impacts": "...",
          "conclusion": "...",
          "sources": []
        },
        "mitigation_strategies_analysis": {
          "title": "Mitigation Strategies Analysis for Residents",
          "summary": "...",
          "identified_strategies": "...",
          "equity_assessment": "...",
          "conclusion": "...",
          "sources": []
        }
      }
    },
    {
      "group_name": "Farmers/Business Owners",
      "group_description": "the overall equity implications from the perspective of farmers and business owners, particularly small operators, considering their roles as regulated entities and community members. The assessment could indicate if compliance costs or infrastructure funding might impose disproportionate economic hardship.",
      "analyses": {
        "general_equity_assessment": {
          "title": "General Equity Assessment for Farmers/Business Owners",
          "summary": "200",
          "recognitional_equity": { "title": "Recognitional Equity", "findings": "150" },
          "procedural_equity": { "title": "Procedural Equity", "findings": "150" },
          "distributional_equity": { "title": "Distributional Equity", "findings": "150" },
          "structural_equity": { "title": "Structural Equity", "findings": "150" },
          "sources": []
        },
        "vulnerable_groups_analysis": {
          "title": "Vulnerable Groups Analysis for Farmers/Business Owners",
          "summary": "...",
          "identified_groups_and_impacts": "...",
          "equity_assessment_summary": "...",
          "conclusion": "...",
          "sources": []
        },
        "severity_impact_analysis": {
          "title": "Severity of Impact Analysis for Farmers/Business Owners",
          "summary": "...",
          "high_severity_impacts": "...",
          "moderate_severity_impacts": "...",
          "equity_implications_of_impacts": "...",
          "conclusion": "...",
          "sources": []
        },
        "mitigation_strategies_analysis": {
          "title": "Mitigation Strategies Analysis for Farmers/Business Owners",
          "summary": "...",
          "identified_strategies": "...",
          "equity_assessment": "...",
          "conclusion": "...",
          "sources": []
        }
      }
    }
  ],
  "overall_summary_and_recommendations": {
    "title": "Overall Summary & Recommendations",
    "key_equity_gaps": "...",
    "key_equity_strengths": "...",
    "recommendations": "...",
    "sources": []
  }
}
"""

# These are standard constants
ANALYSIS_QUERY_GENERIC = "Provide an equity analysis of this document, focusing on: {focus_description}"
DELAY_BETWEEN_REQUESTS_SECONDS = 1 # Already set to 1
PERSPECTIVES = [
    {
        "group_name": "Policy Makers",
        "description": "the overall equity implications from the perspective of federal and state policymakers, considering their regulatory responsibilities and influence on equity outcomes. This assessment could indicate how effectively equity measures are embedded in their processes, or if there might be systematic gaps in addressing social or racial disparities.",
        "dimensions": {
            "recognitional": "how the document suggests policy makers acknowledge how historical or systemic exclusion might impact decision-making access for marginalized groups. The analysis might highlight whether unique water justice needs appear to be adequately recognized.",
            "procedural": "how the document examines indications of how agencies manage pollution control and public input, considering whether affected communities appear to meaningfully influence agenda-setting or enforcement priorities.",
            "distributional": "whether the document suggests funding and technical assistance are directed in a way that prioritizes equity impacts, or if there might be unaddressed distributional disparities.",
            "structural": "how the document hints at perpetuating top-down oversight, and whether it could suggest a reallocation of decision-making power or reduction of structural barriers for historically excluded groups."
        }
    },
    {
        "group_name": "Residents",
        "description": "the overall equity implications from the perspective of ordinary residents, especially those in vulnerable communities, regarding their access to clean and affordable water. The assessment might indicate if community voices appear to be sufficiently represented in decisions affecting their health and well-being.",
        "dimensions": {
            "recognitional": "how the document suggests residents experience inequity when their specific circumstances—such as historic under-investment in infrastructure or exposure to legacy industrial sites—appear overlooked or undervalued in funding and policy priorities.",
            "procedural": "how the document examines indications of meaningful resident engagement in public hearings and notice periods, and if marginalized populations might face capacity issues in effective participation.",
            "distributional": "whether the document suggests residents in distressed or rural communities might benefit less from environmental outcomes, or if they appear to pay higher rates for water services due to infrastructure underfunding or costly upgrades.",
            "structural": "how the document hints at systemic obstacles for residents, particularly from minority and low-income groups, such as under-resourced water utilities, lack of representation in regulatory processes, and enduring legacies of exclusion from environmental policymaking."
        }
    },
    {
        "group_name": "Farmers/Business Owners",
        "description": "the overall equity implications from the perspective of farmers and business owners, particularly small operators, considering their roles as regulated entities and community members. The assessment could indicate if compliance costs or infrastructure funding might impose disproportionate economic hardship.",
        "dimensions": {
            "recognitional": "how the document suggests the Act primarily recognizes large industrial and municipal actors, and if distinct rural or small-operator needs might be missed in the broader regulatory structures.",
            "procedural": "how the document assesses whether adequate input opportunities exist for small businesses and farmers through regulatory consultations and permit processes, or if resource constraints, lack of technical assistance, and geographic isolation might impede their meaningful participation.",
            "distributional": "whether the document suggests compliance costs (such as new filtration or runoff systems) might weigh heavier on small agricultural operations and small businesses—sometimes threatening economic viability, especially in distressed regions.",
            "structural": "how the document hints at small operators generally lacking a seat at high-level regulatory tables; financial and information barriers could prevent them from accessing support or defending their interests."
        }
    }
]

# This maps frontend analysis types to backend raw analysis keys for clarity
ANALYSIS_TYPE_DESCRIPTIONS = {
    "general": "the overall equity implications, considering all relevant dimensions of the COEQWAL framework.",
    "vulnerable_groups": "how vulnerable groups are affected or mentioned.",
    "severity_of_impact": "the severity of the document's impacts on equity.",
    "mitigation_strategies": "strategies or solutions for equity concerns."
}


# --- Helper Functions (remain unchanged mostly, adapted for new JSON) ---
def get_pdf_title(file_path: str, default_filename: str) -> str:
    """Extracts title from PDF metadata or returns default filename."""
    if PdfReader is None:
        logger.warning(f"PyPDF2 not installed. Title extraction for '{default_filename}' skipped.")
        return f"Title not extracted (PyPDF2 missing) - {default_filename}"
    try:
        reader = PdfReader(file_path)
        title = reader.metadata.get('/Title', default_filename)
        if not isinstance(title, str):
            title = str(title) if title else default_filename
        return title.strip()
    except Exception as e:
        logger.error(f"Could not read metadata from PDF '{file_path}': {e}")
        return default_filename

def _populate_sources_into_json(structured_data: Dict[str, Any], raw_analyses: Dict[str, Dict[str, Any]]):
    """
    Helper function to inject raw openai_sources into the structured_data JSON.
    Local sources are explicitly excluded.
    This is done purely by Python after the LLM has filled the text fields.
    """
    logger.debug("Populating sources into final JSON structure...")

    # Handle sources for each perspective and each analysis type within it
    for perspective_entry in structured_data.get("overall_analysis_by_perspective", []):
        group_name_slug = perspective_entry["group_name"].replace(" ", "_").lower()
        
        analyses_section = perspective_entry.get("analyses", {})
        
        for analysis_type_key in ["general_equity_assessment", "vulnerable_groups_analysis", "severity_impact_analysis", "mitigation_strategies_analysis"]:
            if analysis_type_key in analyses_section:
                # Map JSON's analysis_type_key to the raw_analyses' focus_type string (e.g., "general_equity_assessment" -> "general")
                raw_analysis_focus_map = {
                    "general_equity_assessment": "general",
                    "vulnerable_groups_analysis": "vulnerable_groups",
                    "severity_impact_analysis": "severity_of_impact",
                    "mitigation_strategies_analysis": "mitigation_strategies"
                }
                raw_focus_type = raw_analysis_focus_map.get(analysis_type_key)
                
                if raw_focus_type:
                    # Construct the key used in raw_analyses (e.g., "perspective_policymakers_general")
                    raw_analysis_lookup_key = f"perspective_{group_name_slug}_{raw_focus_type}"
                else:
                    logger.warning(f"Unknown analysis_type_key '{analysis_type_key}', skipping source mapping.")
                    continue

                if raw_analysis_lookup_key in raw_analyses:
                    raw_openai_sources = raw_analyses[raw_analysis_lookup_key].get("openai_sources", [])
                    combined_sources = []
                    for openai_source_str in raw_openai_sources:
                        combined_sources.append({"type": "openai", "data": openai_source_str})
                    
                    analyses_section[analysis_type_key]["sources"] = combined_sources
                    logger.debug(f"Injected {len(combined_sources)} sources for {group_name_slug}_{analysis_type_key}")
                else:
                    logger.debug(f"Raw analysis key '{raw_analysis_lookup_key}' not found, ensuring empty sources for corresponding section.")
                    analyses_section[analysis_type_key]["sources"] = []

    # Handle overall_summary_and_recommendations sources
    if "overall_summary_and_recommendations" in structured_data:
        overall_summary_raw_key = "overall_summary" # Key used for its raw analysis
        if overall_summary_raw_key in raw_analyses:
            main_openai_sources = []
            for openai_source_str in raw_analyses[overall_summary_raw_key].get("openai_sources", []):
                main_openai_sources.append({"type": "openai", "data": openai_source_str})
            structured_data["overall_summary_and_recommendations"]["sources"] = main_openai_sources
            logger.debug(f"Injected {len(main_openai_sources)} sources for overall_summary_and_recommendations.")
        else:
            structured_data["overall_summary_and_recommendations"]["sources"] = []
            logger.debug("Raw analysis key 'overall_summary' not found, ensuring empty sources for overall_summary_and_recommendations.")
    
    logger.debug("Source population complete.")


def format_analyses_into_json(raw_analyses: Dict[str, Dict[str, Any]], filename: str, title: str,
                              file_size_kb: int, upload_date_utc: str, client: OpenAI,
                              session_id: str, source: str = "user") -> Optional[Dict[str, Any]]:
    """
    Synthesizes raw text analyses into the final structured JSON format.
    Sources are populated by _populate_sources_into_json.
    """
    logger.info("-> Synthesizing raw analyses into the final JSON structure (text portion)...")

    # Check for any failures in raw analysis generation from the `raw_analyses` dict
    if any("ANALYSIS FAILED" in raw_analysis.get("text", "") for raw_analysis in raw_analyses.values()):
        logger.error("Skipping full JSON formatting due to failure in raw analysis generation for one or more sections.")
        error_json = json.loads(JSON_SKELETON)
        error_json["id"] = session_id
        error_json["source"] = source
        error_json["document"]["filename"] = filename
        error_json["document"]["title"] = title
        error_json["document"]["size_kb"] = file_size_kb
        error_json["document"]["upload_date_utc"] = upload_date_utc
        error_json["analysis_status"] = "failed" # Mark as failed due to analysis error
        error_json["analysis_error"] = "One or more raw analyses failed during text generation. See logs for details."
        error_json["overall_analysis_by_perspective"] = [] # Clear nested analyses on failure
        error_json["overall_summary_and_recommendations"]["key_equity_gaps"] = "Due to incomplete raw analysis generation."
        _populate_sources_into_json(error_json, raw_analyses) # Still attempt to populate sources
        return error_json

    # Dynamically build the raw analyses text for the formatter LLM
    raw_analyses_text_str = ""
    for k, v in raw_analyses.items():
        raw_analyses_text_str += f"\n--- RAW ANALYSIS TEXT FOR: {k.replace('_', ' ').upper()} ---\n{v.get('text', 'Not provided.')}\n"
    
    # --- Formatter Prompt (Updated for new JSON structure) ---
    formatter_prompt = textwrap.dedent(f"""
    ## IDENTITY ##
    You are an expert data structurer and equity analyst.

    Your core task is to populate a provided JSON structure based solely on raw, unstructured analysis texts.

    ---

    ## BEHAVIOR ##

    ### A. CONTENT RULES

    1. **Content Sourcing**  
    - All generated content must be derived **only** from the raw analysis texts provided below.
    - Do **not** use external knowledge, assumptions, or hallucinate missing context.

    2. **Indicative Tone**  
    - All summary, narrative, and description fields must use an **indicative, tentative, or suggestive tone**.
    - Avoid definitive or authoritative claims.
    - Use phrases like:
        - “This may indicate...”
        - “It suggests that...”
        - “A potential interpretation is...”
        - “Could be seen as...”
        - “There is an indication that...”
        - “The document appears to...”
        - “Not explicitly indicated by the document.”

    3. **Perspective-Specific Behavior**
    - In `overall_analysis_by_perspective`, one entry exists per stakeholder group (Policy Makers, Residents, Farmers/Business Owners).
        - For each `group_name`, **copy the exact `group_description`** from the JSON skeleton default.
        - Populate all four analyses:
        - `general_equity_assessment`
        - `vulnerable_groups_analysis`
        - `severity_impact_analysis`
        - `mitigation_strategies_analysis`
        - For `general_equity_assessment`, break down the corresponding “general” raw analysis into four subfields:
        - Recognitional
        - Procedural
        - Distributional
        - Structural
        - Treat each `summary` subfield independently. Each one should contain ~200 characters, regardless of other fields. Do not compress or shorten later ones.
        - Treat each `findings` subfield independently. Each one should contain ~150 characters, regardless of other fields. Do not compress or shorten later ones.
        - For the remaining three analyses, fill in all subfields (`summary`, `identified_groups_and_impacts`, etc.) using the relevant raw analysis text.

    4. **Overarching Summary**
    - Populate the `overall_summary_and_recommendations` section with any cross-cutting or overarching insights derived from the raw texts.
    - Maintain the same tentative tone.

    ---

    ### B. FORMATTING & STRUCTURE RULES

    5. **Placeholder Replacement**
    - Replace every `"..."` placeholder with fully formed, appropriate content.
    - Preserve all structural elements of the original JSON schema.

    6. **Numeric Placeholders**
    - Any field containing a number (e.g., `"40"`, `"120"`) should be replaced with text of **approximately that many characters**.
    - These are soft targets, not strict limits.

    7. **Schema Adherence**
    - Do **not** alter the schema structure in any way.
    - Do **not** include citations, URLs, or references in any content field.
    - Do **not** modify the `sources` arrays — they will be handled separately by Python.

    8. **Top-Level Metadata Fields**
    - Leave the fields `id`, `source`, and `document` as `"..."`.

    9. **Test Fields Completion**
    - Populate the `test_fields` object with careful attention:
        - You should populate "test_pic" one of the following strings "head-image.png", "head-image-2.png", or "head-image-3.png" depending on the main subject of the document being 
        - You should populate "test_subject" with the main subject of the document, e.g. "Managing Potable Tap Water", "Federal Water Pollution Control", etc.
        - You should populate "test_title" with the actual title of the document e.g. "The Clean Water Act". Or if the title is not available, create a title based on the document's content. 
        - You should populate "test_short_caption" with a short caption for the analysis' findings like "In 50 Years: Progress and Persistent Challenges" or "An Equity-Focused Review of Your Document"
        - You should populate "test_long_caption" with a slightly longer caption for the analysiis that provides more context e.g. "An equity analysis of America's landmark environmental legislation and its impact on communities across the nation"
        - You should populate "test_date" with the date the document was enacted or published, if available e.g. "Enacted: 1972" or "Published: 2020". If not available, leave the field completely blank.
        - You should populate "test_scope" with either the strings "federal", "state", "agency", or "other" based on the document's scope. 
    ---

    ## INPUTS ##
    **JSON SKELETON TO POPULATE (Text fields only, leaving 'id', 'source', 'document' as '...'):**  
    {JSON_SKELETON}

    **RAW TEXT ANALYSES TO USE:**  
    {raw_analyses_text_str}
    """)

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": formatter_prompt}
            ],
            response_format={"type": "json_object"}
        )
        json_output_str = response.choices[0].message.content
        structured_data = json.loads(json_output_str)

        # Assign document metadata and top-level fields (Python-controlled)
        structured_data["id"] = session_id
        structured_data["source"] = source
        structured_data["document"]["filename"] = filename
        structured_data["document"]["title"] = title
        structured_data["document"]["size_kb"] = file_size_kb
        structured_data["document"]["upload_date_utc"] = upload_date_utc
        structured_data["analysis_status"] = "completed" # Set top-level status for consistency with DB/list
        structured_data["analysis_error"] = None


        _populate_sources_into_json(structured_data, raw_analyses) # Populate sources

        logger.info("-> Successfully synthesized analyses into JSON structure and populated sources.")
        return structured_data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from OpenAI response during formatting: {e}. Response was: {json_output_str[:500]}...", exc_info=True)
        # Attempt to return a partial JSON indicating formatting failure and populate sources
        error_json = json.loads(JSON_SKELETON)
        error_json["id"] = session_id
        error_json["source"] = source
        error_json["document"]["filename"] = filename
        error_json["document"]["title"] = title
        error_json["document"]["size_kb"] = file_size_kb
        error_json["document"]["upload_date_utc"] = upload_date_utc
        error_json["analysis_status"] = "failed" # Mark as failed due to JSON error
        error_json["analysis_error"] = f"JSON formatting failed: {e}. Raw analyses might be incomplete or malformed."
        error_json["overall_analysis_by_perspective"] = [] # Clear main content if format fails
        error_json["overall_summary_and_recommendations"]["key_equity_gaps"] = "Due to incomplete raw analysis generation."
        _populate_sources_into_json(error_json, raw_analyses)
        return error_json
    except Exception as e:
        logger.error(f"Failed to format analyses into JSON for unknown reason: {e}", exc_info=True)
        error_json = json.loads(JSON_SKELETON)
        error_json["id"] = session_id
        error_json["source"] = source
        error_json["document"]["filename"] = filename
        error_json["document"]["title"] = title
        error_json["document"]["size_kb"] = file_size_kb
        error_json["document"]["upload_date_utc"] = upload_date_utc
        error_json["analysis_status"] = "failed" # Mark as failed due to unexpected error
        error_json["analysis_error"] = f"An unexpected error occurred during final JSON synthesis: {e}"
        error_json["overall_analysis_by_perspective"] = [] # Clear main content on failure
        error_json["overall_summary_and_recommendations"]["key_equity_gaps"] = "Due to unexpected error during JSON formatting."
        _populate_sources_into_json(error_json, raw_analyses)
        return error_json

# --- Main analysis function ---
async def perform_equity_analysis(
    session_id: str, # This is the document_id for user uploads
    original_filename: str,
    title: str,
    file_size_kb: int,
    upload_date_utc: str,
    rag_system_instance: HybridRAGSystem,
    openai_interface_instance: OpenAIInteraction,
    analysis_output_dir: str,
):
    logger.info(f"Background task: Starting analysis for session: {session_id}, file: {original_filename}")
    
    db_conn = None
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Initial update of analysis_status to 'in_progress' in DB
        cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('in_progress', None, session_id))
        db_conn.commit()
    except sqlite3.Error as e:
        logger.error(f"DB error setting status to 'in_progress' for {session_id} at task start: {e}", exc_info=True)
        temp_db_conn = None
        try:
            temp_db_conn = get_db_connection()
            temp_cursor = temp_db_conn.cursor()
            temp_cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('failed', f"Task start DB Error: {e}", session_id))
            temp_db_conn.commit()
        except Exception as update_e:
            logger.error(f"Failed fallback DB update for {session_id}: {update_e}", exc_info=True)
        finally:
            if temp_db_conn: close_db_connection(temp_db_conn)
        return

    # --- OpenAI VS Processing Wait ---
    vector_store_id = None
    openai_file_id = None
    try:
        cursor.execute("SELECT openai_vector_store_id, openai_file_id FROM openai_resources WHERE document_id = ?", (session_id,))
        vs_file_ids_row = cursor.fetchone()
        if vs_file_ids_row:
            vector_store_id, openai_file_id = vs_file_ids_row
        else:
            raise ValueError(f"OpenAI Vector Store or File ID not found in DB for session {session_id}.")
        
        logger.info(f"[{session_id}] Waiting for OpenAI Vector Store file processing to complete (VS ID: {vector_store_id}, File ID: {openai_file_id})...")
        
        # Update status to 'waiting_vs_processing' while waiting for OpenAI
        cursor.execute("UPDATE documents SET analysis_status = ? WHERE document_id = ?", ('waiting_vs_processing', session_id))
        db_conn.commit()

        processing_success = openai_interface_instance.wait_for_vector_store_file_processing(
            vector_store_id=vector_store_id,
            file_id=openai_file_id,
            timeout=settings.PROCESSING_TIMEOUT_SECONDS,
            poll_interval=settings.POLLING_INTERVAL_SECONDS
        )
        
        if not processing_success:
            raise Exception(f"OpenAI Vector Store file processing failed or timed out for session {session_id}.")

        logger.info(f"[{session_id}] OpenAI Vector Store file processing completed.")

        cursor.execute("UPDATE documents SET analysis_status = ? WHERE document_id = ?", ('completed', session_id)) # <--- Set to 'completed' after VS processing
        db_conn.commit()
        logger.info(f"[{session_id}] Document status set to 'completed' in DB (RAG ready).")

    except sqlite3.Error as e: # Catch DB errors during VS processing wait
        logger.error(f"Database error during VS processing wait for {session_id}: {e}", exc_info=True)
        cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('failed', f"DB Error during VS wait: {e}", session_id))
        db_conn.commit()
        return # Exit task on DB error
    except Exception as e: # Catch OpenAI VS processing errors
        logger.error(f"OpenAI VS processing error for session {session_id}: {e}", exc_info=True)
        cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('failed', f"VS Processing Error: {e}", session_id))
        db_conn.commit()
        return


    # --- Analysis Generation ---
    try:
        session_output_dir = os.path.join(analysis_output_dir, session_id)
        os.makedirs(session_output_dir, exist_ok=True)
        output_file_path = os.path.join(session_output_dir, "analysis_result.json")

        if settings.SIMULATE_ANALYSIS:
            # ... (simulation logic, existing code here is fine) ...
            logger.info(f"[{session_id}] Running analysis in SIMULATION MODE.")
            await asyncio.sleep(2) 
            
            dummy_json_result = json.loads(JSON_SKELETON)
            dummy_json_result["id"] = session_id
            dummy_json_result["source"] = "user"
            dummy_json_result["document"]["filename"] = original_filename
            dummy_json_result["document"]["title"] = title or "Simulated Document Title"
            dummy_json_result["document"]["size_kb"] = file_size_kb
            dummy_json_result["document"]["upload_date_utc"] = upload_date_utc
            
            dummy_json_result["overall_analysis_by_perspective"] = [] 
            for perspective_info in PERSPECTIVES:
                perspective_entry = {
                    "group_name": perspective_info["group_name"],
                    "group_description": perspective_info["description"],
                    "analyses": {}
                }
                dummy_json_result["overall_analysis_by_perspective"].append(perspective_entry)

                for analysis_type in ANALYSIS_TYPE_DESCRIPTIONS.keys():
                    analysis_key = "general_equity_assessment" if analysis_type == "general" else f"{analysis_type}_analysis"
                    
                    if analysis_type == "general":
                        perspective_entry["analyses"][analysis_key] = {
                            "title": f"General Equity Assessment for {perspective_info['group_name']} (Simulated)",
                            "summary": f"This is a simulated general equity assessment for {perspective_info['group_name']}.",
                            "recognitional_equity": { "title": "Recognitional Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "procedural_equity": { "title": "Procedural Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "distributional_equity": { "title": "Distributional Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "structural_equity": { "title": "Structural Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "sources": [{"type": "openai", "data": f"Simulated Source for {perspective_info['group_name']} General."}]
                        }
                    else:
                        perspective_entry["analyses"][analysis_key] = {
                            "title": f"{analysis_type.replace('_', ' ').title()} Analysis for {perspective_info['group_name']} (Simulated)",
                            "summary": f"Simulated summary for {analysis_type} from {perspective_info['group_name']}'s perspective.",
                            "identified_groups_and_impacts": "Simulated groups.",
                            "high_severity_impacts": "Simulated high impacts.",
                            "identified_strategies": "Simulated strategies.",
                            "equity_assessment": "Simulated equity assessment.",
                            "conclusion": "Simulated conclusion.",
                            "sources": [{"type": "openai", "data": f"Simulated Source for {perspective_info['group_name']} {analysis_type}."}]
                        }
            
            dummy_json_result["overall_summary_and_recommendations"] = {
                "title": "Overall Summary & Recommendations (Simulated)",
                "key_equity_gaps": "Simulated key equity gaps.",
                "key_equity_strengths": "Simulated key equity strengths.",
                "recommendations": "Simulated recommendations.",
                "sources": [{"type": "openai", "data": "Simulated Overall Summary Source."}]
            }

            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(dummy_json_result, f, indent=2, ensure_ascii=False)
            logger.info(f"[{session_id}] Simulated analysis saved to file: {output_file_path}")

            # Final DB update: confirm 'completed' and set file path
            cursor.execute("UPDATE documents SET analysis_status = ?, analysis_json_filepath = ?, analysis_error = ? WHERE document_id = ?",
                           ('completed', output_file_path, None, session_id))
            db_conn.commit()
            logger.info(f"[{session_id}] Simulated analysis completed and DB info updated.")

        else: # --- REAL ANALYSIS LOGIC ---
            logger.info(f"[{session_id}] Running analysis in REAL MODE.")
            raw_analyses: Dict[str, Dict[str, Any]] = {}
            
            for perspective_info in PERSPECTIVES:
                perspective_group_key = perspective_info["group_name"].replace(" ", "_").lower()
                raw_analyses[perspective_group_key] = {}
                logger.info(f"[{session_id}] -> Generating analyses for perspective: '{perspective_info['group_name']}'...")

                for focus_type, focus_description_suffix in ANALYSIS_TYPE_DESCRIPTIONS.items():
                    query_focus = perspective_info['description'] if focus_type == "general" else f"Regarding {perspective_info['group_name']}'s perspective, {focus_description_suffix}"
                    full_query_for_rag_system = ANALYSIS_QUERY_GENERIC.format(focus_description=query_focus)
                    raw_analysis_key_for_rag_system = f"perspective_{perspective_group_key}_{focus_type}"
                    logger.info(f"[{session_id}]    -> Querying for '{perspective_info['group_name']}' - '{focus_type}' analysis...")
                    
                    # Pass db_conn to rag_system_instance.answer_question
                    answer, _, openai_srcs = rag_system_instance.answer_question(
                        session_id=session_id, # document_id for rag_system
                        query=full_query_for_rag_system,
                        focus_area=focus_type,
                        custom_instructions=None,
                        db_conn=db_conn
                    )
                    
                    if "Error:" in answer:
                        logger.error(f"[{session_id}] Received an error for '{perspective_info['group_name']}' - '{focus_type}': {answer}. Marking as failed.")
                        raw_analyses[raw_analysis_key_for_rag_system] = {"text": f"ANALYSIS FAILED: {answer}", "openai_sources": openai_srcs}
                    else:
                        raw_analyses[raw_analysis_key_for_rag_system] = {"text": answer, "openai_sources": openai_srcs}
                    
                    logger.info(f"[{session_id}]    Generated raw analysis for '{perspective_info['group_name']}' - '{focus_type}'. Waiting {DELAY_BETWEEN_REQUESTS_SECONDS}s...")
                    time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

            # --- Generate an overall summary analysis ---
            overall_summary_query = "Provide an overall summary of the document's equity implications and recommendations, synthesizing findings across all perspectives previously considered."
            logger.info(f"[{session_id}] -> Generating overall summary analysis...")
            overall_answer, _, overall_openai_srcs = rag_system_instance.answer_question(
                session_id=session_id,
                query=overall_summary_query,
                focus_area="general",
                db_conn=db_conn # PASS db_conn
            )
            raw_analyses["overall_summary"] = {"text": overall_answer, "openai_sources": overall_openai_srcs}
            logger.info(f"[{session_id}] Generated overall summary.")
            time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

            # --- Synthesize all raw analyses text into final JSON structure ---
            final_json_result = format_analyses_into_json(
                raw_analyses, original_filename, title, file_size_kb, upload_date_utc,
                openai_interface_instance.client,
                session_id=session_id,
                source="user"
            )
            if not final_json_result:
                raise Exception("Failed to synthesize the final JSON structure from raw analyses.")

            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(final_json_result, f, indent=2, ensure_ascii=False)
            logger.info(f"[{session_id}] Analysis saved to file: {output_file_path}")

            # Final DB update: confirm 'completed' and set file path
            cursor.execute("UPDATE documents SET analysis_status = ?, analysis_json_filepath = ?, analysis_error = ? WHERE document_id = ?",
                           ('completed', output_file_path, None, session_id)) # <--- ENSURE 'completed' here too
            db_conn.commit()
            logger.info(f"[{session_id}] Analysis completed and DB info updated.")

    except sqlite3.Error as e:
        logger.error(f"Database error during JSON generation/save for {session_id}: {e}", exc_info=True)
        if db_conn: db_conn.rollback() # Rollback any partial transaction
        # Fallback DB update to 'failed' on DB error
        temp_db_conn = None
        try:
            temp_db_conn = get_db_connection()
            temp_cursor = temp_db_conn.cursor()
            temp_cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('failed', f"DB Error during analysis: {e}", session_id))
            temp_db_conn.commit()
        except Exception as update_e:
            logger.error(f"Failed to update DB status to 'failed' (secondary attempt) for {session_id}: {update_e}", exc_info=True)
        finally:
            if temp_db_conn: close_db_connection(temp_db_conn)
        
    except Exception as e: # Catch general analysis generation errors
        logger.error(f"Critical error during background REAL analysis for session {session_id}: {e}", exc_info=True)
        # Fallback DB update to 'failed' on general error
        temp_db_conn = None
        try:
            temp_db_conn = get_db_connection()
            temp_cursor = temp_db_conn.cursor()
            temp_cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('failed', f"Analysis Runtime Error: {e}", session_id))
            temp_db_conn.commit()
        except Exception as update_e:
            logger.error(f"Failed to update DB status to 'failed' (secondary attempt) for {session_id}: {update_e}", exc_info=True)
        finally:
            if temp_db_conn: close_db_connection(temp_db_conn)
    finally:
        if db_conn: # Ensure db_conn is closed if obtained within this function
            close_db_connection(db_conn)