
import os
import streamlit as st
from google import genai
from google.genai import types

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Nova AI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #101426, #171b35, #111827);
        color: #f3f4f6;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #111629;
        border-right: 1px solid #303653;
    }

    .hero {
        text-align: center;
        padding: 28px 12px 24px 12px;
        border: 1px solid #373b64;
        border-radius: 22px;
        background: linear-gradient(135deg, #24294b, #30204c);
        margin-bottom: 24px;
    }

    .hero-icon {
        font-size: 48px;
        margin-bottom: 6px;
    }

    .hero h1 {
        color: #ffffff;
        font-size: 35px;
        margin: 0;
        font-weight: 750;
    }

    .hero p {
        color: #c5c9e5;
        margin-top: 10px;
        font-size: 15px;
    }

    .status {
        display: inline-block;
        padding: 6px 12px;
        background: #183d38;
        color: #91f0ce;
        border-radius: 20px;
        font-size: 12px;
        margin-top: 12px;
    }

    .stChatMessage {
        border: 1px solid #343957;
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
        background-color: #1b2037;
    }

    .stChatInput textarea {
        background: #1b2037 !important;
        color: white !important;
    }

    div.stButton > button {
        border-radius: 12px;
        border: 1px solid #6f6ce8;
        background: linear-gradient(90deg, #6259db, #9257d9);
        color: white;
        font-weight: 600;
    }

    div.stButton > button:hover {
        border-color: #b4a8ff;
        color: white;
    }

    .footer {
        text-align: center;
        color: #929ab8;
        font-size: 12px;
        margin-top: 28px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- API CONFIGURATION ----------------
MODEL = "gemini-3.5-flash-lite"
api_key = os.getenv("GEMINI_API_KEY")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ✨ Nova AI")
    st.caption("Your personal AI workspace")
    st.divider()

    st.markdown("### About")
    st.write(
        "Nova is a Python-based AI assistant "
        "powered by the Gemini API."
    )

    st.markdown("### Capabilities")
    st.write("💬 Answer questions")
    st.write("💻 Help with coding")
    st.write("📚 Explain concepts")
    st.write("✍️ Generate ideas and text")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Built with Python + Streamlit + Gemini")

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <div class="hero-icon">✨</div>
    <h1>Nova AI Assistant</h1>
    <p>Your ideas, questions, and tasks — one conversation away.</p>
    <span class="status">● AI Assistant Interface</span>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.error(
        "GEMINI_API_KEY was not found. Set your API key "
        "in the terminal used to launch this app, then restart it."
    )
    st.stop()

# Create the Gemini client
client = genai.Client(api_key=api_key)

# ---------------- CHAT HISTORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome suggestions
if not st.session_state.messages:
    st.markdown("### What would you like to explore?")
    col1, col2 = st.columns(2)

    if col1.button("🤖 Learn about AI", use_container_width=True):
        st.session_state.pending_prompt = (
            "Explain Artificial Intelligence in simple words."
        )
        st.rerun()

    if col2.button("🐍 Python coding", use_container_width=True):
        st.session_state.pending_prompt = (
            "Write a beginner-friendly Python program to add two numbers."
        )
        st.rerun()

    if col1.button("🔌 Understand APIs", use_container_width=True):
        st.session_state.pending_prompt = (
            "Explain APIs and how they work with a simple example."
        )
        st.rerun()

    if col2.button("💡 Generate ideas", use_container_width=True):
        st.session_state.pending_prompt = (
            "Give me five useful AI project ideas for a fresh graduate."
        )
        st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get a new message or a suggested prompt
question = st.chat_input("Message Nova AI...")

if "pending_prompt" in st.session_state:
    question = st.session_state.pop("pending_prompt")

# ---------------- GENERATE RESPONSE ----------------
if question:
    question = question.strip()

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Nova is thinking..."):
                try:
                    # Include recent conversation for context
                    conversation = []

                    for message in st.session_state.messages[-12:]:
                        role = (
                            "user" if message["role"] == "user"
                            else "model"
                        )
                        conversation.append({
                            "role": role,
                            "parts": [{"text": message["content"]}]
                        })

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=conversation,
                        config=types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=800
                        )
                    )

                    answer = response.text

                    if not answer:
                        answer = "I couldn't generate a text response. Please try again."

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:
                    error_message = str(error)

                    if "503" in error_message or "UNAVAILABLE" in error_message:
                        st.warning(
                            "The AI model is temporarily busy. "
                            "Please wait a little and try again."
                        )
                    elif "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                        st.warning(
                            "The API usage limit may have been reached. "
                            "Check your Gemini API quota and try again later."
                        )
                    elif "401" in error_message or "403" in error_message or "API_KEY_INVALID" in error_message:
                        st.error(
                            "The API key was rejected. Check that your "
                            "replacement key is valid and enabled."
                        )
                    elif "404" in error_message or "NOT_FOUND" in error_message:
                        st.error(
                            "The selected model is unavailable to this API. "
                            "Check the current model names in Google's documentation."
                        )
                    else:
                        st.error(
                            "The request failed. Check your internet connection, "
                            "API configuration, and usage limits."
                        )

                    # Remove the failed user message so it can be retried
                    st.session_state.messages.pop()


# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
/* Main application */
.stApp {
    background: linear-gradient(135deg, #0b1020, #17152e, #101827);
    color: #f1f5f9;
}

/* Header and toolbar */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #11172a;
    border-right: 1px solid #303954;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

/* Main title card */
.hero {
    text-align: center;
    padding: 30px 16px;
    border: 1px solid #484477;
    border-radius: 22px;
    background: linear-gradient(135deg, #292653, #3b2358);
    margin-bottom: 25px;
}

.hero-icon {
    font-size: 48px;
}

.hero h1 {
    color: #ffffff !important;
    font-size: 36px;
    margin: 0;
}

.hero p {
    color: #d6d8f5 !important;
    font-size: 15px;
    margin-top: 10px;
}

.status {
    display: inline-block;
    padding: 7px 13px;
    background: #174638;
    color: #a7f3d0 !important;
    border-radius: 20px;
    font-size: 12px;
    margin-top: 12px;
}

/* Make headings and normal text readable */
.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #e8eaf6;
}

/* Chat message cards */
[data-testid="stChatMessage"] {
    background: #1b2340;
    border: 1px solid #374363;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

/* Chat input container */
[data-testid="stChatInput"] {
    background: #151c30 !important;
    border: 1px solid #414b6b !important;
    border-radius: 16px !important;
    padding: 8px !important;
}

[data-testid="stChatInput"] textarea {
    background: #151c30 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #aab4d0 !important;
    -webkit-text-fill-color: #aab4d0 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #6557e8, #9255d6);
    color: #ffffff !important;
    border: 1px solid #8175f0;
    border-radius: 12px;
    font-weight: 600;
    min-height: 42px;
}

.stButton > button:hover {
    border-color: #c4b5fd;
    color: #ffffff !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #aab4d0 !important;
    font-size: 12px;
    margin-top: 28px;
    padding: 15px;
}

/* Hide Streamlit's default decoration */
#MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)