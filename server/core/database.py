import sqlite3
import os
import logging

try:
    from .config import settings
except ImportError:
    # Fallback if running this module standalone or in a different context.
    class MockSettings:
        # Use the intended production/local development path for the mock
        DATABASE_URL = "sqlite:///./server/analysis_platform.db" # Match intended universal name
    settings = MockSettings()
    logging.warning("Could not import settings. Using mock settings for database path.")

logger = logging.getLogger("database")

# Determine the absolute path to the 'server' directory
SERVER_BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # This is server/core/
SERVER_ROOT_DIR = os.path.abspath(os.path.join(SERVER_BASE_DIR, "..")) # This is server/

# Define the database file path. It should be directly inside SERVER_ROOT_DIR.
if settings and settings.DATABASE_URL.startswith("sqlite:///"):
    db_filename = os.path.basename(settings.DATABASE_URL.replace("sqlite:///", "")) # Extract filename
    DATABASE_FILE_PATH = os.path.join(SERVER_ROOT_DIR, db_filename) # Join it with server root
else:
    # Fallback to default name inside server/ if settings are not good
    DATABASE_FILE_PATH = os.path.join(SERVER_ROOT_DIR, "analysis_platform.db")
    logger.warning(f"DATABASE_URL not properly configured in settings. Defaulting to: {DATABASE_FILE_PATH}")

DATABASE_DIR = os.path.dirname(DATABASE_FILE_PATH)
os.makedirs(DATABASE_DIR, exist_ok=True) # Ensure the directory for the DB file exists

logger.info(f"Database directory ensured: {DATABASE_DIR}")

# SQL statements for table creation
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP
);
"""

CREATE_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    original_filename TEXT,
    document_title TEXT,
    file_size_kb INTEGER,
    upload_date_utc TEXT,
    source TEXT NOT NULL,
    analysis_status TEXT NOT NULL DEFAULT 'pending',
    analysis_error TEXT,
    analysis_json_filepath TEXT, -- Path to the JSON file (e.g., 'user/session_id/analysis.json')
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
"""

CREATE_OPENAI_RESOURCES_TABLE = """
CREATE TABLE IF NOT EXISTS openai_resources (
    openai_resource_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    openai_file_id TEXT,
    openai_vector_store_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);
"""

CREATE_CHAT_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    message_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
"""

# Combine all table creation statements
ALL_TABLE_CREATION_SQL = (
    CREATE_SESSIONS_TABLE +
    CREATE_DOCUMENTS_TABLE +
    CREATE_OPENAI_RESOURCES_TABLE +
    CREATE_CHAT_MESSAGES_TABLE
)

def get_db_connection():
    """Establishes a connection to the SQLite database and creates tables if they don't exist."""
    conn = None
    try:
        logger.info(f"Attempting to connect to database: {DATABASE_FILE_PATH}")
        conn = sqlite3.connect(DATABASE_FILE_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        
        conn.execute("PRAGMA foreign_keys = ON;")
        
        conn.executescript(ALL_TABLE_CREATION_SQL)
        conn.commit()
        
        logger.info("Database connection established and tables checked/created successfully.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection or initialization error: {e}", exc_info=True)
        raise ConnectionError(f"Failed to initialize or connect to the database at {DATABASE_FILE_PATH}: {e}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred during database setup: {e}", exc_info=True)
        raise RuntimeError(f"An unexpected error occurred during database setup at {DATABASE_FILE_PATH}: {e}") from e

def close_db_connection(conn: sqlite3.Connection):
    """Safely closes the database connection."""
    if conn:
        try:
            conn.close()
            logger.debug("Database connection closed.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}", exc_info=True)


# --- FastAPI Dependency for DB Connection ---
def get_db_session():
    """
    FastAPI dependency that provides a database connection for the duration of a request.
    The connection is automatically closed after the request is processed.
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn # Yields the connection to the endpoint function
    finally:
        # Ensures the connection is closed
        close_db_connection(conn)