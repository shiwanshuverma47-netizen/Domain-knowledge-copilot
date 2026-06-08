import streamlit as st
import requests

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Domain Knowledge Co-Pilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:       #0d0f0e;
  --surface:  #131614;
  --border:   #1e2320;
  --border2:  #2a2f2b;
  --accent:   #b8f5a0;
  --accent2:  #7de87a;
  --muted:    #4a5248;
  --text:     #dce8d8;
  --text-dim: #8a9e85;
  --danger:   #f4826a;
  --info:     #7ab8f5;
  --tag-bg:   #1a2218;
  --user-bubble: #1a2e1a;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif;
  color: var(--text);
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 6px !important;
  color: var(--text) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent) !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--text-dim) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 12px !important;
  border-radius: 4px !important;
  transition: all 0.15s ease !important;
}
[data-testid="stButton"] > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: rgba(184,245,160,0.05) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--surface) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 8px !important;
}
[data-testid="stFileUploader"] label { color: var(--text-dim) !important; }
[data-testid="stFileUploader"] section { background: transparent !important; }
[data-testid="stFileUploader"] button {
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--text-dim) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 11px !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
}
[data-testid="stChatInput"] textarea {
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* ── Success / Error / Warning ── */
[data-testid="stAlert"] {
  border-radius: 6px !important;
  font-size: 13px !important;
  font-family: 'DM Mono', monospace !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

hr { border-color: var(--border) !important; opacity: 1 !important; }
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
    <div style="padding: 28px 20px 20px;">
        <div style="font-family:'DM Mono',monospace;color:var(--accent);font-size:10px;letter-spacing:3px;margin-bottom:8px;">◈ KNOWLEDGE OS</div>
        <div style="font-family:'Fraunces',serif;font-size:22px;font-weight:300;color:var(--text);line-height:1.2;">Domain Knowledge<br><em>Co-Pilot</em></div>
    </div>
    <hr style="margin:0 0 20px;">
    """, unsafe_allow_html=True)

    # Upload section
    st.markdown("""
    <div style="padding:0 20px 10px;font-family:'DM Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:2px;">
        UPLOAD DOCUMENT
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        label_visibility="collapsed",
        key="file_uploader"
    )

    if uploaded_file is not None:
        if st.button("⬆  Process & Index", use_container_width=True, key="upload_btn"):
            with st.spinner("Uploading and indexing…"):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file,
                            "application/pdf"
                        )
                    }
                    response = requests.post(
                        f"{BACKEND}/upload-pdf",
                        files=files,
                        timeout=60
                    )
                    if response.status_code == 200:
                        st.session_state.pdf_uploaded = True
                        st.session_state.pdf_name = uploaded_file.name
                        st.session_state.messages = []   # fresh chat on new upload
                        st.success("PDF indexed successfully!")
                    else:
                        st.error(f"Upload failed — {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("Backend not running. Start FastAPI first.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Active doc indicator
    if st.session_state.pdf_uploaded and st.session_state.pdf_name:
        st.markdown(f"""
        <div style="margin:16px 20px 0;padding:10px 14px;background:rgba(184,245,160,0.06);
                    border:1px solid var(--border);border-left:2px solid var(--accent);border-radius:6px;">
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:var(--accent);margin-bottom:4px;">ACTIVE DOCUMENT</div>
            <div style="font-size:12px;color:var(--text);word-break:break-all;">{st.session_state.pdf_name}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:20px 0;">', unsafe_allow_html=True)

    # Clear chat
    if st.session_state.messages:
        if st.button("✕  Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

# ─── Main Area ───────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div style="padding: 32px 0 8px;">
    <div style="font-family:'DM Mono',monospace;color:var(--muted);font-size:10px;letter-spacing:3px;margin-bottom:10px;">MODULE 6 · IIT ROORKEE · CAPSTONE</div>
    <div style="font-family:'Fraunces',serif;font-size:38px;font-weight:300;color:var(--text);line-height:1.15;">
        Talk to Your<br><em style="color:var(--accent);">Documents.</em>
    </div>
    <div style="color:var(--text-dim);font-size:13px;margin-top:10px;max-width:500px;line-height:1.7;">
        Upload a PDF and ask questions in plain English.
        Every answer comes with a citation linking back to the exact source passage.
    </div>
</div>
<hr style="margin: 24px 0;">
""", unsafe_allow_html=True)

# ── Empty state ──
if not st.session_state.messages:
    if not st.session_state.pdf_uploaded:
        st.markdown("""
        <div style="text-align:center;padding:60px 24px;color:var(--text-dim);">
            <div style="font-size:40px;opacity:0.2;margin-bottom:16px;">◈</div>
            <div style="font-size:15px;margin-bottom:6px;color:var(--text);">No document loaded</div>
            <div style="font-size:13px;">Upload a PDF from the sidebar to get started.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:60px 24px;color:var(--text-dim);">
            <div style="font-size:40px;opacity:0.2;margin-bottom:16px;">◈</div>
            <div style="font-size:15px;margin-bottom:6px;color:var(--text);">Ready to answer</div>
            <div style="font-size:13px;">Ask anything about <em style="color:var(--text);">{st.session_state.pdf_name}</em></div>
        </div>
        """, unsafe_allow_html=True)

# ── Render existing messages ──
for message in st.session_state.messages:

    if message["role"] == "user":
        with st.chat_message("user", avatar="○"):
            st.markdown(f"""
            <div style="background:var(--user-bubble);border:1px solid var(--border2);
                        border-radius:8px;padding:14px 16px;font-size:14px;line-height:1.6;
                        color:var(--text);">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

    else:
        with st.chat_message("assistant", avatar="◈"):
            # Answer
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:8px;padding:16px;font-size:14px;line-height:1.7;
                        color:var(--text);margin-bottom:10px;">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

            # Citation
            if message.get("citation"):
                citation_text = message["citation"][:400]
                st.markdown(f"""
                <div style="background:var(--tag-bg);border:1px solid var(--border);
                            border-left:3px solid var(--accent);border-radius:6px;
                            padding:12px 14px;margin-top:4px;">
                    <div style="font-family:'DM Mono',monospace;font-size:9px;color:var(--accent);
                                letter-spacing:2px;margin-bottom:6px;">CITATION</div>
                    <div style="font-size:12px;color:var(--text-dim);line-height:1.6;font-style:italic;">
                        {citation_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── Chat input ──
question = st.chat_input(
    "Ask something from your document…",
    disabled=not st.session_state.pdf_uploaded
)

if question:
    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Call backend
    with st.spinner("Retrieving and generating answer…"):
        try:
            response = requests.post(
                f"{BACKEND}/chat",
                json={"question": question},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.get("answer", "No answer returned."),
                    "citation": result.get("citation", "")
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Backend returned error {response.status_code}.",
                    "citation": ""
                })

        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠ Could not connect to backend. Make sure FastAPI is running on port 8000.",
                "citation": ""
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠ Unexpected error: {str(e)}",
                "citation": ""
            })

    st.rerun()