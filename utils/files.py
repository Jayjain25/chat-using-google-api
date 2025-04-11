# utils/files.py
import streamlit as st
import io

def prepare_file_part(uploaded_file):
    """Prepares an uploaded file object into a dict format suitable for the genai API."""
    if uploaded_file is None: return None
    try:
        file_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type
        if not mime_type:
             st.warning(f"Could not determine MIME type for {uploaded_file.name}. Skipping.", icon="⚠️")
             return None
        return { "mime_type": mime_type, "data": file_bytes, "original_filename": uploaded_file.name }
    except AttributeError as e: st.error(f"Invalid file object provided: {e}", icon="📄"); return None
    except Exception as e: st.error(f"Error preparing file {uploaded_file.name}: {e}", icon="📄"); return None