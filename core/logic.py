# core/logic.py
import streamlit as st
import traceback
import google.generativeai as genai
from google.api_core.exceptions import ClientError, GoogleAPIError

# Import top-level and sibling/utils modules
import state_manager # Top level
import config        # Top level
from . import history, gemini # Sibling modules in core
from utils import files   # utils package

# Helper function for formatting display messages
def format_display_message(role, raw_content, response_number=None):
     """Formats raw content for display, adding counter for model messages."""
     if role == "model" and response_number is not None:
         counter_prefix = f"**(R{response_number})**\n\n" if response_number > 0 else ""
         return f"{counter_prefix}{raw_content}"
     return raw_content

def handle_chat_prompt(prompt: str):
    """
    Handles the user's chat input: prepares message, calls API, processes response,
    updates state, and saves history.
    """
    if not prompt or not prompt.strip():
        st.warning("Please enter a message.")
        return

    # Step 1: Prepare User Message Parts for API
    api_parts = []
    files_sent_names = []
    if st.session_state.pending_file_parts:
        pending_files_copy = list(st.session_state.pending_file_parts)
        api_parts.extend(pending_files_copy)
        files_sent_names.extend([part.get("original_filename", f"File {i+1}") for i, part in enumerate(pending_files_copy)])
        st.session_state.pending_file_parts = []; st.session_state.last_uploaded_file_names = set()
    api_parts.append(prompt)

    # Step 2: Add User Message to Session State
    user_display_text = prompt
    if files_sent_names:
         user_display_text += "\n\n*📁 (Sent with: " + ", ".join(files_sent_names) + ")*"
    st.session_state.messages.append({
        "role": "user", "parts": api_parts, "display_content": user_display_text })
    history.save_current_chat_to_file()

    # Step 3: Prepare API History
    api_history = []
    for msg in st.session_state.messages[:-1]:
        parts_for_history = msg.get("parts")
        if parts_for_history is None: parts_for_history = [msg.get("display_content", "")]
        elif not isinstance(parts_for_history, list): parts_for_history = [parts_for_history]
        processed_parts = []
        for part in parts_for_history:
             if isinstance(part, str): processed_parts.append(part)
             elif isinstance(part, dict) and "mime_type" in part and "data" in part: processed_parts.append(part)
             else:
                 try: processed_parts.append(str(part)); print(f"Warning: Converted unexpected part type to string in history: {type(part)}")
                 except Exception: print(f"Warning: Skipping unserializable part type in history: {type(part)}")
        api_history.append({"role": msg["role"], "parts": processed_parts})

    # Step 4: Call Gemini API with Streaming
    try:
        with st.chat_message("model", avatar="✨"):
            response_placeholder = st.empty()
            response_placeholder.markdown("Thinking... 💭")
            full_response_container = [""]
            final_response_obj_container = [None]

            def stream_generator():
                try:
                    generation_config = genai.types.GenerationConfig(
                        temperature=st.session_state.temperature,
                        top_p=st.session_state.top_p,
                        max_output_tokens=st.session_state.max_tokens)
                    safety_settings = {}
                    contents_for_api = api_history + [{"role": "user", "parts": api_parts}]
                    stream = st.session_state.gemini_model.generate_content(
                        contents=contents_for_api, generation_config=generation_config,
                        safety_settings=safety_settings, stream=True)
                    for chunk in stream:
                        final_response_obj_container[0] = chunk
                        if chunk.parts:
                            chunk_text = "".join(part.text for part in chunk.parts if hasattr(part, 'text'))
                            if chunk_text:
                                full_response_container[0] += chunk_text
                                yield chunk_text
                except Exception as e:
                    error_message = f"\n\n*(Error during generation: {e})*"
                    full_response_container[0] += error_message
                    yield error_message
                    print("Error details during stream generation:"); traceback.print_exc()

            response_placeholder.write_stream(stream_generator)
            final_raw_response = full_response_container[0]
            final_response_object = final_response_obj_container[0]
            finish_reason_str, warning_suffix = _determine_finish_reason(final_response_object, final_raw_response)

            if not final_raw_response.strip().startswith("*(Error"): st.session_state.response_count += 1
            final_display_text_with_warning = final_raw_response + warning_suffix
            display_content_with_counter = format_display_message( "model", final_display_text_with_warning, st.session_state.response_count )

            st.session_state.messages.append({ "role": "model", "parts": [final_raw_response], "display_content": display_content_with_counter })
            history.save_current_chat_to_file()

    # Step 5: Handle Errors
    except ClientError as e: st.error(f"Auth Error: {e}", icon="🔑"); _remove_last_user_message_on_error()
    except GoogleAPIError as e: st.error(f"API Error: {e}", icon="☁️"); _remove_last_user_message_on_error()
    except Exception as e: st.error(f"Error: {e}", icon="💥"); st.error(traceback.format_exc()); _remove_last_user_message_on_error()

    # Step 6: Rerun
    st.rerun()

# --- Helper functions ---
def _determine_finish_reason(final_response_object, final_raw_response):
    finish_reason_str = "UNKNOWN"; warning_suffix = ""
    if final_response_object:
        prompt_feedback = getattr(final_response_object, 'prompt_feedback', None)
        try:
            if final_response_object.candidates and final_response_object.candidates[0].finish_reason: finish_reason_str = final_response_object.candidates[0].finish_reason.name
            elif prompt_feedback and prompt_feedback.block_reason: finish_reason_str = prompt_feedback.block_reason.name
            elif final_raw_response and finish_reason_str == "UNKNOWN": finish_reason_str = "STOP"
        except Exception as e: print(f"Could not determine finish reason: {e}")
        if finish_reason_str not in ["STOP", "UNKNOWN", "FINISH_REASON_UNSPECIFIED"]:
            if finish_reason_str == "MAX_TOKENS": warning_suffix = "\n\n*(Response possibly truncated)*"
            elif finish_reason_str == "SAFETY": warning_suffix = "\n\n*(Blocked: Safety)*"
            elif finish_reason_str == "RECITATION": warning_suffix = "\n\n*(Blocked: Recitation)*"
            else: warning_suffix = f"\n\n*(Stopped: {finish_reason_str})*"
    elif not final_raw_response and finish_reason_str == "STOP": warning_suffix = "\n\n*(Empty response received)*"
    return finish_reason_str, warning_suffix

def _remove_last_user_message_on_error():
    try:
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop(); print("Removed last user message due to error.")
            # history.save_current_chat_to_file() # Optional save
    except Exception as e: print(f"Error removing last user message: {e}")