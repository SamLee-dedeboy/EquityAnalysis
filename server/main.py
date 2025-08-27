import os
import uuid
import logging
import secrets
import json
import time
import sqlite3
from typing import List, Optional, Dict

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, status, Cookie, BackgroundTasks, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Original Core Modules ---
from core.config import settings
from core.openai_interaction import OpenAIInteraction
from core.rag_system import HybridRAGSystem
from core.local_db import load_db_on_startup, get_local_db
from core import equity_analyzer

# --- DB Utilities ---
from core.database import get_db_connection, close_db_connection, get_db_session

# --- Original Models ---
from models.models import (
    QueryRequest, QueryResponse, UploadResponse, ErrorResponse, ChatMessage,
    EndSessionRequest, EndSessionResponse, AnalysisResultResponse, AnalysisStatusResponse
)

logger = logging.getLogger("main_app")

# --- Global Variables ---
openai_interface: OpenAIInteraction | None = None
rag_system: HybridRAGSystem | None = None

# --- File Storage Paths ---
# Base directory of main.py
BASE_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))

TEMP_UPLOAD_DIR = os.path.join(BASE_SERVER_DIR, "temp_uploads")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

# Directory  for the /user/ 
USER_PERSISTENT_DATA_BASE_DIR = os.path.join(BASE_SERVER_DIR, "policy_analyses", "user") 
os.makedirs(USER_PERSISTENT_DATA_BASE_DIR, exist_ok=True)

# Pre-processed analysis JSONs
PREPROCESSED_ANALYSES_DIR = os.path.join(BASE_SERVER_DIR, "policy_analyses", "preprocessed") 
os.makedirs(PREPROCESSED_ANALYSES_DIR, exist_ok=True)

# Base dir for policy_analyses
ANALYSES_ROOT_DIR = os.path.join(BASE_SERVER_DIR, "policy_analyses") 
os.makedirs(ANALYSES_ROOT_DIR, exist_ok=True)

# --- FastAPI Application Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated.")
    global openai_interface, rag_system
    
    if not settings:
        logger.critical("Settings not loaded. Cannot proceed with startup.")
        yield
        return

    try:
        openai_interface = OpenAIInteraction()
        logger.info("OpenAI Interaction layer initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI Interaction: {e}", exc_info=True)
        openai_interface = None

    db_conn_check = None
    try:
        db_conn_check = get_db_connection()
        logger.info("Database connection tested and tables checked/created.")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to initialize database: {e}", exc_info=True)
        raise RuntimeError(f"Database initialization failed: {e}") from e
    finally:
        if db_conn_check:
            close_db_connection(db_conn_check)
    
    load_db_on_startup()
    local_db_instance = get_local_db()
    if local_db_instance: logger.info(f"Local DB loaded with {len(local_db_instance.documents)} docs.")
    else: logger.warning("Local DB did not load successfully.")

    if openai_interface:
        try:
            rag_system = HybridRAGSystem(openai_interaction=openai_interface)
            logger.info("Hybrid RAG System initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Hybrid RAG System: {e}", exc_info=True)
            rag_system = None
    else:
        logger.error("Hybrid RAG System initialization skipped because OpenAI Interaction failed.")
        rag_system = None
    
    logger.info("Application startup complete. Ready to serve requests.")
    yield
    logger.info("Application shutdown initiated.")


app = FastAPI(title="COEQWAL Analysis Bot", lifespan=lifespan)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency Checks ---
async def check_system_ready():
    if not rag_system or not openai_interface:
        logger.error("System not ready: RAG or OpenAI interface not initialized.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Core system components are not initialized. Please check server logs for startup errors."
        )

# --- DB Session Dependency ---
def get_db_session():
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        close_db_connection(conn)

# --- Session Management ---
async def ensure_session(response: Response, session_id: str | None = Cookie(None), db: sqlite3.Connection = Depends(get_db_session)) -> str:
     """
     Manages the user's session ID.
     If a session_id cookie is not present, a new one is generated, set in the cookie,
     and recorded in the 'sessions' table.
     If a session_id exists, its 'last_active_at' timestamp is updated in the DB.
     """
     try:
         cursor = db.cursor()
         
         if session_id is None:
             session_id = str(uuid.uuid4())
             logger.info(f"New session initiated with ID: {session_id}")
             response.set_cookie(key="session_id", value=session_id, httponly=True, samesite='lax')
             
             cursor.execute("INSERT OR IGNORE INTO sessions (session_id, last_active_at) VALUES (?, CURRENT_TIMESTAMP)", (session_id,))
             db.commit()
         else:
             logger.debug(f"Existing session ID '{session_id}' found. Updating last_active_at.")
             cursor.execute("UPDATE sessions SET last_active_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
             db.commit()
     except sqlite3.Error as e:
         logger.error(f"Database error during session management for {session_id}: {e}", exc_info=True)
     
     return session_id


# --- API Endpoints ---
@app.post("/upload",
          response_model=UploadResponse,
          status_code=status.HTTP_200_OK,
          responses={
              status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
              status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "File processing failed (e.g., OpenAI issue)"},
              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error during upload initiation"},
          })
async def upload_document(
    background_tasks: BackgroundTasks,
    response: Response,
    file: UploadFile = File(...),
    session_id: str | None = Cookie(None),
    db: sqlite3.Connection = Depends(get_db_session),
    _=Depends(check_system_ready)
):
    """
    Handles document uploads, initializes session/document records in the DB,
    uploads file to OpenAI, and schedules background analysis.
    """
    active_session_id = await ensure_session(response, session_id, db)
    original_filename = file.filename or "uploaded_file"
    
    # Use the CORRECT path for session-specific user data. This is where the uploaded file will be temporarily saved.
    session_data_dir = os.path.join(USER_PERSISTENT_DATA_BASE_DIR, active_session_id)
    os.makedirs(session_data_dir, exist_ok=True)
    temp_file_path = os.path.join(session_data_dir, f"{active_session_id}_{original_filename}")

    if rag_system is None:
        logger.error("RAG system is None during upload, indicating startup failure.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG system not initialized. Cannot process upload.")

    cursor = db.cursor()
    
    try:
        logger.info(f"Receiving file '{original_filename}' for session: {active_session_id}. Saving temporarily to: {temp_file_path}")
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        logger.info(f"File saved to temporary location.")

        file_size_kb = os.path.getsize(temp_file_path) // 1024
        title = equity_analyzer.get_pdf_title(temp_file_path, original_filename)
        upload_date_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(os.path.getmtime(temp_file_path)))

        doc_id = active_session_id 
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (document_id, session_id, original_filename, document_title, file_size_kb, upload_date_utc, source, analysis_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, active_session_id, original_filename, title, file_size_kb, upload_date_utc, "user", "pending"))
        
        db.commit()

        success_rag, message_rag, file_id_openai, vector_store_id_openai = rag_system.add_user_document_for_session(
            session_id=active_session_id,
            file_path=temp_file_path,
            original_filename=original_filename,
            db_conn=db
        )
        
        if success_rag:
            cursor.execute("UPDATE documents SET analysis_status = ? WHERE document_id = ?", ("vs_processing_pending", doc_id))
            db.commit()
            
            # Pass USER_PERSISTENT_DATA_BASE_DIR as analysis_output_dir
            background_tasks.add_task(
                equity_analyzer.perform_equity_analysis,
                session_id=active_session_id,
                original_filename=original_filename,
                title=title,
                file_size_kb=file_size_kb,
                upload_date_utc=upload_date_utc,
                rag_system_instance=rag_system,
                openai_interface_instance=openai_interface,
                analysis_output_dir=USER_PERSISTENT_DATA_BASE_DIR
            )
            
            return UploadResponse(
                success=True,
                message=message_rag + " Document indexed. Detailed analysis started in background.",
                session_id=active_session_id,
                filename=original_filename,
                analysis_status="pending"
            )
        else:
            logger.error(f"OpenAI upload or VS creation failed for session {active_session_id}. Reason: {message_rag}")
            cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ("failed_upload", message_rag, doc_id))
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message_rag)

    except sqlite3.Error as e:
        logger.error(f"Database error during upload process for session {active_session_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error during upload: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload process for session {active_session_id}: {e}", exc_info=True)
        if os.path.exists(temp_file_path):
            try: os.remove(temp_file_path); logger.info(f"Cleaned temp file on unexpected error: {temp_file_path}")
            except OSError: logger.error(f"Could not remove temp file on unexpected error: {temp_file_path}")
        
        try:
            if db:
                cursor = db.cursor()
                cursor.execute("UPDATE documents SET analysis_status = ?, analysis_error = ? WHERE document_id = ?", ('failed', f"Unexpected error: {e}", active_session_id))
                db.commit()
        except sqlite3.Error as db_e:
            logger.error(f"Failed to update document status to 'failed' in DB for {active_session_id} after unexpected error: {db_e}", exc_info=True)
            
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error during upload initiation: {e}")


@app.post("/query",
        response_model=QueryResponse,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error during query"},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Session or document not found"},
        })
async def handle_query(
    query_req: QueryRequest,
    db: sqlite3.Connection = Depends(get_db_session),
    _=Depends(check_system_ready)
):
    session_id = query_req.session_id
    query = query_req.query
    focus_area = query_req.focus_area
    custom_instructions = query_req.custom_instructions

    logger.info(f"Received query for session {session_id}, focus '{focus_area}': '{query[:100]}...'")
    
    cursor = db.cursor()
    user_vector_store_id = None
    original_filename = "N/A"
    document_analysis_status = "not_found"

    try:
        cursor.execute("""
            SELECT d.original_filename, d.analysis_status, o.openai_vector_store_id
            FROM documents d
            LEFT JOIN openai_resources o ON d.document_id = o.document_id
            WHERE d.document_id = ? AND d.source = 'user'
        """, (session_id,))
        doc_data = cursor.fetchone()

        if not doc_data:
            logger.warning(f"No active user document found in DB for session {session_id}. Query will proceed without document-specific RAG.")
            user_vector_store_id = None
            original_filename = "Generic Document"
            document_analysis_status = "not_found"
        else:
            original_filename, document_analysis_status, user_vector_store_id = doc_data
            logger.debug(f"Document found for session {session_id}. Analysis Status: '{document_analysis_status}'. VS ID: '{user_vector_store_id}'")

        local_db_instance = get_local_db()
        local_chunks = local_db_instance.search(query, top_k=settings.TOP_K_LOCAL) if local_db_instance else []
        local_context_str = rag_system._format_local_context_for_prompt(local_chunks)

        prompt_content_string = rag_system._get_system_prompt(
            focus_area,
            original_filename,
            local_context_str,
            query,
            custom_instructions
        )

        tools = []
        if user_vector_store_id and document_analysis_status == "completed":
            tools.append({
                "type": "file_search",
                "vector_store_ids": [user_vector_store_id],
                "max_num_results": settings.MAX_NUM_RESULTS,
            })
        else:
            logger.warning(f"OpenAI file search disabled for session {session_id}. Document status: {document_analysis_status}, VS ID: {user_vector_store_id}. It needs to be 'completed'.")

        kwargs = {
            "model": settings.RESPONSES_MODEL,
            "input": prompt_content_string,
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["include"] = ["file_search_call.results"]
        
        response_openai = rag_system.openai_interaction.client.responses.create(**kwargs)

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

        try:
            cursor = db.cursor() # Ensure cursor is available here
            # Save user message
            cursor.execute(
                "INSERT INTO chat_messages (message_id, document_id, session_id, sender, message_text) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), session_id, session_id, "user", query)
            )
            # Save bot response
            cursor.execute(
                "INSERT INTO chat_messages (message_id, document_id, session_id, sender, message_text) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), session_id, session_id, "bot", final_answer)
            )
            db.commit()
            logger.info(f"Chat messages saved for session {session_id}.")
        except sqlite3.Error as db_insert_error:
            logger.error(f"Failed to save chat messages to DB for session {session_id}: {db_insert_error}", exc_info=True)
            db.rollback() # Rollback if message insertion fails
            
        return QueryResponse(
            answer=final_answer,
            local_sources=local_chunks,
            openai_sources=retrieved_chunks_from_openai_tool
        )

    except sqlite3.Error as e:
        logger.error(f"Database error during query processing for session {session_id}: {e}", exc_info=True)
        # Ensure DB rollback for any DB error in this block
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during query.")
    except Exception as e:
        logger.error(f"Unexpected error during query processing for session {session_id}: {e}", exc_info=True)
        detail = str(e) if "Error:" in str(e) else "Internal server error during query processing."
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


@app.get("/get_analysis_status/{session_id}", response_model=AnalysisStatusResponse,
         status_code=status.HTTP_200_OK,
         responses={
             status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Session/Document not found"},
             status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error retrieving status"},
         })
async def get_analysis_status(
    session_id: str, # This is the document_id for user uploads
    db: sqlite3.Connection = Depends(get_db_session),
    _=Depends(check_system_ready)
):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT analysis_status, analysis_error FROM documents WHERE document_id = ? AND source = 'user'", (session_id,))
        result = cursor.fetchone()
        if not result:
            logger.warning(f"Analysis status requested for session {session_id}, but user document not found in DB.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User document for session {session_id} not found.")
        
        status, error = result
        return AnalysisStatusResponse(
            session_id=session_id,
            analysis_status=status,
            message=f"Analysis status for session {session_id} is {status}.",
            analysis_result_path=None, # Not needed by frontend for status polling
            analysis_error=error
        )
    except sqlite3.Error as e:
        logger.error(f"Database error getting analysis status for {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error retrieving analysis status.")


@app.get("/get_analysis_result/{session_id}", response_model=AnalysisResultResponse,
         status_code=status.HTTP_200_OK,
         responses={
             status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Session/Document not found"},
             status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Analysis not yet completed"},
             status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Error retrieving analysis file"},
         })
async def get_analysis_result(
    session_id: str, # This is the document_id for user uploads
    db: sqlite3.Connection = Depends(get_db_session),
    _=Depends(check_system_ready)
):
    cursor = db.cursor()
    
    # Initialize variables for potentially missing data
    source = None
    analysis_status = None
    analysis_error = None
    analysis_json_filepath = None
    original_filename = None
    document_title = None
    file_size_kb = None
    upload_date_utc = None
    
    analysis_data = None # To hold the loaded JSON content

    try:
        # 1. First, check if it's a user-uploaded document in the DB
        cursor.execute("""
            SELECT d.source, d.analysis_status, d.analysis_error, d.analysis_json_filepath,
                   d.original_filename, d.document_title, d.file_size_kb, d.upload_date_utc
            FROM documents d
            WHERE d.document_id = ? AND d.source = 'user'
        """, (session_id,))
        doc_data = cursor.fetchone()

        if doc_data:
            source, analysis_status, analysis_error, analysis_json_filepath, \
            original_filename, document_title, file_size_kb, upload_date_utc = doc_data

            if analysis_status != "completed":
                logger.info(f"Analysis result requested for {session_id}, but status is {analysis_status}. Returning conflict.")
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "session_id": session_id,
                        "analysis_status": analysis_status,
                        "message": f"Analysis for session {session_id} is not yet completed. Current status: {analysis_status}. Error: {analysis_error or 'N/A'}",
                        "analysis_error": analysis_error
                    }
                )
            
            # If status is 'completed', try to load the file from disk
            if not analysis_json_filepath or not os.path.exists(analysis_json_filepath):
                logger.error(f"Analysis result file not found on disk for session {session_id} at path: {analysis_json_filepath}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis result file not found on server for user document.")

            with open(analysis_json_filepath, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
        else: # If not found in user documents, check preprocessed folder
            preprocessed_filepath = os.path.join(PREPROCESSED_ANALYSES_DIR, f"{session_id}.json")
            if os.path.exists(preprocessed_filepath):
                try:
                    with open(preprocessed_filepath, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    source = "preprocessed"
                    analysis_status = "completed"
                    analysis_error = None
                    # Attempt to extract metadata from the preprocessed JSON itself
                    doc_metadata_from_file = analysis_data.get("document", {})
                    original_filename = doc_metadata_from_file.get("filename", f"{session_id}.json")
                    document_title = doc_metadata_from_file.get("title", session_id)
                    file_size_kb = doc_metadata_from_file.get("size_kb", 0)
                    upload_date_utc = doc_metadata_from_file.get("upload_date_utc", "N/A")

                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logger.error(f"Error loading preprocessed analysis result {preprocessed_filepath}: {e}", exc_info=True)
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not load preprocessed analysis result file: {e}")
            else:
                logger.warning(f"Analysis result requested for session {session_id}, but neither user document nor preprocessed file found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy analysis for ID {session_id} not found.")

        # Ensure analysis_data is loaded before proceeding
        if analysis_data is None:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis data could not be loaded for an unknown reason.")

        # Ensure top-level fields are present for consistency, merging with loaded data
        analysis_data["id"] = session_id
        analysis_data["source"] = source
        analysis_data["analysis_status"] = analysis_status
        analysis_data["analysis_error"] = analysis_error
        if "document" not in analysis_data: analysis_data["document"] = {}
        analysis_data["document"]["filename"] = original_filename or session_id
        analysis_data["document"]["title"] = document_title or original_filename or session_id
        analysis_data["document"]["size_kb"] = file_size_kb
        analysis_data["document"]["upload_date_utc"] = upload_date_utc


        return AnalysisResultResponse(
            session_id=session_id,
            analysis_status=analysis_status, # Use the determined status
            analysis_data=analysis_data,
            message="Analysis completed and retrieved successfully."
        )
    except HTTPException:
        raise # Re-raise already handled HTTPExceptions
    except sqlite3.Error as e:
        logger.error(f"Database error while fetching analysis result for {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error retrieving analysis result.")
    except Exception as e:
        logger.error(f"Error reading analysis result file or general error for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not load analysis result file: {e}")


@app.post("/end-session",
          response_model=EndSessionResponse,
          status_code=status.HTTP_200_OK,
          responses={
              status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core system not ready"},
              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": EndSessionResponse, "description": "Internal error or cleanup failed"},
          })
async def end_session(
    end_req: EndSessionRequest,
    response: Response, # To delete the cookie
    db: sqlite3.Connection = Depends(get_db_session), # Provides DB connection
    _=Depends(check_system_ready)
):
    """
    Deletes resources associated with a SINGLE DOCUMENT identified by the provided session_id.
    This session_id is used as the document_id for user-uploaded documents.
    It does NOT delete all documents ever uploaded by a user if they reused a session_id.
    """
    document_id_to_delete = end_req.session_id # Frontend passes document_id as session_id
    logger.info(f"Received request to end and cleanup resources for document ID: {document_id_to_delete}")

    cursor = db.cursor()
    
    try:
        # 1. Fetch data needed for cleanup from the 'documents' table for the specific document_id
        cursor.execute("""
            SELECT d.analysis_json_filepath, o.openai_file_id, o.openai_vector_store_id, d.session_id
            FROM documents d
            LEFT JOIN openai_resources o ON d.document_id = o.document_id
            WHERE d.document_id = ? AND d.source = 'user' -- Target only user-uploaded docs
        """, (document_id_to_delete,))
        doc_info = cursor.fetchone()
        
        if not doc_info:
            logger.warning(f"Document ID {document_id_to_delete} not found or not a user-uploaded document. Assuming already cleaned or non-existent.")
            if Cookie("session_id", None) == document_id_to_delete: # Check if current cookie matches deleted doc
                 response.delete_cookie(key="session_id")
            return EndSessionResponse(success=True, message="Document not found or already cleaned up.")

        analysis_json_filepath, openai_file_id, openai_vector_store_id, associated_session_id_from_db = doc_info

        # --- Cleanup Steps ---
        # 1. Initialize cleanup success flags
        openai_cleanup_success = True
        local_file_cleanup_success = True
        db_cleanup_success = True

        # 2. Delete OpenAI resources (if IDs exist)
        if openai_file_id:
            try:
                if not openai_interface.delete_file(openai_file_id):
                    logger.warning(f"Failed to delete OpenAI file {openai_file_id} for doc {document_id_to_delete}.")
                    openai_cleanup_success = False
                else: logger.info(f"OpenAI file {openai_file_id} deleted.")
            except Exception as e:
                logger.error(f"Error deleting OpenAI file {openai_file_id} for doc {document_id_to_delete}: {e}", exc_info=True)
                openai_cleanup_success = False

        if openai_vector_store_id:
            try:
                if not openai_interface.delete_vector_store(openai_vector_store_id):
                    logger.warning(f"Failed to delete OpenAI VS {openai_vector_store_id} for doc {document_id_to_delete}.")
                    openai_cleanup_success = False
                else: logger.info(f"OpenAI VS {openai_vector_store_id} deleted.")
            except Exception as e:
                logger.error(f"Error deleting OpenAI VS {openai_vector_store_id} for doc {document_id_to_delete}: {e}", exc_info=True)
                openai_cleanup_success = False

        # 3. Delete local file system resources (analysis JSON file and potentially its directory)
        if analysis_json_filepath and os.path.exists(analysis_json_filepath):
            try:
                os.remove(analysis_json_filepath)
                logger.info(f"Deleted local analysis JSON file: {analysis_json_filepath}")
            except OSError as e:
                logger.error(f"Error deleting local analysis JSON file {analysis_json_filepath}: {e}", exc_info=True)
                local_file_cleanup_success = False
        else:
            logger.warning(f"Local analysis JSON file not found for deletion (already gone?): {analysis_json_filepath}")
            
        doc_folder_path = os.path.join(USER_PERSISTENT_DATA_BASE_DIR, document_id_to_delete)
        if os.path.exists(doc_folder_path) and not os.listdir(doc_folder_path): # Check if directory is empty
            try:
                os.rmdir(doc_folder_path)
                logger.info(f"Removed empty document directory: {doc_folder_path}")
            except OSError as e:
                logger.warning(f"Failed to remove empty document directory {doc_folder_path}: {e}")

        # 4. Delete database records for THIS specific document_id
        try:
            cursor.execute("DELETE FROM chat_messages WHERE document_id = ?", (document_id_to_delete,))
            cursor.execute("DELETE FROM openai_resources WHERE document_id = ?", (document_id_to_delete,))
            cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id_to_delete,))
            db.commit() # Commit the deletions
            logger.info(f"Database records for document {document_id_to_delete} removed.")
        except sqlite3.Error as e:
            logger.error(f"Database error deleting records for document {document_id_to_delete}: {e}", exc_info=True)
            db.rollback() # Rollback if DB deletion fails
            db_cleanup_success = False

        # 5. Final result based on all cleanup attempts
        if openai_cleanup_success and local_file_cleanup_success and db_cleanup_success:
            message = f"Document {document_id_to_delete} and associated resources cleaned up successfully."
            logger.info(message)
            if associated_session_id_from_db == end_req.session_id: # Assuming end_req.session_id holds the current cookie's value
                 response.delete_cookie(key="session_id")
            return EndSessionResponse(success=True, message=message)
        else:
            message = f"Document {document_id_to_delete} cleanup encountered issues. Check server logs."
            logger.error(message)
            if associated_session_id_from_db == end_req.session_id:
                 response.delete_cookie(key="session_id")
            return JSONResponse(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 content={"success": False, "message": message}
            )

    except sqlite3.Error as e: # Catch overall DB errors during cleanup preparation
        logger.error(f"Database error during end session cleanup for document {document_id_to_delete}: {e}", exc_info=True)
        if db: db.rollback()
        # Still attempt to delete cookie if doc_id matches request's session_id
        if document_id_to_delete == end_req.session_id:
            response.delete_cookie(key="session_id")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error during cleanup: {e}")
    except Exception as e: # Catch general unexpected errors
        logger.error(f"Unexpected error during end session for document {document_id_to_delete}: {e}", exc_info=True)
        if document_id_to_delete == end_req.session_id:
            response.delete_cookie(key="session_id")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during session end.")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    # Attempt to connect to DB for health check
    db_ok = False
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_conn.execute("SELECT 1") # Simple query to test connection
        db_ok = True
    except sqlite3.Error:
        db_ok = False
        logger.error("Health check: Database connection failed.", exc_info=True)
    finally:
        if db_conn:
            close_db_connection(db_conn)

    # Check if rag_system and openai_interface are initialized
    rag_system_initialized_status = bool(rag_system)
    openai_initialized_status = bool(openai_interface)

    # Overall status is 'ok' only if all critical components are ready
    overall_status = "ok" if rag_system_initialized_status and openai_initialized_status and db_ok else "degraded"
    
    return {
        "status": overall_status,
        "openai_initialized": openai_initialized_status,
        "rag_system_initialized": rag_system_initialized_status,
        "db_connected": db_ok
    }
    

@app.get("/api/policies")
async def list_policies(
    db: sqlite3.Connection = Depends(get_db_session), # Inject DB connection
    _=Depends(check_system_ready)
):
    """
    Returns a lightweight list of all policy analyses metadata.
    Includes both preprocessed (from static files) and user-uploaded (from DB/files).
    """
    policies_list_data = []
    cursor = db.cursor()

    try:
        # --- Fetch Preprocessed Policies ---
        # Scan the preprocessed folder for JSON files.
        for fname in os.listdir(PREPROCESSED_ANALYSES_DIR):
            if not fname.endswith(".json"): continue
            fpath = os.path.join(PREPROCESSED_ANALYSES_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    doc_metadata_from_file = data.get("document", {})
                    display_filename = doc_metadata_from_file.get("filename")
                    display_title = doc_metadata_from_file.get("title")
                    
                    final_display_name = display_filename or display_title or data.get("id", fname[:-5])
                    
                    policies_list_data.append({
                        "id": data.get("id", fname[:-5]),
                        "document": {
                            "filename": display_filename or "",
                            "title": display_title or final_display_name
                        },
                        "source": "preprocessed",
                        "analysis_status": "completed", # Preprocessed are always considered completed
                        "analysis_error": None
                    })
            except Exception as e:
                logger.error(f"Error reading preprocessed policy {fname}: {e}", exc_info=True)
                continue
        
        # --- Fetch User-Uploaded Policies from DB ---
        cursor.execute("""
            SELECT d.document_id, d.original_filename, d.document_title, d.source, d.analysis_status, d.analysis_error
            FROM documents d
            WHERE d.source = 'user'
        """)
        user_docs = cursor.fetchall()
        
        for row in user_docs:
            doc_id, original_filename, doc_title, source, status, error = row
            policies_list_data.append({
                "id": doc_id,
                "document": {
                    "filename": original_filename or doc_id,
                    "title": doc_title or original_filename or doc_id
                },
                "source": source,
                "analysis_status": status,
                "analysis_error": error
            })

    except sqlite3.Error as e:
        logger.error(f"Database error listing policies: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching policy list.")
    
    return policies_list_data


@app.get("/api/policies/{policy_id}")
async def get_policy(
    policy_id: str,
    db: sqlite3.Connection = Depends(get_db_session), # Inject DB connection
    _=Depends(check_system_ready)
):
    """
    Return the full data for one policy analysis.
    Handles both preprocessed (from static JSON) and user-uploaded (from file system via DB path).
    """
    cursor = db.cursor()
    
    try:
        # 1. Check if it's a user-uploaded document by looking in the DB
        cursor.execute("""
            SELECT d.original_filename, d.document_title, d.file_size_kb, d.upload_date_utc, d.source, d.analysis_status, d.analysis_error, d.analysis_json_filepath
            FROM documents d
            WHERE d.document_id = ? AND d.source = 'user'
        """, (policy_id,))
        doc_data_user = cursor.fetchone()
        
        if doc_data_user:
            # It's a user-uploaded document found in the DB
            original_filename, doc_title, file_size_kb, upload_date_utc, source, status, error, filepath = doc_data_user
            
            if status != "completed":
                # If it's a user document, and analysis is not complete, return conflict
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "session_id": policy_id, # For user docs, session_id is policy_id
                        "analysis_status": status,
                        "message": f"Analysis for {policy_id} is not yet completed. Status: {status}. Error: {error or 'N/A'}",
                        "analysis_error": error
                    }
                )
            
            # If status is 'completed', try to load the file from disk
            if not filepath or not os.path.exists(filepath):
                logger.error(f"Analysis result file not found on disk for session {policy_id} at path: {filepath}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis result file not found on server.")

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                
                # Ensure top-level fields are present for consistency
                analysis_data["id"] = policy_id
                analysis_data["source"] = source
                analysis_data["analysis_status"] = status
                analysis_data["analysis_error"] = error
                if "document" not in analysis_data: analysis_data["document"] = {}
                analysis_data["document"]["filename"] = original_filename or policy_id
                analysis_data["document"]["title"] = doc_title or original_filename or policy_id
                analysis_data["document"]["size_kb"] = file_size_kb
                analysis_data["document"]["upload_date_utc"] = upload_date_utc

                return JSONResponse(content=analysis_data)

            except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
                logger.error(f"Error loading analysis result from file {filepath} for session {policy_id}: {e}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not load analysis result from file: {e}")

        else: # If not found in user documents, check preprocessed folder
            preprocessed_filepath = os.path.join(PREPROCESSED_ANALYSES_DIR, f"{policy_id}.json")
            if os.path.exists(preprocessed_filepath):
                try:
                    with open(preprocessed_filepath, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    # Ensure preprocessed data has necessary top-level fields
                    analysis_data["id"] = policy_id
                    analysis_data["source"] = "preprocessed"
                    analysis_data["analysis_status"] = "completed"
                    analysis_data["analysis_error"] = None
                    if "document" not in analysis_data: analysis_data["document"] = {}
                    if not analysis_data["document"].get("filename"):
                        analysis_data["document"]["filename"] = policy_id + ".json"
                    if not analysis_data["document"].get("title"):
                        analysis_data["document"]["title"] = policy_id

                    return JSONResponse(content=analysis_data)
                except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
                    logger.error(f"Error loading preprocessed analysis result {preprocessed_filepath}: {e}", exc_info=True)
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not load preprocessed analysis result: {e}")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy analysis for ID {policy_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching policy {policy_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching policy.")
    except Exception as e:
        logger.error(f"Unexpected error fetching policy {policy_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error fetching policy: {e}")

@app.get("/get_chat_history/{document_id}", response_model=List[ChatMessage],
         status_code=status.HTTP_200_OK,
         responses={
             status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Document not found"},
             status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error retrieving chat history"},
         })
async def get_chat_history(
    document_id: str,
    db: sqlite3.Connection = Depends(get_db_session)
):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT 1 FROM documents WHERE document_id = ? AND source = 'user'", (document_id,))
        if not cursor.fetchone():
            logger.warning(f"Attempted to retrieve chat history for non-existent or non-user document: {document_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found or not a user document.")

        cursor.execute(
            "SELECT sender, message_text FROM chat_messages WHERE document_id = ? ORDER BY created_at ASC",
            (document_id,)
        )
        chat_records = cursor.fetchall()

        history = []
        for sender, message_text in chat_records:
            # Map 'user' and 'bot' senders to 'user' and 'bot' message types for frontend consumption
            history.append(ChatMessage(type=sender, content=message_text))
        
        logger.info(f"Retrieved {len(history)} chat messages for document {document_id}.")
        return history
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving chat history for {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error retrieving chat history.")
    except HTTPException:
        raise # Re-raise HTTPException if already handled
    except Exception as e:
        logger.error(f"Unexpected error retrieving chat history for {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error retrieving chat history: {e}")
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")