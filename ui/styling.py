# app/ui/styling.py

def load_css() -> str:
    """Returns the CSS styles as a string."""
    return """
<style>
    /* --- General App Styling --- */
    /* Can uncomment to change base font if desired */
    /*
    body, .stApp {
        font-family: 'Google Sans', sans-serif; !important
    }
    */

    .stApp {
        /* background-color: #f0f4f9; */ /* Optional: Light blue-grey background */
    }

    /* --- Sidebar Styling --- */
    [data-testid="stSidebar"] {
        /* background-color: #ffffff; */ /* Optional: White sidebar */
        /* border-right: 1px solid #dee2e6; */ /* Optional: Subtle border */
        padding-top: 1rem; /* Add some padding at the top */
    }
    [data-testid="stSidebar"] .stButton>button {
        border-radius: 8px; /* Slightly rounded buttons */
        border: 1px solid transparent; /* Make border transparent initially */
        background-color: #f8f9fa; /* Light grey button background */
        color: #3c4043; /* Darker text color */
        transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
        font-weight: 500; /* Medium weight */
        padding: 0.4rem 0.75rem; /* Adjust padding */
        margin-bottom: 0.3rem; /* Space between history buttons */
        text-align: left; /* Align text left */
        justify-content: flex-start; /* Align icon and text left */
        overflow: hidden; /* Prevent text overflow */
        text-overflow: ellipsis; /* Add ellipsis for long names */
        white-space: nowrap; /* Keep on one line */
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #e8eaed; /* Slightly darker grey on hover */
        border-color: #dadce0; /* Show subtle border on hover */
    }
    [data-testid="stSidebar"] .stButton>button:active {
         background-color: #dadce0; /* Even darker on click */
    }
    /* Style the primary (current chat) button differently */
    [data-testid="stSidebar"] .stButton>button[kind="primary"] {
         background-color: #e8f0fe; /* Light blue background */
         border: 1px solid #d2e3fc;
         color: #1967d2; /* Blue text */
         font-weight: 500;
    }
    [data-testid="stSidebar"] .stButton>button[kind="primary"]:hover {
         background-color: #d2e3fc;
         border-color: #aecbfa;
    }
    /* Smaller icons for rename/delete */
    [data-testid="stSidebar"] .stButton>button svg[data-icon="pencil"],
    [data-testid="stSidebar"] .stButton>button svg[data-icon="trash"],
    [data-testid="stSidebar"] .stButton>button svg[data-icon="check"],
    [data-testid="stSidebar"] .stButton>button svg[data-icon="x"] {
        height: 1em; /* Adjust size as needed */
        width: 1em;
        vertical-align: middle; /* Align icon better with text */
    }


    /* --- Chat Message Styling --- */
    .stChatMessage {
        border-radius: 12px; /* More rounded corners */
        padding: 0.8rem 1rem; /* Adjust padding */
        margin-bottom: 0.75rem; /* Space between messages */
        box-shadow: 0 1px 3px rgba(60,64,67,0.1); /* Subtle shadow */
        border: none; /* Remove default border */
        max-width: 90%; /* Slightly wider max width */
        background-color: #ffffff; /* Default white background */
        transition: background-color 0.2s ease; /* Smooth background transition */
    }

    /* User messages - Align right */
    div[data-testid="stChatMessage"] {
        /* Default alignment (model) */
        margin-left: 0;
        margin-right: auto; /* Push to left */
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContentUser"]) {
        /* User message alignment */
        margin-left: auto; /* Push to right */
        margin-right: 0;
    }

    /* User message content */
    [data-testid="stChatMessageContentUser"] {
        background-color: #e8f0fe; /* Light blue background for user */
    }

    /* Model message content */
    [data-testid="stChatMessageContentModel"] {
         background-color: #ffffff; /* White background for model */
    }

    /* Reduce paragraph spacing inside messages */
    [data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] p {
        margin-bottom: 0.3rem;
        line-height: 1.5; /* Improve readability */
    }
    [data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] > p:last-child {
        margin-bottom: 0; /* Remove bottom margin on last paragraph */
    }

    /* Code block styling */
    .stChatMessage pre {
        border-radius: 8px;
        background-color: #f1f3f4; /* Light grey for code blocks */
        padding: 0.75rem;
        border: none;
        font-size: 0.9em;
        line-height: 1.4;
    }
    .stChatMessage code:not(pre > code) { /* Inline code styling */
        background-color: #f1f3f4;
        padding: 0.15em 0.4em;
        border-radius: 4px;
        font-size: 0.9em;
    }

    /* --- Copy Button Styling (Attempt) --- */
    /* This selector targets the button within the column used for copy */
    div[data-testid="stChatMessage"] > div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        padding: 0.1rem !important; /* Make it small */
        box-shadow: none !important;
        margin-top: 0rem; /* Fine-tune vertical alignment */
        color: #5f6368; /* Grey icon color */
        opacity: 0.7; /* Slightly transparent until hover */
        transition: opacity 0.2s ease;
    }
    div[data-testid="stChatMessage"] > div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stButton"] > button:hover {
         background: #e0e0e0 !important; /* Subtle hover background */
         opacity: 1;
    }
    div[data-testid="stChatMessage"] > div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stButton"] > button svg {
        width: 0.9em !important; /* Smaller icon */
        height: 0.9em !important;
    }


    /* --- Chat Input --- */
    /* Limited styling possible */
    /* [data-testid="stChatInput"] { */
        /* background-color: #ffffff; */
        /* box-shadow: 0 -1px 4px rgba(0,0,0,0.05); */
        /* border-top: 1px solid #dee2e6; */
    /* } */
    /* [data-testid="stChatInputTextArea"] > textarea { */
        /* background-color: #f8f9fa; */ /* Slightly grey background */
        /* border-radius: 8px; */
        /* border: 1px solid #dadce0; */
    /* } */

    /* --- Loading Animation --- */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .thinking-indicator {
        display: inline-block; /* Needed for animation */
        animation: pulse 1.5s ease-in-out infinite;
        font-style: italic;
        color: #5f6368; /* Dim color */
    }

</style>
"""