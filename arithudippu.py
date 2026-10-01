import streamlit as st
import requests
import json
from datetime import datetime

# ==========================================
# NxT AI - ADVANCED OFFLINE AI ASSISTANT
# ==========================================

st.set_page_config(
    page_title="NxT AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"

# ==========================================
# THEMES
# ==========================================

THEMES = {
    "Midnight Blue": {
        "bg": "#071226",
        "bg2": "#101f40",
        "panel": "rgba(19,39,75,0.75)",
        "input": "#172c4c",
        "text": "#f0f6ff",
        "muted": "#b2c5e0",
        "accent": "#38bdf8",
        "border": "rgba(100,180,255,0.28)",
        "user": "rgba(28,92,160,0.40)"
    },
    "AMOLED Black": {
        "bg": "#000000",
        "bg2": "#080b12",
        "panel": "rgba(22,22,28,0.94)",
        "input": "#202028",
        "text": "#ffffff",
        "muted": "#b5b5bd",
        "accent": "#60a5fa",
        "border": "rgba(160,160,180,0.25)",
        "user": "rgba(30,65,115,0.45)"
    },
    "Light Glass": {
        "bg": "#eaf3ff",
        "bg2": "#dbeafe",
        "panel": "rgba(255,255,255,0.85)",
        "input": "#ffffff",
        "text": "#172b4d",
        "muted": "#526781",
        "accent": "#0879cf",
        "border": "rgba(60,110,170,0.25)",
        "user": "rgba(193,224,255,0.85)"
    },
    "Emerald": {
        "bg": "#061c19",
        "bg2": "#0c3029",
        "panel": "rgba(12,55,45,0.82)",
        "input": "#124335",
        "text": "#ecfff8",
        "muted": "#a9d9c9",
        "accent": "#34d399",
        "border": "rgba(70,220,165,0.28)",
        "user": "rgba(17,110,80,0.45)"
    },
    "Sunset": {
        "bg": "#24102b",
        "bg2": "#421d3a",
        "panel": "rgba(73,35,73,0.82)",
        "input": "#51294e",
        "text": "#fff3fa",
        "muted": "#e4bfd7",
        "accent": "#fb9bcb",
        "border": "rgba(250,150,210,0.30)",
        "user": "rgba(135,57,112,0.45)"
    }
}

# ==========================================
# AI CHARACTERS
# ==========================================

CHARACTERS = {
    "Friendly Bro": {
        "name": "Bro",
        "avatar": "😎",
        "prompt": "You are a friendly and supportive AI friend. "
                  "Speak naturally and conversationally."
    },
    "Study Mentor": {
        "name": "Professor",
        "avatar": "🧑‍🏫",
        "prompt": "You are a patient academic mentor. "
                  "Explain topics step by step with examples."
    },
    "Coding Expert": {
        "name": "CodeX",
        "avatar": "👨‍💻",
        "prompt": "You are a software engineering expert. "
                  "Write correct code and explain technical concepts."
    },
    "Creative Writer": {
        "name": "Muse",
        "avatar": "🎨",
        "prompt": "You are a creative writing assistant. "
                  "Help with stories, ideas and original writing."
    },
    "Research Assistant": {
        "name": "Nexus",
        "avatar": "🧠",
        "prompt": "You are a careful research assistant. "
                  "Explain evidence and identify uncertainty."
    },
    "Custom": {
        "name": "NxT",
        "avatar": "🤖",
        "prompt": "You are a helpful and adaptable AI assistant."
    }
}

# ==========================================
# SESSION STATE
# ==========================================

if "chats" not in st.session_state:
    st.session_state.chats = [{
        "id": 1,
        "title": "New conversation",
        "messages": [],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }]

if "active_chat" not in st.session_state:
    st.session_state.active_chat = 1

if "next_chat_id" not in st.session_state:
    st.session_state.next_chat_id = 2

if "theme" not in st.session_state:
    st.session_state.theme = "Midnight Blue"

if "character" not in st.session_state:
    st.session_state.character = "Friendly Bro"

if "character_name" not in st.session_state:
    st.session_state.character_name = "Bro"

if "avatar" not in st.session_state:
    st.session_state.avatar = "😎"

if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = ""

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "model" not in st.session_state:
    st.session_state.model = DEFAULT_MODEL

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_active_chat():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat:
            return chat
    return st.session_state.chats[0]


def create_new_chat():
    chat_id = st.session_state.next_chat_id
    st.session_state.next_chat_id += 1

    st.session_state.chats.insert(0, {
        "id": chat_id,
        "title": "New conversation",
        "messages": [],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    st.session_state.active_chat = chat_id


@st.cache_data(ttl=10)
def get_ollama_models():
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=3
        )
        response.raise_for_status()

        return [
            model["name"]
            for model in response.json().get("models", [])
        ]

    except requests.RequestException:
        return []


def build_system_prompt():
    preset = CHARACTERS[st.session_state.character]

    personality = st.session_state.custom_prompt.strip()

    if not personality:
        personality = preset["prompt"]

    styles = {
        "Friendly": "Use a friendly and approachable tone.",
        "Professional": "Use a professional and formal tone.",
        "Casual": "Use a casual and natural tone.",
        "Academic": "Use an academic and structured tone.",
        "Creative": "Use an imaginative and expressive tone."
    }

    details = {
        "Short": "Keep answers concise and brief.",
        "Balanced": "Give moderately detailed answers.",
        "Detailed": "Give thorough answers with examples where useful."
    }

    return (
        f"You are {st.session_state.character_name}, "
        f"an AI assistant. {personality}\n"
        f"{styles[st.session_state.response_style]}\n"
        f"{details[st.session_state.answer_detail]}\n"
        "Be accurate. If you are unsure, say so. "
        "Do not claim to have internet access."
    )


def generate_response(messages):
    system_prompt = build_system_prompt()

    payload = {
        "model": st.session_state.model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            }
        ] + messages,
        "stream": False,
        "options": {
            "temperature": st.session_state.temperature
        }
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def apply_theme(theme):
    t = THEMES[theme]

    is_light = theme == "Light Glass"
    color_scheme = "light" if is_light else "dark"

    return f"""
    <style>
    :root {{
        color-scheme: {color_scheme};
    }}

    .stApp {{
        background:
            radial-gradient(
                ellipse at 8% 8%,
                {t["accent"]}22,
                transparent 38%
            ),
            radial-gradient(
                ellipse at 92% 80%,
                {t["accent"]}18,
                transparent 36%
            ),
            linear-gradient(
                135deg,
                {t["bg"]},
                {t["bg2"]}
            );
        color: {t["text"]} !important;
    }}

    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        max-width: 1150px;
        padding-top: 1.7rem;
        padding-bottom: 4rem;
    }}

    section[data-testid="stSidebar"] {{
        background: {t["panel"]};
        border-right: 1px solid {t["border"]};
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent;
    }}

    /* TEXT VISIBILITY FIX */

    .stApp p,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp span,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {{
        color: {t["text"]};
    }}

    .stApp [data-testid="stCaptionContainer"],
    .stApp small {{
        color: {t["muted"]} !important;
    }}

    /* INPUTS */

    .stApp input,
    .stApp textarea,
    .stApp [data-testid="stChatInput"] textarea {{
        color: {t["text"]} !important;
        -webkit-text-fill-color: {t["text"]} !important;
        background-color: {t["input"]} !important;
        caret-color: {t["accent"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 12px !important;
    }}

    .stApp input::placeholder,
    .stApp textarea::placeholder,
    .stApp [data-testid="stChatInput"] textarea::placeholder {{
        color: {t["muted"]} !important;
        -webkit-text-fill-color: {t["muted"]} !important;
        opacity: 1 !important;
    }}

    /* SELECTBOX */

    .stApp [data-baseweb="select"] > div {{
        color: {t["text"]} !important;
        background: {t["input"]} !important;
        border-color: {t["border"]} !important;
    }}

    .stApp [data-baseweb="select"] * {{
        color: {t["text"]} !important;
    }}

    [data-baseweb="popover"],
    [role="listbox"],
    [role="option"] {{
        background: {t["input"]} !important;
        color: {t["text"]} !important;
    }}

    /* BUTTONS */

    .stApp .stButton > button,
    .stApp .stDownloadButton > button {{
        background: {t["panel"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 13px !important;
        transition: all .2s ease;
    }}

    .stApp .stButton > button:hover,
    .stApp .stDownloadButton > button:hover {{
        border-color: {t["accent"]} !important;
        box-shadow: 0 0 18px {t["accent"]}40;
        transform: translateY(-1px);
    }}

    /* CHAT */

    [data-testid="stChatMessage"] {{
        background: {t["panel"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 18px !important;
        padding: 14px !important;
        margin-bottom: 12px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }}

    [data-testid="stChatInput"] {{
        background: {t["input"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 18px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {t["text"]} !important;
        -webkit-text-fill-color: {t["text"]} !important;
    }}

    [data-testid="stChatInput"] button {{
        color: {t["accent"]} !important;
    }}

    /* GLASS PANELS */

    .hero {{
        background: {t["panel"]};
        border: 1px solid {t["border"]};
        border-radius: 25px;
        padding: 27px;
        margin-bottom: 22px;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        box-shadow: 0 12px 40px rgba(0,0,0,.16);
    }}

    .glass-card {{
        background: {t["panel"]};
        border: 1px solid {t["border"]};
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        margin-bottom: 12px;
    }}

    .brand {{
        color: {t["accent"]} !important;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: 1px;
    }}

    .muted {{
        color: {t["muted"]} !important;
    }}

    .status {{
        display: inline-block;
        color: #10b981;
        background: rgba(16,185,129,.10);
        border: 1px solid rgba(16,185,129,.35);
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
    }}

    hr {{
        border-color: {t["border"]} !important;
    }}
    </style>
    """


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown(
        '<div class="brand">✦ NxT AI</div>',
        unsafe_allow_html=True
    )

    st.caption("ON-DEVICE INTELLIGENCE")

    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("### 💬 Chat History")

    for chat in st.session_state.chats:
        active = chat["id"] == st.session_state.active_chat
        prefix = "🔵 " if active else "💬 "

        col1, col2 = st.columns([5, 1])

        with col1:
            if st.button(
                prefix + chat["title"][:22],
                key=f"select_{chat['id']}",
                use_container_width=True
            ):
                st.session_state.active_chat = chat["id"]
                st.rerun()

        with col2:
            if st.button(
                "×",
                key=f"delete_{chat['id']}"
            ):
                if len(st.session_state.chats) > 1:
                    st.session_state.chats = [
                        c for c in st.session_state.chats
                        if c["id"] != chat["id"]
                    ]

                    if st.session_state.active_chat == chat["id"]:
                        st.session_state.active_chat = (
                            st.session_state.chats[0]["id"]
                        )

                    st.rerun()
                else:
                    st.session_state.chats[0]["messages"] = []
                    st.session_state.chats[0]["title"] = (
                        "New conversation"
                    )
                    st.rerun()

    st.divider()

    st.markdown("### 🎨 Appearance")

    st.session_state.theme = st.selectbox(
        "Choose theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(
            st.session_state.theme
        )
    )

    st.divider()

    st.markdown("### 🧑‍🚀 AI Character")

    st.session_state.character = st.selectbox(
        "Personality",
        list(CHARACTERS.keys()),
        index=list(CHARACTERS.keys()).index(
            st.session_state.character
        )
    )

    preset = CHARACTERS[st.session_state.character]

    avatar_options = [
        "🤖", "😎", "🧑‍🏫", "👨‍💻", "🎨",
        "🧠", "👽", "🦊", "🐼", "🚀", "🌟"
    ]

    default_avatar = preset["avatar"]

    if "avatar" not in st.session_state:
        st.session_state.avatar = default_avatar

    if st.session_state.character != "Custom":
        st.session_state.character_name = preset["name"]
        st.session_state.avatar = default_avatar

    st.session_state.avatar = st.selectbox(
        "Avatar",
        avatar_options,
        index=(
            avatar_options.index(st.session_state.avatar)
            if st.session_state.avatar in avatar_options
            else 0
        )
    )

    st.session_state.character_name = st.text_input(
        "Character name",
        value=st.session_state.character_name,
        max_chars=30
    )

    st.session_state.custom_prompt = st.text_area(
        "Custom personality",
        value=st.session_state.custom_prompt,
        placeholder="Describe your AI character...",
        height=100
    )

    st.session_state.response_style = st.selectbox(
        "Response tone",
        ["Friendly", "Professional", "Casual",
         "Academic", "Creative"]
    )

    st.session_state.answer_detail = st.select_slider(
        "Answer length",
        options=["Short", "Balanced", "Detailed"],
        value="Balanced"
    )

    st.divider()

    st.markdown("### 🧠 Local AI")

    models = get_ollama_models()

    if models:
        current_model = st.session_state.model
        model_index = (
            models.index(current_model)
            if current_model in models else 0
        )

        st.session_state.model = st.selectbox(
            "AI model",
            models,
            index=model_index
        )

        st.markdown(
            '<div class="status">● Ollama Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Ollama not connected")
        st.caption("Default model: " + DEFAULT_MODEL)

    if st.button("↻ Refresh Connection",
                 use_container_width=True):
        get_ollama_models.clear()
        st.rerun()

    st.session_state.temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    st.divider()

    current_chat = get_active_chat()

    if current_chat["messages"]:
        export_data = json.dumps(
            current_chat["messages"],
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            "⬇ Export Chat",
            data=export_data,
            file_name="nxt_ai_chat.json",
            mime="application/json",
            use_container_width=True
        )

    if st.button("🗑 Clear Current Chat",
                 use_container_width=True):
        current_chat["messages"] = []
        current_chat["title"] = "New conversation"
        st.rerun()

    st.divider()

    st.caption("NxT AI • Offline Intelligence")


# ==========================================
# APPLY THEME
# ==========================================

st.markdown(
    apply_theme(st.session_state.theme),
    unsafe_allow_html=True
)

# ==========================================
# MAIN HEADER
# ==========================================

avatar = st.session_state.avatar
char_name = st.session_state.character_name

st.markdown(f"""
<div class="hero">
    <div class="brand">✦ NxT AI</div>
    <p class="muted">
        Next Generation • Private • On-Device Intelligence
    </p>
    <span class="status">
        ✦ LOCAL AI ASSISTANT
    </span>
    <br><br>
    <p class="muted">
        {avatar} Your assistant: {char_name}
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# ACTIVE CHAT
# ==========================================

chat = get_active_chat()
messages = chat["messages"]

if not messages:
    st.markdown(
        f"""
        <div class="glass-card">
            <h2>Welcome to NxT AI 👋</h2>
            <p class="muted">
                Hello! I'm {char_name}. How can I help you today?
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### ✨ Quick prompts")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "💡 Explain Artificial Intelligence",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Explain Artificial Intelligence simply."
            )
            st.rerun()

        if st.button(
            "🐍 Help me learn Python",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Teach me Python programming with examples."
            )
            st.rerun()

    with col2:
        if st.button(
            "🧠 Explain Machine Learning",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Explain machine learning with real-world examples."
            )
            st.rerun()

        if st.button(
            "🚀 Suggest AI projects",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Suggest innovative AI project ideas."
            )
            st.rerun()

# ==========================================
# DISPLAY EXISTING MESSAGES
# ==========================================

for msg in messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(msg["con
