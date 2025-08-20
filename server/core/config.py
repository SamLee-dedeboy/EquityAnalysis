# core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, ClassVar
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("chatbot_config")

class Settings(BaseSettings):
    """Loads configuration from environment variables or .env file."""
    OPENAI_API_KEY: str

    # --- Local DB Settings ---
    LOCAL_EMBEDDING_MODEL: str = "all-mpnet-base-v2"
    LOCAL_DB_PATH: str = "db_v9.json" # Relative to project root
    
    # --- Application Database Setting ---
    DATABASE_URL: str = "sqlite:///./server/analysis_platform.db"

    # --- OpenAI Model Settings ---
    # Model for the specialized responses.create endpoint
    RESPONSES_MODEL: str = "gpt-4o-mini"
    # Fallback chat model (if needed elsewhere, not used by default in responses.create)
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    # --- Retrieval Settings ---
    TOP_K_LOCAL: int = 8 # Number of chunks from local COEQWAL DB

    # --- OpenAI Vector Store/File Settings ---
    POLLING_INTERVAL_SECONDS: int = 1
    PROCESSING_TIMEOUT_SECONDS: int = 360 # 6 minutes timeout

    # --- Generation Settings (for responses.create) ---
    TEMPERATURE: float = 0.0
    MAX_OUTPUT_TOKENS: int = 1500 # Max tokens for LLM response generation
    MAX_NUM_RESULTS: int = 10 # Max results for file_search tool
    
    SIMULATE_ANALYSIS: bool = False

    # Class configuration for Pydantic Settings
    class Config:
        env_file = '.env' # Load from .env file
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields not defined in the model
        
try:
    settings = Settings()
    # Check if API key was loaded
    if not settings.OPENAI_API_KEY or "YOUR_OPENAI_API_KEY_HERE" in settings.OPENAI_API_KEY:
        logger.error("OpenAI API Key is missing in .env file.")
    else:
        logger.info("Configuration loaded successfully.")
except Exception as e:
    logger.error(f"CRITICAL: Failed to load settings: {e}", exc_info=True)
    settings = None # Indicate failure