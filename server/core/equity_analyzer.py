# core/equity_analyzer.py

import os
import json
import logging
import shutil
import tempfile
import textwrap
import time
import asyncio

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

logger = logging.getLogger("equity_analyzer")

# --- Constants and JSON Skeleton (remain unchanged) ---
# Define ANALYSES_DIR relative to equity_analyzer.py
CURRENT_DIR = os.path.dirname(__file__)
ANALYSES_DIR = os.path.join(CURRENT_DIR, "..", "policy_analyses") # <--- ADD THIS
os.makedirs(ANALYSES_DIR, exist_ok=True) # Ensure it exists

FOCUS_AREAS = ["general", "vulnerable_groups", "severity_of_impact", "mitigation_strategies"]
ANALYSIS_QUERY_GENERIC = "Provide an equity analysis of this document, focusing on: {focus_description}"
DELAY_BETWEEN_REQUESTS_SECONDS = 1
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
  "overall_analysis_by_perspective": [
    {
      "group_name": "Policy Makers",
      "group_description": "the overall equity implications from the perspective of federal and state policymakers, considering their regulatory responsibilities and influence on equity outcomes. This assessment could indicate how effectively equity measures are embedded in their processes, or if there might be systematic gaps in addressing social or racial disparities.",
      "analyses": {
        "general_equity_assessment": {
          "title": "General Equity Assessment for Policy Makers",
          "summary": "...",
          "recognitional_equity": { "title": "Recognitional Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "procedural_equity": { "title": "Procedural Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "distributional_equity": { "title": "Distributional Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "structural_equity": { "title": "Structural Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
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
          "summary": "...",
          "recognitional_equity": { "title": "Recognitional Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "procedural_equity": { "title": "Procedural Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "distributional_equity": { "title": "Distributional Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "structural_equity": { "title": "Structural Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
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
          "summary": "...",
          "recognitional_equity": { "title": "Recognitional Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "procedural_equity": { "title": "Procedural Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "distributional_equity": { "title": "Distributional Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
          "structural_equity": { "title": "Structural Equity", "positive_findings": "...", "concerns": "...", "conclusion": "..." },
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

# --- Helper Functions (remain unchanged) ---
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
    Local sources are explicitly excluded as per new requirement.
    This is done purely by Python after the LLM has filled the text fields.
    """
    logger.debug("Populating sources into final JSON structure...")

    # Handle sources for each perspective and each analysis type within it
    for perspective_entry in structured_data.get("overall_analysis_by_perspective", []):
        group_name_slug = perspective_entry["group_name"].replace(" ", "_").lower()
        
        # Iterate through each analysis type within this perspective
        analyses_section = perspective_entry.get("analyses", {})
        
        for analysis_type_key in ["general_equity_assessment", "vulnerable_groups_analysis", "severity_impact_analysis", "mitigation_strategies_analysis"]:
            if analysis_type_key in analyses_section:
                raw_analysis_key_map = {
                    "general_equity_assessment": "general",
                    "vulnerable_groups_analysis": "vulnerable_groups",
                    "severity_impact_analysis": "severity_of_impact",
                    "mitigation_strategies_analysis": "mitigation_strategies"
                }
                # Example raw_analysis_key: "perspective_policymakers_general" or "perspective_residents_vulnerable_groups"
                raw_key_suffix = raw_analysis_key_map.get(analysis_type_key)
                if raw_key_suffix:
                    raw_analysis_lookup_key = f"perspective_{group_name_slug}_{raw_key_suffix}"
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
                    logger.debug(f"Raw analysis key '{raw_analysis_lookup_key}' not found, skipping source injection for corresponding section.")
                    # Ensure sources array exists even if empty
                    analyses_section[analysis_type_key]["sources"] = []

    if "overall_summary_and_recommendations" in structured_data:
        overall_summary_raw_key = "overall_summary" # Define a key if you add a top-level summary analysis
        if overall_summary_raw_key in raw_analyses:
            main_openai_sources = []
            for openai_source_str in raw_analyses[overall_summary_raw_key].get("openai_sources", []):
                main_openai_sources.append({"type": "openai", "data": openai_source_str})
            structured_data["overall_summary_and_recommendations"]["sources"] = main_openai_sources
        else:
            structured_data["overall_summary_and_recommendations"]["sources"] = []
    
    logger.debug("Source population complete.")

def format_analyses_into_json(raw_analyses: Dict[str, Dict[str, Any]], filename: str, title: str,
                              file_size_kb: int, upload_date_utc: str, client: OpenAI,
                              session_id: str, source: str = "user") -> Optional[Dict[str, Any]]:
    """
    Synthesizes raw text analyses into the final structured JSON format.
    Sources are inserted *after* LLM generation, purely by Python.
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
        # Set a generic error message
        error_json["overall_analysis_by_perspective"] = [] # Clear nested analyses on failure
        error_json["overall_summary_and_recommendations"]["key_equity_gaps"] = "Due to incomplete raw analysis generation."
        _populate_sources_into_json(error_json, raw_analyses) # Still attempt to populate sources
        return error_json

    # Dynamically build the raw analyses text for the formatter LLM
    # This will be a more complex string now, including perspective and analysis type.
    raw_analyses_text_str = ""
    for k, v in raw_analyses.items():
        raw_analyses_text_str += f"\n--- RAW ANALYSIS TEXT FOR: {k.replace('_', ' ').upper()} ---\n{v.get('text', 'Not provided.')}\n"
    
    # --- NEW FORMATTER PROMPT ---
    # This prompt needs to guide the LLM to fill the new nested structure.
    # It must map raw_analyses_text_str content into the correct paths.
    formatter_prompt = textwrap.dedent(f"""
    You are an expert data structurer and equity analyst. Your task is to populate the provided JSON structure.
    All generated content in the JSON must be derived **ONLY** from the raw analysis texts provided below.
    Crucially, all summary, narrative, and description fields must use an **indicative, tentative, or suggestive tone**.
    Avoid definitive or authoritative statements. Employ phrases like "This may indicate...", "It suggests that...",
    "A potential interpretation is...", "It appears to...", "Could be seen as...", "There is an indication that...",
    "The document seems to...", "It might imply...", etc.
    If the provided raw analysis text does not contain information for a specific field in the JSON, use phrases like "Not explicitly indicated by the document." or "The document does not appear to provide details on this aspect."

    **Instructions:**
    1.  Carefully read all provided raw text analyses. Each raw analysis is clearly labeled (e.g., "RAW ANALYSIS TEXT FOR: PERSPECTIVE_POLICY_MAKERS_GENERAL").
    2.  Fill in every "..." placeholder in the JSON skeleton with **detailed and comprehensive** information synthesized from these analysis texts. Do not over-summarize; preserve key details and nuanced interpretations.
    3.  Ensure all content strictly adheres to the schema and the required indicative tone.
    4.  **DO NOT ADD ANY SOURCE INFORMATION OR CITATIONS TO THE TEXT FIELDS OR THE 'sources' ARRAYS.** The 'sources' arrays in the JSON skeleton will be populated separately by Python.
    5.  For the `overall_analysis_by_perspective` array, there will be one entry for each stakeholder group (Policy Makers, Residents, Farmers/Business Owners).
        *   For each `group_name`, ensure the `group_description` is precisely copied from the provided JSON_SKELETON's default value for that group.
        *   Within each perspective's `analyses` object, fill in the four types of analysis: `general_equity_assessment`, `vulnerable_groups_analysis`, `severity_impact_analysis`, and `mitigation_strategies_analysis`.
        *   **For `general_equity_assessment` within each perspective:** Break down the corresponding "general" raw analysis into the sub-fields for each of the four equity dimensions (Recognitional, Procedural, Distributional, Structural). Aim to identify both "positive_findings" and "concerns" if discernible, and provide a "conclusion".
        *   **For other analysis types (vulnerable groups, severity, mitigation) within each perspective:** Fill their respective `summary`, `identified_groups_and_impacts`, `high_severity_impacts`, `identified_strategies`, etc., fields using the relevant raw analysis text.
    6.  Ensure the `overall_summary_and_recommendations` section is populated using any relevant overarching themes or conclusions found in the raw analyses.
    7.  The `id`, `source`, and `document` fields at the top-level of the JSON will be populated by Python, leave them as `...` in your output.
    8.  Ensure the output is a single, valid JSON object and nothing else.

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
            # temperature=0.2 # Keep temperature low for structured output
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
        # Also ensure top-level analysis_status for consistency with /api/policies list
        structured_data["analysis_status"] = "completed" # Mark as completed here
        structured_data["analysis_error"] = None


        # --- Python Logic to Inject Raw Sources (POST-LLM) ---
        _populate_sources_into_json(structured_data, raw_analyses)

        logger.info("-> Successfully synthesized analyses into JSON structure and injected raw sources.")
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
        # Clear main analysis content on failure to avoid malformed output
        error_json["overall_analysis_by_perspective"] = []
        error_json["overall_summary_and_recommendations"]["key_equity_gaps"] = "Due to JSON formatting failure."
        _populate_sources_into_json(error_json, raw_analyses) # Still try to populate sources on error
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
        # Clear main analysis content on failure
        error_json["overall_analysis_by_perspective"] = []
        error_json["overall_summary_and_recommendations"]["key_equity_gaps"] = "Due to unexpected error during JSON formatting."
        _populate_sources_into_json(error_json, raw_analyses) # Still try to populate sources on error
        return error_json

ANALYSIS_TYPE_DESCRIPTIONS = {
    "general": "the overall equity implications, considering all relevant dimensions of the COEQWAL framework.",
    "vulnerable_groups": "how vulnerable groups are affected or mentioned.",
    "severity_of_impact": "the severity of the document's impacts on equity.",
    "mitigation_strategies": "strategies or solutions for equity concerns."
}

async def perform_equity_analysis(
    session_id: str,
    original_filename: str,
    title: str,
    file_size_kb: int,
    upload_date_utc: str,
    rag_system_instance: HybridRAGSystem,
    openai_interface_instance: OpenAIInteraction,
    user_sessions_dict: Dict[str, Dict[str, Any]],
    analysis_output_dir: str # This will be ANALYSES_DIR from main.py
):
    """
    Performs the full equity analysis for a single document as a background task.
    Updates session status and saves results to file and in-memory dict.
    """
    logger.info(f"Background task: Starting analysis for session: {session_id}, file: {original_filename}")
    
    session_info = user_sessions_dict.get(session_id)
    if not session_info:
        logger.error(f"Session {session_id} not found in user_sessions_dict during background analysis start.")
        return

    session_info['analysis_status'] = 'in_progress'
    session_info['analysis_result_cached'] = None
    session_info['analysis_result_path'] = None
    session_info['analysis_error'] = None

    try:
        # --- NEW STEP: WAIT FOR OPENAI VECTOR STORE PROCESSING TO COMPLETE ---
        # (NO CHANGE HERE - existing logic)
        vector_store_id = session_info.get("vector_store_id")
        openai_file_id = session_info.get("file_id")

        if not vector_store_id or not openai_file_id:
            raise ValueError(f"Vector Store ID or File ID missing for session {session_id}. Cannot proceed with analysis.")
        
        logger.info(f"[{session_id}] Waiting for OpenAI Vector Store file processing to complete...")
        session_info['analysis_status'] = 'waiting_vs_processing' # More granular status for frontend
        
        processing_success = openai_interface_instance.wait_for_vector_store_file_processing(
            vector_store_id=vector_store_id,
            file_id=openai_file_id,
            timeout=settings.PROCESSING_TIMEOUT_SECONDS, # Use configured timeout
            poll_interval=settings.POLLING_INTERVAL_SECONDS # Use configured interval
        )
        
        if not processing_success:
            raise Exception(f"OpenAI Vector Store file processing failed or timed out for session {session_id}.")

        logger.info(f"[{session_id}] OpenAI Vector Store file processing completed.")
        session_info['analysis_status'] = 'analysis_generating' # Status while LLM calls are made

        # --- SIMULATION TOGGLE ---
        if settings.SIMULATE_ANALYSIS:
            logger.info(f"[{session_id}] Running analysis in SIMULATION MODE (no OpenAI calls).")
            await asyncio.sleep(2) 
            
            # --- UPDATED DUMMY JSON RESULT FOR SIMULATION ---
            dummy_json_result = json.loads(JSON_SKELETON) # Load skeleton
            dummy_json_result["id"] = session_id
            dummy_json_result["source"] = "user"
            dummy_json_result["document"]["filename"] = original_filename
            dummy_json_result["document"]["title"] = title or "Simulated Document Title"
            dummy_json_result["document"]["size_kb"] = file_size_kb
            dummy_json_result["document"]["upload_date_utc"] = upload_date_utc
            dummy_json_result["analysis_status"] = "completed" # Set top-level status for list
            dummy_json_result["analysis_error"] = None


            # Populate dummy data for each perspective and analysis type
            for p_idx, perspective_info in enumerate(PERSPECTIVES):
                # Ensure the perspective entry exists in the skeleton (if it's not already pre-populated)
                if p_idx < len(dummy_json_result["overall_analysis_by_perspective"]):
                    perspective_entry = dummy_json_result["overall_analysis_by_perspective"][p_idx]
                else: # Add if skeleton didn't have enough entries
                    perspective_entry = {
                        "group_name": perspective_info["group_name"],
                        "group_description": perspective_info["description"],
                        "analyses": {}
                    }
                    dummy_json_result["overall_analysis_by_perspective"].append(perspective_entry)

                perspective_entry["group_name"] = perspective_info["group_name"]
                perspective_entry["group_description"] = perspective_info["description"]
                
                for analysis_type in ANALYSIS_TYPE_DESCRIPTIONS.keys():
                    if analysis_type == "general": # Special handling for general equity assessment
                        perspective_entry["analyses"]["general_equity_assessment"] = {
                            "title": f"General Equity Assessment for {perspective_info['group_name']} (Simulated)",
                            "summary": f"This is a simulated general equity assessment for {perspective_info['group_name']}. The document appears to provide some insights.",
                            "recognitional_equity": { "title": "Recognitional Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "procedural_equity": { "title": "Procedural Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "distributional_equity": { "title": "Distributional Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "structural_equity": { "title": "Structural Equity", "positive_findings": "Simulated positive findings.", "concerns": "Simulated concerns.", "conclusion": "Simulated conclusion." },
                            "sources": [{"type": "openai", "data": f"Simulated Source from Doc for {perspective_info['group_name']} General."}]
                        }
                    else: # Other analysis types
                        perspective_entry["analyses"][f"{analysis_type}_analysis"] = {
                            "title": f"{analysis_type.replace('_', ' ').title()} Analysis for {perspective_info['group_name']} (Simulated)",
                            "summary": f"This is a simulated summary for {analysis_type} from {perspective_info['group_name']}'s perspective.",
                            "identified_groups_and_impacts": "Simulated identified groups and impacts.",
                            "high_severity_impacts": "Simulated high severity impacts.",
                            "identified_strategies": "Simulated identified strategies.",
                            "equity_assessment": "Simulated equity assessment.",
                            "conclusion": "Simulated conclusion.",
                            "sources": [{"type": "openai", "data": f"Simulated Source from Doc for {perspective_info['group_name']} {analysis_type}."}]
                        }
            
            # Populate overall_summary_and_recommendations
            dummy_json_result["overall_summary_and_recommendations"] = {
                "title": "Overall Summary & Recommendations (Simulated)",
                "key_equity_gaps": "Simulated key equity gaps across all perspectives.",
                "key_equity_strengths": "Simulated key equity strengths across all perspectives.",
                "recommendations": "Simulated recommendations for future actions.",
                "sources": [{"type": "openai", "data": "Simulated Overall Summary Source."}]
            }

            # Save to file
            output_file_path = os.path.join(analysis_output_dir, f"{session_id}.json")
            os.makedirs(analysis_output_dir, exist_ok=True)
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(dummy_json_result, f, indent=2, ensure_ascii=False)
            logger.info(f"[{session_id}] Simulated analysis saved to file: {output_file_path}")

            # Update in-memory dict
            session_info['analysis_status'] = 'completed'
            session_info['analysis_result_path'] = output_file_path
            session_info['analysis_result_cached'] = dummy_json_result
            logger.info(f"[{session_id}] Simulated analysis completed and session info updated.")

        else: # --- REAL ANALYSIS LOGIC ---
            logger.info(f"[{session_id}] Running analysis in REAL MODE (making OpenAI calls).")
            # raw_analyses will now be structured as {perspective_slug: {analysis_type_slug: {text: ..., sources: ...}}}
            raw_analyses: Dict[str, Dict[str, Any]] = {} 
            final_json_result: Optional[Dict[str, Any]] = None
            
            # --- Generate analyses for each PERSPECTIVE and each ANALYSIS TYPE within it ---
            for perspective_info in PERSPECTIVES:
                perspective_group_key = perspective_info["group_name"].replace(" ", "_").lower()
                raw_analyses[perspective_group_key] = {} # Initialize inner dict for this perspective
                logger.info(f"[{session_id}] -> Generating analyses for perspective: '{perspective_info['group_name']}'...")

                for focus_type, focus_description_suffix in ANALYSIS_TYPE_DESCRIPTIONS.items():
                    # Construct query specific to perspective and analysis type
                    # For general, use the group description. For others, use specific analysis type description.
                    
                    if focus_type == "general":
                        query_focus = perspective_info['description'] # Use perspective's general description
                    else:
                        query_focus = f"Regarding {perspective_info['group_name']}'s perspective, {focus_description_suffix}"
                    
                    full_query_for_rag_system = ANALYSIS_QUERY_GENERIC.format(focus_description=query_focus)
                    
                    # Store raw analysis by perspective_key and focus_type
                    raw_analysis_key_for_rag_system = f"perspective_{perspective_group_key}_{focus_type}"
                    
                    logger.info(f"[{session_id}]    -> Querying for '{perspective_info['group_name']}' - '{focus_type}' analysis...")
                    
                    answer, _, openai_srcs = rag_system_instance.answer_question(
                        session_id=session_id,
                        query=full_query_for_rag_system,
                        focus_area=focus_type # Pass original focus_type for prompt selection
                    )
                    
                    if "Error:" in answer:
                        logger.error(f"[{session_id}] Received an error for '{perspective_info['group_name']}' - '{focus_type}': {answer}. Marking as failed.")
                        raw_analyses[raw_analysis_key_for_rag_system] = {"text": f"ANALYSIS FAILED: {answer}", "openai_sources": openai_srcs}
                    else:
                        raw_analyses[raw_analysis_key_for_rag_system] = {"text": answer, "openai_sources": openai_srcs}
                    
                    logger.info(f"[{session_id}]    Generated raw analysis for '{perspective_info['group_name']}' - '{focus_type}'. Waiting {DELAY_BETWEEN_REQUESTS_SECONDS}s...")
                    time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

            # --- Generate an overall summary analysis if needed (optional, for overall_summary_and_recommendations) ---
            # You might want a dedicated query here not tied to a specific perspective for the "overall_summary" section.
            # Example:
            overall_summary_query = "Provide an overall summary of the document's equity implications and recommendations, synthesizing findings across all perspectives previously considered."
            logger.info(f"[{session_id}] -> Generating overall summary analysis...")
            overall_answer, _, overall_openai_srcs = rag_system_instance.answer_question(
                session_id=session_id,
                query=overall_summary_query,
                focus_area="general" # Use general focus for overall summary
            )
            raw_analyses["overall_summary"] = {"text": overall_answer, "openai_sources": overall_openai_srcs}
            logger.info(f"[{session_id}] Generated overall summary.")
            time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS) # Add a small delay

            # --- Synthesize all raw analyses text into final JSON structure (Python injects sources after) ---
            final_json_result = format_analyses_into_json(
                raw_analyses, original_filename, title, file_size_kb, upload_date_utc,
                openai_interface_instance.client,
                session_id=session_id,
                source="user"
            )
            if not final_json_result:
                raise Exception("Failed to synthesize the final JSON structure from raw analyses.")

            # --- Save result to file and update in-memory dict ---
            # (NO CHANGE - uses analysis_output_dir passed from main.py)
            output_file_path = os.path.join(analysis_output_dir, f"{session_id}.json")
            os.makedirs(analysis_output_dir, exist_ok=True)
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(final_json_result, f, indent=2, ensure_ascii=False)
            logger.info(f"[{session_id}] Analysis saved to file: {output_file_path}")

            # Update in-memory dict
            session_info['analysis_status'] = 'completed'
            session_info['analysis_result_path'] = output_file_path
            session_info['analysis_result_cached'] = final_json_result
            logger.info(f"[{session_id}] Analysis completed and session info updated.")

    except Exception as e:
        logger.error(f"[{session_id}] Critical error during background REAL analysis: {e}", exc_info=True)
        session_info['analysis_status'] = 'failed'
        session_info['analysis_error'] = str(e)
    finally:
        pass