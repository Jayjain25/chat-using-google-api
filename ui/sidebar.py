# ui/sidebar.py
import streamlit as st
import json
import datetime

# Import from top-level and core/utils packages
import config
import state_manager
from core import history, gemini
from utils import files

def render_sidebar():
    """Renders all elements within the Streamlit sidebar."""
    with st.sidebar:
        with st.expander("📜 Chat History & Management", expanded=True):
            if st.button("➕ New Chat", use_container_width=True, key="new_chat_top_history"):
                history.save_current_chat_to_file(); state_manager.reset_chat_session_state()
                gemini.initialize_model(); history.save_current_chat_to_file()
                st.success("Started new chat.", icon="✨"); st.rerun()
            saved_chats = history.list_saved_chats()
            if not saved_chats: st.caption("No saved chats yet.")
            else:
                st.caption("Click name to load, ✏️ to rename, 🗑️ to delete.")
                for chat_meta in saved_chats: _render_chat_history_item(chat_meta)
        st.divider()
        with st.expander("⚙️ Configuration", expanded=False):
            st.checkbox("Auto-load last chat on startup", key="autoload_last_chat", help="Load last chat automatically.")
            _render_api_key_section()
            _render_model_selection()
            _render_system_prompt()
        st.divider()
        with st.expander("📎 Attach Files", expanded=False): _render_file_uploader()
        st.divider()
        with st.expander("🛠️ Chat Controls", expanded=False): _render_chat_controls()
        st.divider()
        with st.expander("🤖 Model Parameters", expanded=False): _render_model_parameters()

# --- Helper functions ---
def _render_chat_history_item(chat_meta):
    chat_id = chat_meta['id']; display_name = chat_meta['name']
    is_current = (chat_id == st.session_state.current_chat_id)
    is_renaming = (chat_id == st.session_state.get("renaming_chat_id"))
    col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
    with col1:
        if is_renaming:
            rename_input_key = f"rename_input_{chat_id}"; st.text_input("New name:", value=display_name, key=rename_input_key, label_visibility="collapsed")
        else:
            load_key = f"load_{chat_id}"; button_type = "primary" if is_current else "secondary"; saved_time_str = ""
            try: saved_time_str = chat_meta['saved_at_dt'].strftime("%H:%M")
            except Exception: pass
            button_label = f"{display_name} ({saved_time_str})"
            if st.button(button_label, key=load_key, use_container_width=True, help="Load this chat", type=button_type):
                if not is_current: history.save_current_chat_to_file()
                if history.load_chat_from_id(chat_id): gemini.initialize_model(); st.rerun()
    with col2:
        if is_renaming:
            save_rename_key = f"save_rename_{chat_id}"
            if st.button("✅", key=save_rename_key, help="Save new name", use_container_width=True):
                new_name = st.session_state.get(rename_input_key, display_name).strip()
                if new_name and new_name != display_name:
                    chat_data = history.load_chat_data(chat_id)
                    if chat_data:
                        chat_data["chat_name"] = new_name
                        if history.save_specific_chat_data(chat_id, chat_data):
                            st.toast(f"Renamed to '{new_name}'", icon="✏️")
                            if is_current: st.session_state.current_chat_name = new_name
                            st.session_state.renaming_chat_id = None; st.rerun()
                elif new_name == display_name: st.session_state.renaming_chat_id = None; st.rerun()
                else: st.warning("Enter a valid name.", icon="⚠️")
        else:
             rename_icon_key = f"rename_icon_{chat_id}";
             if st.button("✏️", key=rename_icon_key, help="Rename this chat", use_container_width=True): st.session_state.renaming_chat_id = chat_id; st.rerun()
    with col3:
        if is_renaming:
             cancel_rename_key = f"cancel_rename_{chat_id}";
             if st.button("❌", key=cancel_rename_key, help="Cancel rename", use_container_width=True): st.session_state.renaming_chat_id = None; st.rerun()
        else:
             delete_key = f"delete_{chat_id}"
             if st.button("🗑️", key=delete_key, help=f"Delete chat '{display_name}'", use_container_width=True):
                 if history.delete_chat_file(chat_id):
                     if is_current:
                         remaining_chats = history.list_saved_chats(); loaded_new = False
                         if remaining_chats:
                             if history.load_chat_from_id(remaining_chats[0]['id']): gemini.initialize_model(); st.success("Deleted current, loaded recent.", icon="✨"); loaded_new = True
                         if not loaded_new: state_manager.reset_chat_session_state(); gemini.initialize_model(); history.save_current_chat_to_file(); st.success("Deleted last chat, started new one.", icon="✨")
                     st.rerun()

def _render_api_key_section():
    st.subheader("API Key")
    api_key_input = st.text_input("Google API Key", type="password", value=st.session_state.google_api_key or "", key="api_key_input_widget", label_visibility="collapsed", help="Get key from Google AI Studio.")
    button_disabled = (api_key_input == st.session_state.google_api_key and st.session_state.genai_configured)
    if st.button("Update API Key", key="update_api_key_button", use_container_width=True, disabled=button_disabled):
        st.session_state.google_api_key = api_key_input; st.session_state.genai_configured = False; st.session_state.gemini_model = None
        if gemini.configure_genai(): st.success("Google AI configured.", icon="🔑")
        st.rerun()
    if st.session_state.genai_configured and st.session_state.gemini_model: st.success("Client & model ready.", icon="✅")
    elif st.session_state.genai_configured: st.warning("Model not ready.", icon="⚠️")
    else: st.error("Client not configured.", icon="❌")

def _render_model_selection():
    st.subheader("Model Selection")
    current_model_list = list(config.AVAILABLE_MODELS)
    try: current_selectbox_index = current_model_list.index(st.session_state.model_name)
    except ValueError:
        if st.session_state.model_name not in current_model_list: current_model_list.insert(0, st.session_state.model_name)
        current_selectbox_index = 0
    selected_model = st.selectbox("Available Models", current_model_list, index=current_selectbox_index, label_visibility="collapsed", disabled=not st.session_state.genai_configured, help="Select a Gemini model.", key="model_selectbox")
    if selected_model != st.session_state.model_name:
        st.session_state.model_name = selected_model; gemini.initialize_model(); history.save_current_chat_to_file(); st.rerun()

def _render_system_prompt():
    st.subheader("System Instructions")
    def system_prompt_on_change(): gemini.initialize_model(); history.save_current_chat_to_file()
    st.text_area("System Instructions", key="system_prompt", height=100, label_visibility="collapsed", disabled=not st.session_state.genai_configured, help="Guide the model's behavior.", on_change=system_prompt_on_change)

def _render_file_uploader():
    uploaded_files = st.file_uploader("Upload Images/PDFs", type=["png", "jpg", "jpeg", "webp", "gif", "pdf"], accept_multiple_files=True, key="file_uploader", label_visibility="collapsed", disabled=not st.session_state.genai_configured)
    if uploaded_files:
        current_pending_filenames = {part.get("original_filename") for part in st.session_state.pending_file_parts}
        files_to_process = [f for f in uploaded_files if f.name not in current_pending_filenames and f.name not in st.session_state.last_uploaded_file_names]
        if files_to_process:
            with st.spinner(f"Processing {len(files_to_process)} file(s)..."):
                for file in files_to_process:
                    prepared_part = files.prepare_file_part(file) # Use files.py function
                    if prepared_part and file.name not in current_pending_filenames:
                         st.session_state.pending_file_parts.append(prepared_part); st.session_state.last_uploaded_file_names.add(file.name)
    if st.session_state.pending_file_parts:
        st.success(f"{len(st.session_state.pending_file_parts)} file(s) ready:", icon="📎")
        for i, part in enumerate(st.session_state.pending_file_parts): st.caption(f"- {part.get('original_filename', f'File {i+1}')}")
        if st.button("Clear Pending Files", key="clear_pending", use_container_width=True):
            st.session_state.pending_file_parts = []; st.session_state.last_uploaded_file_names = set(); st.rerun()

def _render_chat_controls():
    st.subheader("Import / Export / Clear")
    col1, col2 = st.columns(2)
    with col1:
        try:
            save_data_str = json.dumps(history.create_save_data(), indent=2)
            safe_chat_name = "".join(c if c.isalnum() else "_" for c in st.session_state.current_chat_name)
            dl_filename = f"chat_export_{safe_chat_name}_{datetime.datetime.now():%Y%m%d_%H%M}.json"
            st.download_button("📥 Export", save_data_str, dl_filename, "application/json", use_container_width=True, disabled=not st.session_state.messages, help="Download current chat.")
        except Exception as e: st.error(f"Export error: {e}", icon="💾")
    with col2:
        uploaded_file_for_load = st.file_uploader("📤 Import", type="json", label_visibility="collapsed", key="load_chat_uploader", help="Load chat from JSON.")
        if uploaded_file_for_load is not None:
             history.save_current_chat_to_file()
             if history.load_chat_from_upload(uploaded_file_for_load): gemini.initialize_model(); st.rerun()
    if st.button("🧹 Clear Messages", use_container_width=True, disabled=not st.session_state.messages, help="Clear messages from current session."):
        st.session_state.messages = []; st.session_state.pending_file_parts = []
        st.session_state.last_uploaded_file_names = set(); st.session_state.response_count = 0
        history.save_current_chat_to_file(); st.success("Messages cleared.", icon="🧹"); st.rerun()

def _render_model_parameters():
    is_model_ready = st.session_state.gemini_model is not None
    st.slider("Temperature", 0.0, 2.0, step=0.1, key="temperature", disabled=not is_model_ready, help="Controls randomness.", on_change=history.save_current_chat_to_file)
    st.slider("Top P", 0.0, 1.0, step=0.05, key="top_p", disabled=not is_model_ready, help="Nucleus sampling.", on_change=history.save_current_chat_to_file)
    st.slider("Max Tokens", 50, config.DEFAULT_MAX_TOKENS, step=50, key="max_tokens", disabled=not is_model_ready, help="Max response length.", on_change=history.save_current_chat_to_file)