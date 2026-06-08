import streamlit as st
import requests

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Domain Knowledge Co-Pilot",
    page_icon="🤖",
    layout="wide"
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ── Base ── */
.stApp {
    background-color: #F5F7FB;
    font-family: 'Inter', sans-serif;
}

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: white;
    border-right: 1px solid #E5E7EB;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #EFF6FF;
    border: 1px dashed #BFDBFE;
    border-radius: 10px;
    padding: 4px;
}

/* ── Spinner text ── */
[data-testid="stSpinner"] p { color: #2563EB; }

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border-radius: 24px !important;
    border: 1px solid #E5E7EB !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    background: white !important;
}

/* ── Chat message wrapper ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* ── Navbar ── */
.navbar {
    background: white;
    padding: 18px 32px;
    border-radius: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #E5E7EB;
}
.logo {
    font-size: 22px;
    font-weight: 700;
    color: #2563EB;
    display: flex;
    align-items: center;
    gap: 8px;
}
.nav-links {
    color: #6B7280;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    gap: 24px;
}
.nav-badge {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #2563EB;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 20px;
}

/* ── Page heading ── */
.heading {
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 8px;
}
.subheading {
    text-align: center;
    color: #6B7280;
    font-size: 15px;
    margin-bottom: 32px;
    line-height: 1.7;
}

/* ── Chat bubbles ── */
.chat-user {
    background: #2563EB;
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 6px;
    margin-left: 100px;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0px 4px 14px rgba(37,99,235,0.25);
}
.chat-ai {
    background: white;
    color: #111827;
    padding: 16px 18px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 6px;
    margin-right: 100px;
    font-size: 14px;
    line-height: 1.7;
    border: 1px solid #E5E7EB;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.06);
}

/* ── Citation ── */
.citation-box {
    background: #EEF2FF;
    border-left: 4px solid #2563EB;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 20px;
    margin-right: 100px;
    color: #374151;
    font-size: 13px;
    line-height: 1.6;
}

/* ── Sidebar internals ── */
.sidebar-title {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
}
.sidebar-subtitle {
    color: #6B7280;
    font-size: 13px;
    margin-bottom: 14px;
}
.active-doc-card {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 14px;
}
.active-doc-label {
    font-size: 11px;
    font-weight: 600;
    color: #166534;
    margin-bottom: 3px;
}
.active-doc-name {
    font-size: 12px;
    color: #15803D;
    word-break: break-all;
}

/* ── Empty state ── */
.empty-card {
    text-align: center;
    padding: 56px 24px;
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    max-width: 460px;
    margin: 0 auto;
}
.empty-icon { font-size: 48px; margin-bottom: 14px; }
.empty-title { font-size: 16px; font-weight: 600; color: #111827; margin-bottom: 6px; }
.empty-sub   { font-size: 13px; color: #6B7280; line-height: 1.6; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F5F7FB; }
::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

BACKEND = "http://127.0.0.1:8000"

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("""
    <div style="padding:24px 16px 16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;
                    padding-bottom:16px;border-bottom:1px solid #E5E7EB;">
            <span style="font-size:24px;">🤖</span>
            <div>
                <div style="font-size:14px;font-weight:700;color:#111827;">Domain Co-Pilot</div>
                <div style="font-size:11px;color:#6B7280;">Knowledge Assistant</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p class="sidebar-title">📂 Upload Document</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sidebar-subtitle">Upload a PDF and start chatting</p>',
        unsafe_allow_html=True
    )

    # ── File uploader — exact logic from old code ──
    uploaded_file = st.file_uploader(
        "Choose PDF",
        type=["pdf"]
    )

    if uploaded_file:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file,
                "application/pdf"
            )
        }

        with st.spinner("Uploading PDF..."):
            try:
                response = requests.post(
                    f"{BACKEND}/upload-pdf",
                    files=files,
                    timeout=60
                )

                if response.status_code == 200:
                    st.session_state.pdf_uploaded = True
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.messages = []   # fresh chat on new upload
                    st.success("✅ PDF Uploaded Successfully!")
                else:
                    st.error(f"Upload failed — {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("⚠️ Backend not running. Start FastAPI first.")
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")

    # Active doc indicator
    if st.session_state.pdf_uploaded and st.session_state.pdf_name:
        st.markdown(f"""
        <div class="active-doc-card">
            <div class="active-doc-label">✅ Active Document</div>
            <div class="active-doc-name">{st.session_state.pdf_name}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:20px 0;border-color:#E5E7EB;">', unsafe_allow_html=True)

    # Clear chat
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ─── Navbar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="logo">🤖 Domain Knowledge Co-Pilot</div>
    <div class="nav-links">
        <span>Upload</span>
        <span>New Chat</span>
        <span>Logout</span>
        <span class="nav-badge">Free Plan</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Page Title ───────────────────────────────────────────────────────────────
st.markdown(
    '<p class="heading">Talk to Your Documents</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="subheading">Upload PDFs and ask AI-powered questions instantly</p>',
    unsafe_allow_html=True
)

# ─── Empty state ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    if not st.session_state.pdf_uploaded:
        st.markdown("""
        <div class="empty-card">
            <div class="empty-icon">📂</div>
            <div class="empty-title">No document loaded</div>
            <div class="empty-sub">Upload a PDF from the sidebar to get started.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="empty-card">
            <div class="empty-icon">💬</div>
            <div class="empty-title">Ready to answer</div>
            <div class="empty-sub">Ask anything about <strong>{st.session_state.pdf_name}</strong></div>
        </div>
        """, unsafe_allow_html=True)

# ─── Chat Input — exact logic from old code ───────────────────────────────────
question = st.chat_input(
    "Ask something from your document..."
)

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    try:
        response = requests.post(
            f"{BACKEND}/chat",
            json={"question": question},
            timeout=60
        )
        result = response.json()

        st.session_state.messages.append({
       "role": "assistant",
       "content": result.get(
        "answer",
        "No answer found"
        ),
        "citation": result.get(
        "citation",
        result.get("source", "")
        )
    })

    except requests.exceptions.ConnectionError:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ Could not connect to backend. Make sure FastAPI is running on port 8000.",
            "citation": ""
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"⚠️ Unexpected error: {str(e)}",
            "citation": ""
        })

    st.rerun()

# ─── Chat Messages — exact logic from old code ────────────────────────────────
for message in st.session_state.messages:

    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-user">
                👤 <b>You</b><br><br>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""
            <div class="chat-ai">
                🤖 <b>AI Assistant</b><br><br>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        if message.get("citation"):
            st.markdown(
                f"""
                <div class="citation-box">
                    📌 <b>Citation:</b><br>
                    {message["citation"][:400]}
                </div>
                """,
                unsafe_allow_html=True
            )