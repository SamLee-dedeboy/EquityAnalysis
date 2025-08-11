# main.py
import os
import uuid
import logging
import secrets
import json
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, status, Cookie, BackgroundTasks, Response
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware # Optional: If frontend served differently
from pydantic import BaseModel # Ensure BaseModel is imported

from core.config import settings
from core.openai_interaction import OpenAIInteraction
from core.rag_system import HybridRAGSystem
from core.local_db import load_db_on_startup, get_local_db
from core import equity_analyzer
from models.models import (
    QueryRequest, QueryResponse, UploadResponse, ErrorResponse,
    EndSessionRequest, EndSessionResponse, AnalysisResultResponse, AnalysisStatusResponse
)

# --- Logging Setup ---
logger = logging.getLogger("main_app")

# --- Global Variables ---
openai_interface: OpenAIInteraction | None = None
rag_system: HybridRAGSystem | None = None

# --- Temporary File Storage ---
TEMP_UPLOAD_DIR = "temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

# === CONFIG ===
BASE_DIR = os.path.dirname(__file__)
ANALYSES_DIR = os.path.join(BASE_DIR, "policy_analyses")  # folder with analyses
os.makedirs(ANALYSES_DIR, exist_ok=True)

# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # (Keep existing lifespan logic as is)
    logger.info("Application startup...")
    global openai_interface, rag_system
    if not settings: logger.critical("Settings not loaded."); yield; return
    try: openai_interface = OpenAIInteraction(); logger.info("OpenAI Interaction initialized.")
    except Exception as e: logger.error(f"Failed OpenAI init: {e}", exc_info=True); openai_interface = None
    load_db_on_startup()
    local_db_instance = get_local_db()
    if local_db_instance: logger.info(f"Local DB loaded with {len(local_db_instance.documents)} docs.")
    else: logger.warning("Local DB did not load successfully.")
    if openai_interface:
        try: rag_system = HybridRAGSystem(openai_interaction=openai_interface); logger.info("Hybrid RAG System initialized.")
        except Exception as e: logger.error(f"Failed RAG init: {e}", exc_info=True); rag_system = None
    else: logger.error("Cannot initialize RAG system (OpenAI failed)."); rag_system = None
    logger.info("Startup complete.")
    yield
    logger.info("Application shutdown...")

# --- FastAPI App Initialization ---
app = FastAPI(title="COEQWAL Analysis Bot", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- CORS Middleware (Optional) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev, allow all; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependency Checks ---
async def check_system_ready():
    if not rag_system or not openai_interface:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Core system components not initialized.")

# --- Session Management ---
async def get_session_id(session_id: str | None = Cookie(None)) -> str | None:
    if session_id is None: return None
    return session_id

async def ensure_session(response: Response, session_id: str | None = Cookie(None)) -> str:
    if session_id is None:
        session_id = str(uuid.uuid4())
        logger.info(f"New session started: {session_id}")
        response.set_cookie(key="session_id", value=session_id, httponly=True, samesite='lax')
    return session_id

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- FIX 1: Define the responses dictionary ---
@app.post("/upload",
        response_model=UploadResponse,
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "File processing failed"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error during upload"},
        })
async def upload_document(
    background_tasks: BackgroundTasks, 
    response: Response,
    file: UploadFile = File(...),
    session_id: str | None = Depends(get_session_id),
    _=Depends(check_system_ready)
):
    """Handles upload. Gets or creates session_id and sets cookie."""
    active_session_id = await ensure_session(response, session_id)
    original_filename = file.filename or "uploaded_file"
    temp_file_path = os.path.join(TEMP_UPLOAD_DIR, f"{active_session_id}_{original_filename}")

    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized. Cannot process upload."
        )

    try:
        logger.info(f"Receiving file '{original_filename}' for session {active_session_id}")
        # Save the file temporarily for processing (blocking)
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        logger.info(f"Temporarily saved file to {temp_file_path}")

        # --- CRITICAL FIX: Get metadata from temp_file_path *NOW*, before it's deleted ---
        file_size_kb = os.path.getsize(temp_file_path) // 1024
        title = equity_analyzer.get_pdf_title(temp_file_path, original_filename)
        upload_date_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(os.path.getmtime(temp_file_path)))
        # --- END CRITICAL FIX ---


        # Initialize session tracking in rag_system.user_sessions upfront
        rag_system.user_sessions[active_session_id] = {
            "file_id": None,
            "vector_store_id": None,
            "original_filename": original_filename,
            "upload_status": "initial_upload_pending", # <--- CHANGE THIS FROM "status" to "upload_status"
            "analysis_status": "pending", # <--- ADD THIS
            "analysis_result_cached": None, # <--- ADD THIS
            "analysis_result_path": None, # <--- ADD THIS
            "analysis_error": None, # <--- ADD THIS
            # Add file metadata needed for equity_analyzer's JSON output
            "file_metadata": { # <--- ADD THIS BLOCK
                "filename": original_filename,
                "title": title,
                "size_kb": file_size_kb,
                "upload_date_utc": upload_date_utc
            }
        }

        # Perform the immediate upload to OpenAI and VS creation (still blocking for HTTP requests)
        success, message = rag_system.add_user_document_for_session(
            session_id=active_session_id,
            file_path=temp_file_path, # rag_system will delete this file internally now
            original_filename=original_filename
        )
        
        current_upload_status = rag_system.user_sessions[active_session_id].get("upload_status", "unknown_after_upload")

        if current_upload_status == "completed":
            background_tasks.add_task(
                equity_analyzer.perform_equity_analysis,
                session_id=active_session_id,
                # Pass collected metadata directly
                original_filename=original_filename, # Redundant if using file_metadata, but harmless for now
                title=title,
                file_size_kb=file_size_kb,
                upload_date_utc=upload_date_utc,
                rag_system_instance=rag_system,
                openai_interface_instance=openai_interface,
                user_sessions_dict=rag_system.user_sessions,
                analysis_output_dir=ANALYSES_DIR # <--- CHANGE THIS TO ANALYSES_DIR
            )
            
            return UploadResponse(
                success=True,
                message=message + " Document indexed for chat. Detailed analysis started in the background.",
                session_id=active_session_id,
                filename=original_filename,
                analysis_status="pending" # <--- This indicates background analysis started
            )
        else: # Upload or VS creation failed early
            logger.error(f"Upload and VS creation failed for session {active_session_id}. Reason: {message}")
            rag_system.user_sessions[active_session_id]['analysis_status'] = 'failed'
            rag_system.user_sessions[active_session_id]['analysis_error'] = message
            
            rag_system.remove_user_session_resources(active_session_id, delete_openai_resources=True)
            
            # rag_system.add_user_document_for_session will only delete temp_file_path on success.
            # So, if upload_status is not 'completed' (i.e., 'failed_upload' or 'failed_vs_creation'),
            # the temp_file_path would still exist and needs to be deleted here.
            if os.path.exists(temp_file_path):
                try: os.remove(temp_file_path); logger.info(f"Cleaned temp file on upload/VS creation failure: {temp_file_path}")
                except OSError: logger.error(f"Could not remove temp file on upload/VS creation failure: {temp_file_path}")

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    except HTTPException as e:
        logger.error(f"HTTPException during upload for session {active_session_id}: {e.detail}", exc_info=False)
        if active_session_id in rag_system.user_sessions:
            rag_system.user_sessions[active_session_id]['analysis_status'] = 'failed'
            rag_system.user_sessions[active_session_id]['analysis_error'] = e.detail
            rag_system.remove_user_session_resources(active_session_id, delete_openai_resources=True)
        # Ensure temp file is removed regardless of if rag_system handled it.
        if os.path.exists(temp_file_path):
            try: os.remove(temp_file_path); logger.info(f"Cleaned temp file on HTTPException: {temp_file_path}")
            except OSError: logger.error(f"Could not remove temp file on HTTPException: {temp_file_path}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during upload for session {active_session_id}: {e}", exc_info=True)
        if active_session_id in rag_system.user_sessions:
            rag_system.user_sessions[active_session_id]['analysis_status'] = 'failed'
            rag_system.user_sessions[active_session_id]['analysis_error'] = str(e)
            rag_system.remove_user_session_resources(active_session_id, delete_openai_resources=True)
        # Ensure temp file is removed regardless of if rag_system handled it.
        if os.path.exists(temp_file_path):
            try: os.remove(temp_file_path); logger.info(f"Cleaned temp file on unexpected error: {temp_file_path}")
            except OSError: logger.error(f"Could not remove temp file on unexpected error: {temp_file_path}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error during upload initiation: {e}")

# --- FIX 2: Define the responses dictionary ---
@app.post("/query",
        response_model=QueryResponse,
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error during query"},
        })
async def handle_query(
    query_req: QueryRequest, # QueryRequest now includes custom_instructions
    _=Depends(check_system_ready)
):
    session_id = query_req.session_id
    query = query_req.query
    focus_area = query_req.focus_area
    custom_instructions = query_req.custom_instructions # <-- Extract the new field

    logger.info(f"Received query for session {session_id}, focus '{focus_area}': '{query[:100]}...'")
    if custom_instructions:
        logger.info(f"Custom instructions provided: '{custom_instructions[:100]}...'")
    if session_id not in rag_system.user_sessions:
        logger.warning(f"Query for session {session_id}, but no document info in RAG system. Local context only.")

    try:
        # Call the analysis function ONCE and store all three results (rag_system.answer_question returns answer, local_sources, openai_sources)
        answer, local_sources, openai_sources = rag_system.answer_question( # <--- ENSURE openai_sources is captured
            session_id=session_id,
            query=query,
            focus_area=focus_area,
            custom_instructions=custom_instructions
        )
        cleaned_answer = answer.strip() if answer else "No answer generated."
        
        logger.info("--- DATA TO BE SENT TO FRONTEND ---")
        logger.info(f"Answer length: {len(cleaned_answer)}")
        logger.info(f"OpenAI Sources found: {len(openai_sources)}")
        for i, source in enumerate(openai_sources):
            # Log clean source to prevent too much clutter in logs
            clean_source_snippet = source.replace('</blockquote>', '').replace('<blockquote>', ' ').strip()[:100] + "..."
            logger.info(f"  Source {i+1}: {clean_source_snippet}")
        logger.info("------------------------------------")
        
        return QueryResponse(
            answer=cleaned_answer,
            local_sources=local_sources,
            openai_sources=openai_sources # <--- ENSURE THIS IS RETURNED
        )
    except Exception as e:
        logger.error(f"Error during query processing for session {session_id}: {e}", exc_info=True)
        detail = str(e) if "Error:" in str(e) else "Internal server error during query processing."
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)



# --- FIX 3: Define the responses dictionary ---
@app.post("/end-session",
        response_model=EndSessionResponse,
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": EndSessionResponse, "description": "Internal error or cleanup failed"},
        })
async def end_session(
    end_req: EndSessionRequest,
    response: Response, # To potentially clear the cookie
    _=Depends(check_system_ready)
):
    """Cleans up resources for the given session ID."""
    session_id = end_req.session_id
    logger.info(f"Received request to end session and clean up resources for: {session_id}")

    if session_id not in rag_system.user_sessions:
        logger.warning(f"Request to end session {session_id}, but it was not found in active sessions.")
        return EndSessionResponse(success=True, message="Session not found or already cleaned up.")

    try:
        success = rag_system.remove_user_session_resources(session_id, delete_openai_resources=True)

        analysis_json_path = os.path.join(ANALYSES_DIR, f"{session_id}.json") # <--- BUILD PATH using ANALYSES_DIR
        if analysis_json_path and os.path.exists(analysis_json_path):
            try:
                os.remove(analysis_json_path)
                logger.info(f"Deleted analysis JSON file: {analysis_json_path}")
            except OSError as e:
                logger.error(f"Error deleting analysis JSON file {analysis_json_path}: {e}")
                success = False # Mark overall success as false if file deletion failed

        if success:
            message = "Session ended and associated resources cleaned up successfully."
            logger.info(message + f" (Session ID: {session_id})")
            response.delete_cookie(key="session_id")
            return EndSessionResponse(success=True, message=message)
        else:
            message = "Session ended, but an error occurred during resource cleanup on the backend. Check server logs."
            logger.error(message + f" (Session ID: {session_id})")
            response.delete_cookie(key="session_id")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "message": message}
            )

    except Exception as e:
        logger.error(f"Unexpected error during session end for {session_id}: {e}", exc_info=True)
        response.delete_cookie(key="session_id")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred while ending the session.")

@app.get("/get_analysis_status/{session_id}", response_model=AnalysisStatusResponse,
        responses={
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Session not found"},
            status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
        })
async def get_analysis_status(session_id: str, _=Depends(check_system_ready)):
    if rag_system is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG system not initialized.")

    session_info = rag_system.user_sessions.get(session_id)
    if not session_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found.")
    
    return AnalysisStatusResponse(
        session_id=session_id,
        analysis_status=session_info.get("analysis_status", "unknown"),
        message=f"Analysis status for session {session_id} is {session_info.get('analysis_status', 'unknown')}.",
        analysis_result_path=session_info.get("analysis_result_path"),
        analysis_error=session_info.get("analysis_error")
    )

@app.get("/get_analysis_result/{session_id}", response_model=AnalysisResultResponse,
        responses={
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Session or analysis not found"},
            status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Analysis not yet completed"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Error retrieving analysis"},
            status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
        })
async def get_analysis_result(session_id: str, _=Depends(check_system_ready)):
    if rag_system is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG system not initialized.")

    session_info = rag_system.user_sessions.get(session_id)
    if not session_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found.")

    analysis_status = session_info.get("analysis_status")
    if analysis_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Analysis for session {session_id} is not yet completed. Current status: {analysis_status}. Error: {session_info.get('analysis_error', 'N/A')}"
        )
    
    analysis_data = session_info.get("analysis_result_cached")
    # Ensure that if it's not cached, it tries to load from the correct path.
    # This path should be the new ANALYSES_DIR
    analysis_path = os.path.join(ANALYSES_DIR, f"{session_id}.json") # <--- BUILD PATH using ANALYSES_DIR

    if analysis_data is None and analysis_path and os.path.exists(analysis_path):
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            # Cache it for future quick access
            session_info['analysis_result_cached'] = analysis_data
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error loading analysis result from file {analysis_path} for session {session_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not load analysis result from file: {e}")
    elif analysis_data is None and (analysis_path is None or not os.path.exists(analysis_path)):
        logger.error(f"Analysis result not found in cache or file for session {session_id}. Path: {analysis_path}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis result not found.")


    return AnalysisResultResponse(
        session_id=session_id,
        analysis_status="completed",
        analysis_data=analysis_data,
        message="Analysis completed and retrieved successfully."
    )
# --- Health Check Endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    if rag_system and openai_interface: return {"status": "ok", "rag_system_initialized": True, "openai_initialized": True}
    else: return {"status": "degraded", "rag_system_initialized": bool(rag_system), "openai_initialized": bool(openai_interface)}
    

@app.get("/api/policies")
async def list_policies():
    """
    Return a lightweight list of all policy analyses metadata.
    """
    policies_list_data = [] # Changed variable name to avoid confusion with the global 'policies' list
    for fname in os.listdir(ANALYSES_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(ANALYSES_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                doc_metadata_from_file = data.get("document", {})
                
                # Prioritize filename for display, then title, then the JSON 'id'
                display_filename = doc_metadata_from_file.get("filename")
                display_title = doc_metadata_from_file.get("title")
                
                # Construct the display name for the list item
                final_display_name = display_filename or \
                                    display_title or \
                                    data.get("id", fname[:-5])
            
                policies_list_data.append({
                    "id": data.get("id", fname[:-5]),
                    # Include a 'document' object, even if sparse, to match Svelte's expectation
                    "document": { 
                        "filename": display_filename or "", # Ensure it's not None
                        "title": display_title or final_display_name # Ensure title is meaningful
                    },
                    "source": data.get("source", "unknown"),
                    # Important: analysis_status and analysis_error must be top-level in your saved JSON for this to work reliably on refresh
                    "analysis_status": data.get("analysis_status", "completed"), # Assuming top-level analysis_status in saved JSON
                    "analysis_error": data.get("analysis_error", None)
                })

        except Exception as e:
            # Log error reading file, but don't stop the whole list
            print(f"Error reading {fname}: {e}")
            continue
    return policies_list_data


@app.get("/api/policies/{policy_id}")
async def get_policy(policy_id: str):
    """
    Return the full JSON data for one policy analysis.
    """
    fpath = os.path.join(ANALYSES_DIR, f"{policy_id}.json")
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="Policy not found")
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content=data)


# --- Run with Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")