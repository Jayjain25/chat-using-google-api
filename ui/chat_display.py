# ui/chat_display.py
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard

def display_chat_messages():
    """Displays the chat message history in the main app area."""
    message_container = st.container()
    with message_container:
        if not st.session_state.get("messages"):
            st.info("Start chatting below, or load a chat from the history!", icon="👋")
            return

        for i, msg in enumerate(st.session_state.messages):
            role = msg.get("role", "user")
            avatar = "👤" if role == "user" else "✨"
            display_content = msg.get("display_content", "")

            if role == "model":
                 col1, col2 = st.columns([0.95, 0.05])
                 with col1:
                     with st.chat_message(role, avatar=avatar):
                        st.markdown(display_content, unsafe_allow_html=False)
                 with col2:
                    raw_content_list = msg.get("parts", [])
                    raw_content = raw_content_list[0] if raw_content_list and isinstance(raw_content_list[0], str) else ""
                    copy_key=f"copy_{st.session_state.current_chat_id}_{i}"
                    st_copy_to_clipboard(raw_content, key=copy_key) # Use basic call
            else: # User message
                with st.chat_message(role, avatar=avatar):
                    st.markdown(display_content, unsafe_allow_html=False)