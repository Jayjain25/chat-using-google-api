# core/gemini.py
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ClientError, GoogleAPIError
# Import config from top level
import config

def initialize_model():
    """Initializes the GenerativeModel object based on current session state settings."""
    if not st.session_state.get("genai_configured", False):
        st.session_state.gemini_model = None; print("Gemini not configured, cannot initialize model."); return

    current_model_name = st.session_state.get("model_name", config.DEFAULT_MODEL_NAME)
    current_system_prompt = st.session_state.get("system_prompt", config.DEFAULT_SYSTEM_PROMPT)
    if not current_system_prompt or not current_system_prompt.strip():
        current_system_prompt = config.DEFAULT_SYSTEM_PROMPT
        st.session_state.system_prompt = current_system_prompt

    try:
        st.session_state.gemini_model = genai.GenerativeModel( current_model_name, system_instruction=current_system_prompt )
        print(f"Gemini model '{current_model_name}' initialized successfully.")
    except Exception as e:
        st.error(f"Error initializing model '{current_model_name}': {e}", icon="⚙️")
        st.session_state.gemini_model = None

def configure_genai():
    """Initializes the Google Generative AI client using API key from session state."""
    api_key = st.session_state.get("google_api_key")
    if api_key:
        try:
            with st.spinner("Configuring Google AI..."): genai.configure(api_key=api_key)
            st.session_state.genai_configured = True
            initialize_model() # Call local function
            return True
        except Exception as e:
            st.error(f"Failed to configure Google AI: {e}", icon="🚨")
            st.session_state.genai_configured = False; st.session_state.gemini_model = None; return False
    else:
        st.session_state.genai_configured = False; st.session_state.gemini_model = None
        print("Google API Key not found in session state for configuration."); return False