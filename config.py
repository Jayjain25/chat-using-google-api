# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory
load_dotenv()

# --- Constants ---
# HISTORY_DIR is relative to where main.py is run
HISTORY_DIR = Path("chat_history")
LAST_CHAT_ID_FILE = HISTORY_DIR / ".last_chat_id"

# --- Default Settings ---
DEFAULT_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL_NAME = "gemini-2.0-flash-lite"
DEFAULT_SYSTEM_PROMPT = "You are a helpful and friendly AI assistant. Analyze any provided images or document content carefully. Be concise and informative in your responses."
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.95
DEFAULT_MAX_TOKENS = 100000 # Increased default for Gemini 1.5 Flash

# Available models list
AVAILABLE_MODELS = [
    "gemini-2.5-pro-preview-03-25",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]

# Ensure history directory exists on import
try:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    print(f"Warning: Could not create history directory {HISTORY_DIR}: {e}")