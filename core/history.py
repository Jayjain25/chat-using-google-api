# core/history.py
import streamlit as st
import json
import datetime
from pathlib import Path
# Import from top level
import config
import state_manager

# Ensure history directory exists
config.HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# --- Last Chat ID Handling ---
def get_last_chat_id():
    if config.LAST_CHAT_ID_FILE.exists():
        try: return config.LAST_CHAT_ID_FILE.read_text().strip()
        except Exception: return None
    return None

def set_last_chat_id(chat_id):
    try: config.LAST_CHAT_ID_FILE.write_text(str(chat_id))
    except Exception as e: print(f"Warning: Could not write last chat ID: {e}")

# --- File Path ---
def get_chat_filepath(chat_id):
    return config.HISTORY_DIR / f"chat_{chat_id}.json"

# --- Data Structuring ---
def create_save_data():
    messages_to_save = []
    for msg in st.session_state.get("messages", []):
        raw_content = ""
        parts = msg.get("parts", [])
        if parts and isinstance(parts[0], str): raw_content = parts[0]
        messages_to_save.append({ "role": msg.get("role"), "content": raw_content })
    return { "chat_id": st.session_state.current_chat_id, "chat_name": st.session_state.current_chat_name,
        "model_name": st.session_state.model_name, "system_prompt": st.session_state.system_prompt,
        "messages": messages_to_save, "temperature": st.session_state.temperature,
        "top_p": st.session_state.top_p, "max_tokens": st.session_state.max_tokens,
        "response_count": st.session_state.response_count, "saved_at": datetime.datetime.now().isoformat() }

# --- Saving ---
def save_current_chat_to_file():
    chat_id = st.session_state.get("current_chat_id")
    if not chat_id: print("Warning: Attempted to save chat without an ID."); return
    filepath = get_chat_filepath(chat_id)
    try:
        data_to_save = create_save_data()
        with open(filepath, "w", encoding="utf-8") as f: json.dump(data_to_save, f, indent=2)
        set_last_chat_id(chat_id)
    except Exception as e: st.error(f"Error auto-saving chat {chat_id}: {e}", icon="💾")

def save_specific_chat_data(chat_id, chat_data):
    if not chat_id or not chat_data: return False
    filepath = get_chat_filepath(chat_id)
    try:
        chat_data["saved_at"] = datetime.datetime.now().isoformat()
        with open(filepath, "w", encoding="utf-8") as f: json.dump(chat_data, f, indent=2)
        if chat_id == st.session_state.get("current_chat_id"): set_last_chat_id(chat_id)
        return True
    except Exception as e: st.error(f"Error saving chat data for {chat_id}: {e}", icon="💾"); return False

# --- Loading ---
def load_chat_data(chat_id):
    filepath = get_chat_filepath(chat_id)
    if not filepath.exists(): print(f"Chat file not found for ID: {chat_id}"); return None
    try:
        with open(filepath, "r", encoding="utf-8") as f: data = json.load(f)
        return data
    except json.JSONDecodeError: st.error(f"Invalid JSON: {filepath.name}", icon="🚫"); return None
    except Exception as e: st.error(f"Error loading {filepath.name}: {e}", icon="🚫"); return None

def _load_chat_data_into_state(data, source_description):
    if not data: return False
    st.session_state.current_chat_id = data.get("chat_id", state_manager.get_default_chat_id())
    st.session_state.current_chat_name = data.get("chat_name", "Loaded Chat")
    st.session_state.model_name = data.get("model_name", config.DEFAULT_MODEL_NAME)
    st.session_state.system_prompt = data.get("system_prompt", config.DEFAULT_SYSTEM_PROMPT)
    st.session_state.temperature = data.get("temperature", config.DEFAULT_TEMPERATURE)
    st.session_state.top_p = data.get("top_p", config.DEFAULT_TOP_P)
    st.session_state.max_tokens = data.get("max_tokens", config.DEFAULT_MAX_TOKENS)

    loaded_messages_simple = data.get("messages", [])
    st.session_state.messages = []
    temp_response_count = 0
    for i, msg_data in enumerate(loaded_messages_simple):
        role = msg_data.get("role")
        raw_content = msg_data.get("content", "")
        display_content = raw_content
        if role == "model":
            temp_response_count += 1; display_content = f"**(R{temp_response_count})**\n\n{raw_content}"
        st.session_state.messages.append({ "role": role, "parts": [raw_content], "display_content": display_content })
    st.session_state.response_count = temp_response_count

    st.session_state.pending_file_parts = []; st.session_state.last_uploaded_file_names = set()
    st.session_state.renaming_chat_id = None
    print(f"Chat '{st.session_state.current_chat_name}' loaded from {source_description}!")
    set_last_chat_id(st.session_state.current_chat_id)
    return True

def load_chat_from_id(chat_id):
    chat_data = load_chat_data(chat_id)
    if chat_data: return _load_chat_data_into_state(chat_data, f"history (ID: {chat_id[:8]}...)")
    return False

def load_chat_from_upload(uploaded_file):
    try:
        data = json.load(uploaded_file)
        if _load_chat_data_into_state(data, f"uploaded file '{uploaded_file.name}'"):
            save_current_chat_to_file(); return True
        return False
    except json.JSONDecodeError: st.error("Invalid JSON file uploaded.", icon="🚫"); return False
    except Exception as e: st.error(f"Error loading chat from upload: {e}", icon="🚫"); return False

# --- Listing ---
def list_saved_chats():
    chat_files_meta = []
    for filepath in config.HISTORY_DIR.glob("chat_*.json"):
        file_chat_id = filepath.stem.replace("chat_", "")
        chat_data = load_chat_data(file_chat_id)
        if chat_data:
            saved_at_str = chat_data.get("saved_at")
            try: saved_at_dt = datetime.datetime.fromisoformat(saved_at_str) if saved_at_str else datetime.datetime.min
            except ValueError: saved_at_dt = datetime.datetime.min
            chat_files_meta.append({ "id": chat_data.get("chat_id", file_chat_id),
                "name": chat_data.get("chat_name", "Untitled Chat"), "saved_at_str": saved_at_str,
                "saved_at_dt": saved_at_dt })
    chat_files_meta.sort(key=lambda x: x["saved_at_dt"], reverse=True)
    return chat_files_meta

# --- Deleting ---
def delete_chat_file(chat_id):
    filepath = get_chat_filepath(chat_id)
    try:
        if filepath.exists():
            filepath.unlink(); st.toast(f"Deleted chat ID {chat_id[:8]}...", icon="🗑️")
            if get_last_chat_id() == chat_id:
                if config.LAST_CHAT_ID_FILE.exists(): config.LAST_CHAT_ID_FILE.unlink()
            if st.session_state.get("renaming_chat_id") == chat_id: st.session_state.renaming_chat_id = None
            return True
        else: st.warning(f"Chat file ID {chat_id[:8]}... not found.", icon="⚠️"); return False
    except Exception as e: st.error(f"Error deleting {filepath.name}: {e}", icon="❌"); return False