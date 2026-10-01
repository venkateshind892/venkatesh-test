import streamlit as st
import requests

# --------------------------------
# NxT AI - Offline Local AI Chat
# --------------------------------

st.set_page_config(
    page_title="NxT AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"

# --------------------------------
# SESSION STATE
# --------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = DEFAULT_MODEL

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = (
        "You are NxT AI, a helpful offline AI assistant. "
        "Give clear, accurate, friendly and useful answers."
    )

# --------------------------------
# GLASSMORPHISM UI
# --------------------------------

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 10% 5%,
        rgba(0, 132, 255, 0.17), transparent 38%),
        radial-gradient(ellipse at 90% 80%,
        rgba(0, 220, 255, 0.10), transparent 35%),
        linear-gradient(135deg, #050b19, #0a1730 55%, #071226);
    color: #f2f7ff;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: rgba(9, 20, 42, 0.82);
    border-right: 1px solid rgba(100, 180, 255, 0.15);
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

h1, h2, h3, p, label {
    color: #edf5ff;
}

.hero {
    background: linear-gradient(
        135deg,
        rgba(35, 75, 135, 0.35),
        rgba(10, 25, 55, 0.48)
    );
    border: 1px solid rgba(125, 190, 255, 0.22);
    border-radius: 24px;
    padding: 28px;
    margin-bottom: 20px;
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.20);
}

.brand {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #ffffff, #58caff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #a9c3e8;
    font-size: 14px;
    margin-top: 6px;
}

.status {
    display: inline-block;
    border: 1px solid rgba(40, 230, 160, 0.4);
    background: rgba(20, 200, 130, 0.10);
    color: #65f2b8;
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 600;
}

.glass-card {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(155, 195, 255, 0.15);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

div[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(145, 190, 255, 0.13);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 12px;
    backdrop-filter: blur(16px);
}

div[data-testid="stChatInput"] {
    background: rgba(16, 35, 68, 0.80);
    border: 1px solid rgba(85, 170, 255, 0.30);
    border-radius: 18px;
}

div[data-testid="stChatInput"] textarea {
    color: #ffffff;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid rgba(85, 175, 255, 0.28);
    background: rgba(45, 105, 180, 0.15);
    color: #eaf5ff;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border-color: #37baff;
    background: rgba(35, 140, 235, 0.25);
    color: white;
    box-shadow: 0 0 18px rgba(0, 155, 255, 0.15);
}

div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
}

hr {
    border-color: rgba(120, 170, 230, 0.15);
}

.small-note {
    color: #8faed5;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# OLLAMA CONNECTION
# --------------------------------

@st.cache_data(ttl=10)
def get_ollama_models():
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=2
        )
        response.raise_for_status()
        return [
            model["name"]
            for model in response.json().get("models", [])
        ]
    except requests.RequestException:
        return []

models = get_ollama_models()
connected = bool(models)

# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand" style="font-size:27px">'
        '🤖 NxT AI</div>',
        unsafe_allow_html=True
    )
    st.caption("OFFLINE INTELLIGENCE")

    st.divider()

    if st.button("＋  New Conversation",
                 use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 💬 Chat History")

    if st.session_state.messages:
        user_prompts = [
            msg["content"]
            for msg in st.session_state.messages
            if msg["role"] == "user"
        ]
        for i, item in enumerate(user_prompts):
            st.caption(f"{i + 1}. {item[:35]}")
    else:
        st.caption("Your conversations will appear here.")

    st.divider()
    st.markdown("### ⚙️ Settings")

    if models:
        default_index = (
            models.index(st.session_state.model)
            if st.session_state.model in models else 0
        )
        selected_model = st.selectbox(
            "Local AI Model",
            models,
            index=default_index
        )
        st.session_state.model = selected_model
    else:
        st.text_input(
            "Local AI Model",
            value=st.session_state.model,
            disabled=True
        )

    st.session_state.system_prompt = st.text_area(
        "AI Instructions",
        value=st.session_state.system_prompt,
        height=100
    )

    st.divider()

    if connected:
        st.markdown(
            '<div class="status">● Local AI Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Local AI is not connected")

    if st.button("🔄 Refresh Connection",
                 use_container_width=True):
        get_ollama_models.clear()
        st.rerun()

    if st.button("🗑️ Clear Chat",
                 use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        '<p class="small-note">'
        'NxT AI • On-device AI concept<br>'
        'Your prompts are sent to your local Ollama runtime.'
        '</p>',
        unsafe_allow_html=True
    )

# --------------------------------
# MAIN HEADER
# --------------------------------

st.markdown("""
<div class="hero">
    <div class="brand">NxT AI</div>
    <div class="subtitle">
        Next Generation • Private • On-Device Intelligence
    </div>
    <br>
    <span class="status">
        ✦ LOCAL AI ASSISTANT
    </span>
</div>
""", unsafe_allow_html=True)

# --------------------------------
# WELCOME SCREEN
# --------------------------------

if not st.session_state.messages:
    st.markdown(
        '<div class="glass-card">'
        '<h2>Welcome to NxT AI 👋</h2>'
        '<p style="color:#a9c3e8">'
        'Your personal AI assistant running locally on your device.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")
    st.markdown("### ✨ What can I help you with?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💡 Explain Artificial Intelligence",
                     use_container_width=True):
            st.session_state.pending_prompt = (
                "Explain Artificial Intelligence simply."
            )
            st.rerun()

        if st.button("🐍 Help me with Python",
                     use_container_width=True):
            st.session_state.pending_prompt = (
                "Teach me Python programming with examples."
            )
            st.rerun()

    with col2:
        if st.button("🧠 Explain Machine Learning",
                     use_container_width=True):
            st.session_state.pending_prompt = (
                "Explain machine learning with real examples."
            )
            st.rerun()

        if st.button("🚀 Give me project ideas",
                     use_container_width=True):
            st.session_state.pending_prompt = (
                "Suggest some innovative AI project ideas."
            )
            st.rerun()

# --------------------------------
# DISPLAY CHAT
# --------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------
# GENERATE RESPONSE
# --------------------------------

prompt = st.chat_input("Message NxT AI...")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not connected:
            st.error(
                "Ollama is not running or no local model is "
                "available. Start Ollama and download a model."
            )
        else:
            with st.spinner("NxT AI is thinking..."):
                try:
                    chat_messages = [
                        {
                            "role": "system",
                            "content": st.session_state.system_prompt
                        }
                    ] + st.session_state.messages

                    response = requests.post(
                        f"{OLLAMA_URL}/api/chat",
                        json={
                            "model": st.session_state.model,
                            "messages": chat_messages,
                            "stream": False
                        },
                        timeout=300
                    )
                    response.raise_for_status()

                    answer = response.json()["message"]["content"]
                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except requests.RequestException as error:
                    st.error(f"Local AI error: {error}")
