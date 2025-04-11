# Streamlit Google Gemini Chatbot (Multimodal)

A Streamlit application providing a conversational interface to Google's Gemini models (including the multimodal Gemini 1.5 Pro), featuring chat management and file uploads (PDFs, Images).

## Features

*   **Conversational Chat:** Interact with Gemini models using natural language.
*   **API Key Management:** Securely input your Google API Key or load it from `.env`.
*   **Model Selection:** Choose between available Gemini models (e.g., `gemini-1.5-pro-latest`, `gemini-pro`).
*   **Parameter Tuning:** Adjust `temperature`, `top_p`, `max_tokens`.
*   **System Instructions:** Provide context/instructions, with a helpful default.
*   **Multimodal Input:** Upload Images and PDFs. Gemini (especially 1.5 Pro) can process the content directly.
*   **Chat History:** View the conversation history.
*   **Chat Management:** New Chat, Rename, Clear Messages, Save (Local JSON), Load (Local JSON).

## Setup

1.  **Clone the repository.**
2.  **Create a virtual environment (recommended).**
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Get your Google API Key:**
    *   Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create and copy your API key. Ensure it's enabled for the Gemini API.
5.  **Create the `.env` file:**
    *   Use `cp .env.example .env` or create `.env`.
    *   Add your key: `GOOGLE_API_KEY="YOUR_KEY_HERE"`
    *   Add `.env` to your `.gitignore`.
6.  **Create `.gitignore` (if needed):**
    ```gitignore
    # .gitignore
    venv/
    .env
    __pycache__/
    *.pyc
    *.json # Optional: ignore downloaded chat files
    ```

## Running the App

```bash
streamlit run app.py