# main.py
import streamlit as st
import traceback # Keep for potential top-level debugging if needed

# Import from top-level files and new packages
import config
import state_manager
import startup
from ui import sidebar, chat_display # Import UI package modules
from core import logic, gemini     # Import Core package modules

# --- Set Page Config FIRST ---
# Must be the first Streamlit command
st.set_page_config(page_title="Gemini Chat+", layout="wide")

# --- Initialize Session State (Runs on every script execution) ---
state_manager.initialize_session()

# --- Run One-Time Startup Logic ---
startup.run_startup_logic()

# --- Main App UI ---
st.title(f"✨ Gemini Chat: {st.session_state.current_chat_name}")
# Display caption based on initialized session state
st.caption(f"Model: `{st.session_state.model_name}` | Temp: `{st.session_state.temperature:.2f}` | TopP: `{st.session_state.top_p:.2f}` | Max Tokens: `{st.session_state.max_tokens}` | Chat ID: `{st.session_state.current_chat_id[:8]}...`")

# --- Render Sidebar UI ---
sidebar.render_sidebar() # Call function from ui.sidebar

# --- Render Chat Message History ---
chat_display.display_chat_messages() # Call function from ui.chat_display

# --- Handle Chat Input ---
# Check if the model is ready before enabling input
model_ready = st.session_state.get("gemini_model") is not None
prompt = st.chat_input("Ask Gemini...", disabled=(not model_ready))

if prompt:
    logic.handle_chat_prompt(prompt) # Call function from core.logic

# --- Optional: Add footer ---
# st.divider()
# st.caption("Modular Gemini Chatbot v3")