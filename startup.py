# startup.py
import streamlit as st
# Import necessary modules from top-level and core package
import state_manager
import config
from core import history, gemini

def run_startup_logic():
    """Executes one-time setup logic like autoload and initial API checks."""
    if st.session_state.get('app_just_started', True):
        print("Running one-time startup logic...")
        st.session_state.app_just_started = False
        st.session_state.loaded_on_start = False

        if st.session_state.autoload_last_chat:
            last_id = history.get_last_chat_id()
            if last_id:
                print(f"Attempting to autoload last chat ID: {last_id}")
                loaded_successfully = history.load_chat_from_id(last_id)
                if loaded_successfully:
                    st.session_state.loaded_on_start = True
                    gemini.initialize_model() # Initialize model AFTER loading state
                    print(f"Successfully autoloaded chat: {st.session_state.current_chat_name}")
                else:
                    print(f"Failed to load last chat ID {last_id}, starting fresh.")
                    current_id = st.session_state.current_chat_id
                    state_manager.reset_chat_session_state(new_chat_id=current_id)
                    history.save_current_chat_to_file()
                    gemini.initialize_model()
            else:
                print("No last chat ID found, starting fresh.")
                history.save_current_chat_to_file()
                gemini.initialize_model()
        else:
             print("Autoload disabled, starting fresh.")
             history.save_current_chat_to_file()
             gemini.initialize_model()

        if not st.session_state.get("initial_key_check_done", False):
            if st.session_state.google_api_key and not st.session_state.genai_configured:
                print("Performing initial API key check...")
                gemini.configure_genai() # This also initializes model
            elif not st.session_state.google_api_key:
                print("API Key not found for initial check.")
            st.session_state.initial_key_check_done = True

    if st.session_state.get("loaded_on_start", False):
        st.success(f"Chat '{st.session_state.current_chat_name}' auto-loaded!", icon="📂")
        st.session_state.loaded_on_start = False