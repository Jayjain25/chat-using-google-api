# state_manager.py
import streamlit as st
import uuid
# Import config from the same directory
import config

def get_default_chat_id():
    """Generates a new default chat ID."""
    return str(uuid.uuid4())

def initialize_session():
    """
    Initializes all necessary session state variables with defaults using setdefault.
    Safe to call on every script run.
    """
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("current_chat_id", get_default_chat_id())
    st.session_state.setdefault("current_chat_name", "New Chat")
    st.session_state.setdefault("response_count", 0)
    st.session_state.setdefault("google_api_key", config.DEFAULT_GOOGLE_API_KEY)
    st.session_state.setdefault("genai_configured", False)
    st.session_state.setdefault("gemini_model", None)
    st.session_state.setdefault("model_name", config.DEFAULT_MODEL_NAME)
    st.session_state.setdefault("system_prompt", config.DEFAULT_SYSTEM_PROMPT)
    st.session_state.setdefault("pending_file_parts", [])
    st.session_state.setdefault("last_uploaded_file_names", set())
    st.session_state.setdefault("initial_key_check_done", False)
    st.session_state.setdefault("autoload_last_chat", True)
    st.session_state.setdefault("app_just_started", True)
    st.session_state.setdefault("loaded_on_start", False)
    st.session_state.setdefault("renaming_chat_id", None)
    st.session_state.setdefault("temperature", config.DEFAULT_TEMPERATURE)
    st.session_state.setdefault("top_p", config.DEFAULT_TOP_P)
    st.session_state.setdefault("max_tokens", config.DEFAULT_MAX_TOKENS)

def reset_chat_session_state(new_chat_id=None):
    """Resets state variables specific to a single chat session."""
    st.session_state.messages = []
    st.session_state.current_chat_id = new_chat_id or get_default_chat_id()
    st.session_state.current_chat_name = "New Chat"
    st.session_state.response_count = 0
    st.session_state.pending_file_parts = []
    st.session_state.last_uploaded_file_names = set()
    st.session_state.renaming_chat_id = None
    # Keep current model parameters or reset? Let's keep them for now.