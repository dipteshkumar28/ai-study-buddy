import os
import copy
from utils import DEFAULTS, MULTI_DOC_PROMPT, REVISION_NOTES_PROMPT, SUMMARY_PROMPT, FLASHCARD_PROMPT, QUIZ_PROMPT, ADAPTIVE_QUIZ_PROMPT,CHAT_PROMPT, EXPLAIN_PROMPT, VOICE_TUTOR_PROMPT, MULTI_DOC_PROMPT
import streamlit as st
import json
import random
import time
import re
import io
import hashlib
from pathlib import Path
from datetime import date

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #13161e;
    --surface2:  #1a1d27;
    --border:    #232736;
    --border2:   #2e3248;
    --accent:    #7c6aff;
    --accent2:   #ff6ab0;
    --accent3:   #6affe0;
    --accent4:   #ffd166;
    --text:      #e8eaf0;
    --muted:     #7a7f96;
    --success:   #4ade80;
    --warning:   #facc15;
    --danger:    #f87171;
    --xp-color:  #ffd166;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'Syne', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3 { font-family: 'Syne', sans-serif; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #1a1233 0%, #0d0f14 60%, #0f1a1a 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(124,106,255,.25) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -40px; left: 200px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(106,255,224,.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #f472b6, #6affe0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0;
}
.hero p { color: var(--muted); font-size: 1rem; margin: 0; }

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    transition: border-color .2s;
}
.card:hover { border-color: var(--accent); }
.card-sm { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 12px; }

/* Section label */
.section-label {
    font-size: .7rem; font-weight: 700;
    letter-spacing: .15em; color: var(--accent);
    text-transform: uppercase; margin-bottom: 8px;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 12px; border: 1px solid var(--border);
    padding: 4px; gap: 4px;
}
[data-baseweb="tab"] {
    background: transparent !important; border-radius: 8px !important;
    color: var(--muted) !important; font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; font-size: .85rem !important;
    padding: 8px 18px !important; border: none !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: var(--accent) !important; color: white !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent); color: white; border: none;
    border-radius: 10px; font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: .85rem; padding: 10px 24px;
    transition: opacity .15s, transform .1s; width: 100%;
}
.stButton > button:hover { opacity: .88; transform: translateY(-1px); }
.stButton > button:active { transform: translateY(0); }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #1a1d27 !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,106,255,.2) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1a1d27; border: 1.5px dashed var(--border);
    border-radius: 14px; padding: 16px; transition: border-color .2s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent); }

/* Progress */
.stProgress > div > div { background: var(--accent) !important; }

/* Metric */
[data-testid="metric-container"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px;
}

/* Flashcard */
.flashcard { perspective: 1000px; width: 100%; min-height: 220px; cursor: pointer; margin-bottom: 20px; }
.flashcard-inner { position: relative; width: 100%; min-height: 220px; transition: transform .6s cubic-bezier(.4,0,.2,1); transform-style: preserve-3d; }
.flashcard.flipped .flashcard-inner { transform: rotateY(180deg); }
.flashcard-front, .flashcard-back {
    position: absolute; width: 100%; min-height: 220px; backface-visibility: hidden;
    border-radius: 18px; display: flex; flex-direction: column;
    align-items: center; justify-content: center; padding: 32px; text-align: center;
}
.flashcard-front { background: linear-gradient(135deg, #1a1233, #1c1a35); border: 1px solid var(--accent); }
.flashcard-back { background: linear-gradient(135deg, #0f1f1a, #121f1a); border: 1px solid var(--accent3); transform: rotateY(180deg); }
.flashcard-label { font-size: .65rem; letter-spacing: .15em; font-weight: 700; text-transform: uppercase; margin-bottom: 16px; opacity: .6; }
.flashcard-text { font-size: 1.1rem; font-weight: 600; line-height: 1.5; }

/* Quiz */
.quiz-option { background: #1a1d27; border: 1px solid var(--border); border-radius: 12px; padding: 14px 20px; margin-bottom: 10px; cursor: pointer; transition: all .2s; font-size: .9rem; }
.quiz-option:hover { border-color: var(--accent); background: #1f2235; }
.quiz-option.correct { border-color: var(--success) !important; background: rgba(74,222,128,.1) !important; color: var(--success); }
.quiz-option.wrong { border-color: var(--danger) !important; background: rgba(248,113,113,.1) !important; color: var(--danger); }

/* Summary */
.summary-box { background: #1a1d27; border-left: 3px solid var(--accent); border-radius: 0 14px 14px 0; padding: 24px; font-family: 'DM Mono', monospace; font-size: .88rem; line-height: 1.8; white-space: pre-wrap; }

/* Badge */
.badge { display: inline-block; background: rgba(124,106,255,.15); border: 1px solid rgba(124,106,255,.3); color: var(--accent); border-radius: 20px; padding: 3px 12px; font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; margin-right: 6px; }
.badge.green { background: rgba(74,222,128,.1); border-color: rgba(74,222,128,.3); color: var(--success); }
.badge.pink  { background: rgba(244,114,182,.1); border-color: rgba(244,114,182,.3); color: var(--accent2); }
.badge.gold  { background: rgba(255,209,102,.1); border-color: rgba(255,209,102,.3); color: var(--xp-color); }
.badge.cyan  { background: rgba(106,255,224,.1); border-color: rgba(106,255,224,.3); color: var(--accent3); }

/* Score ring */
.score-ring { display: flex; align-items: center; justify-content: center; gap: 24px; padding: 24px; }
.ring-container { text-align: center; }
.ring-number { font-size: 3rem; font-weight: 800; color: var(--accent3); }
.ring-label { font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .1em; }

/* XP Bar */
.xp-bar-container { background: var(--border); border-radius: 8px; height: 8px; margin: 8px 0; overflow: hidden; }
.xp-bar-fill { height: 100%; border-radius: 8px; background: linear-gradient(90deg, var(--accent), var(--accent3)); transition: width .6s ease; }

/* Level badge */
.level-badge {
    background: linear-gradient(135deg, #1a1233, #1c2035);
    border: 2px solid var(--accent);
    border-radius: 16px; padding: 16px;
    text-align: center; margin-bottom: 12px;
}
.level-number { font-size: 2rem; font-weight: 800; color: var(--xp-color); }
.level-title { font-size: .7rem; color: var(--muted); text-transform: uppercase; letter-spacing: .1em; }

/* Study mode timer */
.timer-display {
    font-family: 'DM Mono', monospace;
    font-size: 3.5rem; font-weight: 500;
    text-align: center; padding: 32px;
    background: linear-gradient(135deg, #1a1233, #0f1a1a);
    border-radius: 20px; border: 1px solid var(--border);
    margin: 16px 0;
}
.timer-display.work { color: var(--accent3); border-color: var(--accent3); }
.timer-display.break { color: var(--accent2); border-color: var(--accent2); }

/* Progress chart bar */
.prog-bar-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.prog-bar-label { width: 120px; font-size: .78rem; color: var(--muted); }
.prog-bar-track { flex: 1; background: var(--border); border-radius: 6px; height: 10px; overflow: hidden; }
.prog-bar-value { height: 100%; border-radius: 6px; }
.prog-bar-pct { width: 40px; font-size: .78rem; text-align: right; color: var(--text); font-family: 'DM Mono', monospace; }

/* Doc chip */
.doc-chip {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(124,106,255,.1); border: 1px solid rgba(124,106,255,.3);
    border-radius: 20px; padding: 4px 12px; margin: 4px;
    font-size: .78rem; color: var(--accent);
}
.doc-chip.active { background: var(--accent); color: white; border-color: var(--accent); }

/* Revision note */
.note-item { background: #1a1d27; border-left: 3px solid var(--accent4); border-radius: 0 10px 10px 0; padding: 14px 18px; margin-bottom: 10px; font-size: .87rem; line-height: 1.6; }

/* Achievement popup */
.achievement { background: linear-gradient(135deg, #1a1233, #1a1f10); border: 1px solid var(--xp-color); border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; display: flex; align-items: center; gap: 14px; }
.achievement-icon { font-size: 2rem; }
.achievement-name { font-weight: 700; font-size: .9rem; color: var(--xp-color); }
.achievement-desc { font-size: .75rem; color: var(--muted); margin-top: 2px; }

/* Explain mode selector */
.explain-mode { background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 12px; cursor: pointer; transition: all .2s; }
.explain-mode:hover { border-color: var(--accent); }
.explain-mode.selected { border-color: var(--accent3); background: rgba(106,255,224,.05); }
.explain-mode-icon { font-size: 1.4rem; margin-bottom: 6px; }
.explain-mode-name { font-weight: 700; font-size: .88rem; }
.explain-mode-desc { font-size: .75rem; color: var(--muted); margin-top: 3px; }

/* Weak area tag */
.weak-tag { display: inline-block; background: rgba(248,113,113,.1); border: 1px solid rgba(248,113,113,.3); color: var(--danger); border-radius: 20px; padding: 3px 10px; font-size: .72rem; margin: 3px; }
.strong-tag { display: inline-block; background: rgba(74,222,128,.1); border: 1px solid rgba(74,222,128,.3); color: var(--success); border-radius: 20px; padding: 3px 10px; font-size: .72rem; margin: 3px; }

/* Spinner */
.stSpinner > div { border-color: var(--accent) transparent transparent !important; }

/* Streak */
.streak-fire { font-size: 2rem; }
.streak-num { font-size: 1.8rem; font-weight: 800; color: var(--xp-color); }

/* Radio */
[data-testid="stRadio"] label { color: var(--text) !important; font-size: .9rem; }

/* ─── Login / Auth ─── */
.login-container {
    max-width: 460px; margin: 60px auto 0; padding: 40px;
    background: linear-gradient(135deg, #13161e, #1a1d27);
    border: 1px solid var(--border); border-radius: 24px;
}
.login-title {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #6affe0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 6px;
}
.login-sub { color: var(--muted); text-align: center; font-size: .88rem; margin-bottom: 28px; }
.user-avatar {
    width: 48px; height: 48px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 800; color: white;
    margin-right: 10px; vertical-align: middle;
}
.user-info-bar {
    display: flex; align-items: center;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 14px; padding: 10px 16px; margin-bottom: 12px;
}
.user-name { font-weight: 700; font-size: .95rem; }
.user-email { font-size: .72rem; color: var(--muted); }

/* ─── Voice Tutor ─── */
.voice-card {
    background: linear-gradient(135deg, #1a1233, #0f1a1a);
    border: 1px solid var(--accent); border-radius: 20px;
    padding: 32px; text-align: center; margin-bottom: 20px;
}
.voice-icon {
    font-size: 4rem; margin-bottom: 12px;
    animation: pulse 2s infinite;
}
.voice-icon.listening { animation: pulse-fast .6s infinite; color: var(--accent2); }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.7;transform:scale(1.05)} }
@keyframes pulse-fast { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.6;transform:scale(1.15)} }
.voice-status { font-size: .85rem; color: var(--muted); margin-top: 8px; letter-spacing: .05em; }
.transcript-box {
    background: #1a1d27; border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; font-size: .9rem;
    line-height: 1.7; min-height: 80px; margin-top: 16px;
    font-family: 'DM Mono', monospace;
}
.voice-answer {
    background: linear-gradient(135deg, rgba(124,106,255,.08), rgba(106,255,224,.05));
    border: 1px solid rgba(124,106,255,.3);
    border-radius: 14px; padding: 20px; font-size: .9rem;
    line-height: 1.7; margin-top: 16px;
}

/* ─── Streaming answer ─── */
.stream-box {
    background: #1a1d27; border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; font-size: .9rem;
    line-height: 1.8; font-family: 'DM Mono', monospace;
    min-height: 60px; white-space: pre-wrap;
}
.stream-cursor {
    display: inline-block; width: 2px; height: 1em;
    background: var(--accent3); margin-left: 2px;
    animation: blink .7s step-end infinite; vertical-align: text-bottom;
}
@keyframes blink { 50%{ opacity:0 } }

/* ─── User Dashboard ─── */
.dashboard-hero {
    background: linear-gradient(135deg, #12102a 0%, #0d1a18 100%);
    border: 1px solid var(--border); border-radius: 20px;
    padding: 28px 32px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 24px;
}
.dash-avatar {
    width: 72px; height: 72px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; font-weight: 800; color: white; flex-shrink: 0;
    border: 3px solid var(--accent);
}
.dash-name { font-size: 1.5rem; font-weight: 800; }
.dash-meta { color: var(--muted); font-size: .83rem; margin-top: 4px; }
.stat-pill {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 12px; padding: 12px 18px; text-align: center;
}
.stat-pill-num { font-size: 1.6rem; font-weight: 800; color: var(--accent3); }
.stat-pill-label { font-size: .68rem; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Deps ──────────────────────────────────────────────────────────────────────
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    import pdfplumber
    DEPS_OK = True
except ImportError as e:
    DEPS_OK = False
    MISSING = str(e)

# ══════════════════════════════════════════════════════════════════════════════
# SIMPLE USER STORE  (file-based, no DB needed — swap for real DB in prod)
# ══════════════════════════════════════════════════════════════════════════════
PROFILE_FILE = Path("study_profile.json")   # local progress file - no accounts
PERSIST = os.getenv("PERSIST_PROGRESS", "1") == "1"

def _load_profile() -> dict:
    if PERSIST and PROFILE_FILE.exists():
        try:
            return json.loads(PROFILE_FILE.read_text())
        except Exception:
            return {}
    return {}

def auth_save_profile(_username, profile_data: dict):
    """Kept under the old name so existing calls work; saves locally, no login."""
    if not PERSIST:
        return
    data = _load_profile()
    data.setdefault("created", date.today().isoformat())
    data.update(profile_data)
    PROFILE_FILE.write_text(json.dumps(data, indent=2))

# ── Session state ─────────────────────────────────────────────────────────────

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = copy.deepcopy(v)
if not st.session_state.get("_profile_loaded"):
    for k, v in _load_profile().items():
        if k in DEFAULTS and k not in ("api_key", "model"):
            st.session_state[k] = v
    st.session_state["_profile_loaded"] = True

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_llm(temperature=0.4):
    key = st.session_state.api_key.strip()
    if not key:
        return None
    os.environ["GROQ_API_KEY"], os.environ["GROQ_MODEL"] = key, st.session_state.model
    return ChatGroq(model=st.session_state.model, api_key=key, temperature=temperature)

@st.cache_resource
def get_agent():
    from agent import build_graph
    return build_graph()

def extract_text_from_file(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

def chunk_text(text: str, max_chars=12000) -> str:
    return text[:max_chars]

def run_chain(template: str, variables: dict) -> str:
    llm = get_llm()
    if llm is None:
        return "⚠️ Please enter your Groq API key in the sidebar first."
    prompt = PromptTemplate(input_variables=list(variables.keys()), template=template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(variables)

def run_chain_streaming(template: str, variables: dict, placeholder):
    """Stream tokens into a Streamlit placeholder in real-time."""
    llm = get_llm()
    if llm is None:
        placeholder.markdown("⚠️ Please enter your Groq API key in the sidebar first.")
        return "⚠️ Please enter your Groq API key in the sidebar first."
    prompt = PromptTemplate(input_variables=list(variables.keys()), template=template)
    chain = prompt | llm | StrOutputParser()
    full_text = ""
    for chunk in chain.stream(variables):
        full_text += chunk
        placeholder.markdown(
            f'<div class="stream-box">{full_text}<span class="stream-cursor"></span></div>',
            unsafe_allow_html=True
        )
    placeholder.markdown(
        f'<div class="stream-box">{full_text}</div>',
        unsafe_allow_html=True
    )
    return full_text

def parse_json_block(text: str):
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    for char in ["[", "{"]:
        idx = text.find(char)
        if idx != -1:
            try:
                return json.loads(text[idx:])
            except Exception:
                pass
    return None

def get_active_text() -> str:
    if st.session_state.active_doc and st.session_state.active_doc in st.session_state.documents:
        return st.session_state.documents[st.session_state.active_doc]
    return st.session_state.extracted_text

def award_xp(amount: int, reason: str = ""):
    st.session_state.xp += amount
    new_level = 1 + st.session_state.xp // 200
    if new_level > st.session_state.level:
        st.session_state.level = new_level
        st.toast(f"🎉 Level Up! You reached Level {new_level}!", icon="🏆")
    # Persist to user profile
    if st.session_state.logged_in and st.session_state.username:
        auth_save_profile(st.session_state.username, {
            "xp": st.session_state.xp,
            "level": st.session_state.level,
        })

def check_achievements():
    earned = st.session_state.achievements
    new_ones = []
    checks = [
        ("first_quiz", "🎯 First Quiz", "Completed your first quiz", st.session_state.total_quizzes >= 1),
        ("quiz_master", "🏆 Quiz Master", "Completed 10 quizzes", st.session_state.total_quizzes >= 10),
        ("flashcard_fan", "🃏 Flashcard Fan", "Viewed 50 flashcards", st.session_state.total_flashcards_viewed >= 50),
        ("perfect_score", "💯 Perfect Score", "Got 100% on a quiz", any(h.get("score_pct", 0) == 100 for h in st.session_state.quiz_history)),
        ("streak_3", "🔥 3-Day Streak", "Studied 3 days in a row", st.session_state.streak >= 3),
        ("level_5", "⭐ Scholar", "Reached Level 5", st.session_state.level >= 5),
        ("multi_doc", "📚 Researcher", "Uploaded 3+ documents", len(st.session_state.documents) >= 3),
        ("note_taker", "📝 Note Taker", "Saved 5 revision notes", len(st.session_state.revision_notes) >= 5),
        ("voice_user", "🎤 Voice Learner", "Used Voice AI Tutor", len(st.session_state.voice_history) >= 1),
    ]
    for key, name, desc, condition in checks:
        if condition and key not in earned:
            st.session_state.achievements.append(key)
            new_ones.append((name, desc))
    if st.session_state.logged_in and st.session_state.username:
        auth_save_profile(st.session_state.username, {"achievements": st.session_state.achievements})
    return new_ones

def update_streak():
    today = date.today().isoformat()
    last = st.session_state.last_study_date
    if last == today:
        return
    if last:
        from datetime import date as d
        last_d = d.fromisoformat(last)
        today_d = d.fromisoformat(today)
        if (today_d - last_d).days == 1:
            st.session_state.streak += 1
        elif (today_d - last_d).days > 1:
            st.session_state.streak = 1
    else:
        st.session_state.streak = 1
    st.session_state.last_study_date = today
    if st.session_state.logged_in and st.session_state.username:
        auth_save_profile(st.session_state.username, {"streak": st.session_state.streak})


# ────────────────────────────────────────────────────────────────────────────
# SIDEBAR  (only shown when logged in)
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # User info bar
    initials = st.session_state.username[:2].upper()
    st.markdown(f"""
    <div class="user-info-bar">
        <div class="user-avatar">{initials}</div>
        <div>
            <div class="user-name">{st.session_state.username}</div>
            <div class="user-email">{st.session_state.user_email}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # XP / Level display
    xp_in_level = st.session_state.xp % 200
    xp_pct = xp_in_level / 200 * 100
    level_names = {1:"Novice",2:"Learner",3:"Student",4:"Scholar",5:"Expert",6:"Master",7:"Sage",8:"Legend"}
    lvl_name = level_names.get(st.session_state.level, "Legend")
    st.markdown(f"""
    <div class="level-badge">
        <div class="level-number">Lv.{st.session_state.level}</div>
        <div class="level-title">{lvl_name}</div>
        <div class="xp-bar-container" style="margin-top:8px;">
            <div class="xp-bar-fill" style="width:{xp_pct:.0f}%"></div>
        </div>
        <div style="font-size:.7rem;color:var(--muted);margin-top:4px;">{xp_in_level}/200 XP · 🔥 {st.session_state.streak} day streak</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Groq API Key", value=st.session_state.api_key,
        type="password", placeholder="gsk_...",
        help="Get your free key at https://console.groq.com/keys",
    )
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
    if st.session_state.api_key:
        st.markdown('<span class="badge green">✓ Key Saved</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge">No Key</span>', unsafe_allow_html=True)

    models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"]
    st.session_state.model = st.selectbox("Model", models, index=models.index(st.session_state.model) if st.session_state.model in models else 0)

    # Streaming toggle
    st.markdown("---")
    st.markdown('<div class="section-label">⚡ Features</div>', unsafe_allow_html=True)
    st.session_state.stream_enabled = st.toggle("Real-time Streaming Answers", value=st.session_state.stream_enabled,
                                                  help="Stream AI responses token-by-token as they're generated")

    st.markdown("---")
    st.markdown('<div class="section-label">📄 Upload Materials</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop PDF or TXT (multi-select)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )
    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.documents:
                with st.spinner(f"Extracting {f.name}…"):
                    text = extract_text_from_file(f)
                st.session_state.documents[f.name] = text
                if not st.session_state.active_doc:
                    st.session_state.active_doc = f.name
                    st.session_state.extracted_text = text
                st.success(f"✓ {f.name}")
                update_streak()
                award_xp(10, "Upload document")

    if st.session_state.documents:
        st.markdown('<div class="section-label" style="margin-top:12px;">Active Document</div>', unsafe_allow_html=True)
        doc_options = list(st.session_state.documents.keys())
        chosen = st.selectbox("Select document", doc_options,
                               index=doc_options.index(st.session_state.active_doc) if st.session_state.active_doc in doc_options else 0,
                               label_visibility="collapsed")
        if chosen != st.session_state.active_doc:
            st.session_state.active_doc = chosen
            st.session_state.extracted_text = st.session_state.documents[chosen]
            st.rerun()

        chips_html = ""
        for dname in doc_options:
            active_cls = "active" if dname == st.session_state.active_doc else ""
            short = dname[:20] + "…" if len(dname) > 20 else dname
            chips_html += f'<span class="doc-chip {active_cls}">📄 {short}</span>'
        st.markdown(chips_html, unsafe_allow_html=True)

        if st.button("🗑️ Remove active doc"):
            del st.session_state.documents[st.session_state.active_doc]
            if st.session_state.documents:
                st.session_state.active_doc = list(st.session_state.documents.keys())[0]
                st.session_state.extracted_text = st.session_state.documents[st.session_state.active_doc]
            else:
                st.session_state.active_doc = None
                st.session_state.extracted_text = ""
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-label">⚙️ Settings</div>', unsafe_allow_html=True)
    st.session_state.num_flashcards = st.slider("Flashcards to generate", 4, 20, st.session_state.num_flashcards)
    st.session_state.num_quiz = st.slider("Quiz questions", 3, 15, st.session_state.num_quiz)

    st.markdown("---")
    if st.session_state.achievements:
        st.markdown('<div class="section-label">🏅 Achievements</div>', unsafe_allow_html=True)
        ach_map = {
            "first_quiz":("🎯","First Quiz"),"quiz_master":("🏆","Quiz Master"),
            "flashcard_fan":("🃏","Flashcard Fan"),"perfect_score":("💯","Perfect Score"),
            "streak_3":("🔥","3-Day Streak"),"level_5":("⭐","Scholar"),
            "multi_doc":("📚","Researcher"),"note_taker":("📝","Note Taker"),
            "voice_user":("🎤","Voice Learner"),
        }
        badges_html = ""
        for ach in st.session_state.achievements:
            icon, name = ach_map.get(ach, ("🏅", ach))
            badges_html += f'<span class="badge gold">{icon} {name}</span> '
        st.markdown(badges_html, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("♻️ Reset progress"):
        for k, v in DEFAULTS.items():
            if k not in ("api_key", "model"):
                st.session_state[k] = copy.deepcopy(v)
        if PROFILE_FILE.exists():
            PROFILE_FILE.unlink()
        st.rerun()

# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────
if not DEPS_OK:
    st.error(f"Missing dependency: {MISSING}\nRun: pip install -r requirements.txt")
    st.stop()

st.markdown(f"""
<div class="hero">
    <h1>📚 AI Study Buddy</h1>
    <p>No sign-up needed. Upload notes → get summaries, flashcards, adaptive quizzes, voice tutoring, and real-time AI answers.</p>
</div>
""", unsafe_allow_html=True)

active_text = get_active_text()
if not active_text:
    st.markdown("""
    <div class="card" style="text-align:center;padding:48px;">
        <div style="font-size:3rem;margin-bottom:16px;">⬆️</div>
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">No material loaded</div>
        <div style="color:var(--muted);font-size:.9rem;">Upload a PDF or TXT file in the sidebar to get started.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "👤 My Dashboard", "📝 Summary", "🃏 Flashcards", "🎯 Quiz", "🧠 Adaptive Quiz",
    "🤖 Agent Chat", "🔍 Explain", "📝 Notes", "📊 Progress",
    "🎤 Voice Tutor", "⏱️ Study Mode", "📚 Multi-Doc", "🔍 Raw"
])
(tab_userdash, tab_sum, tab_flash, tab_quiz, tab_adaptive,
 tab_chat, tab_explain, tab_notes, tab_dashboard,
 tab_voice, tab_study, tab_multi, tab_raw) = tabs

# ════════════════════════════════════════════════════════════════════════════
# TAB 0 – USER DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab_userdash:
    initials_big = st.session_state.username[:2].upper()
    avg_score = int(sum(h["score_pct"] for h in st.session_state.quiz_history) / len(st.session_state.quiz_history)) if st.session_state.quiz_history else 0
    joined_date = _load_profile().get("created", date.today().isoformat())

    st.markdown(f"""
    <div class="dashboard-hero">
        <div class="dash-avatar">{initials_big}</div>
        <div>
            <div class="dash-name">{st.session_state.username}</div>
            <div class="dash-meta">📧 {st.session_state.user_email} &nbsp;·&nbsp; 📅 Started {joined_date}</div>
            <div style="margin-top:8px;">
                <span class="badge gold">Lv.{st.session_state.level} {level_names.get(st.session_state.level,'Legend')}</span>
                <span class="badge cyan">🔥 {st.session_state.streak}-day streak</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # XP progress
    st.markdown('<div class="section-label">XP Progress</div>', unsafe_allow_html=True)
    xp_in_lvl = st.session_state.xp % 200
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
        <div style="font-family:'DM Mono',monospace;font-size:.85rem;color:var(--muted);">Lv.{st.session_state.level}</div>
        <div style="flex:1;">
            <div class="xp-bar-container" style="height:12px;">
                <div class="xp-bar-fill" style="width:{xp_in_lvl/200*100:.0f}%"></div>
            </div>
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:.85rem;color:var(--muted);">Lv.{st.session_state.level+1}</div>
        <div style="font-size:.8rem;color:var(--xp-color);">{xp_in_lvl}/200 XP</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    s1, s2, s3, s4, s5 = st.columns(5)
    stats = [
        (s1, str(st.session_state.xp), "Total XP", "var(--xp-color)"),
        (s2, str(st.session_state.total_quizzes), "Quizzes Done", "var(--accent3)"),
        (s3, f"{avg_score}%", "Avg Score", "var(--accent2)"),
        (s4, str(st.session_state.total_flashcards_viewed), "Cards Viewed", "var(--accent)"),
        (s5, str(len(st.session_state.revision_notes)), "Notes Saved", "var(--success)"),
    ]
    for col, num, label, color in stats:
        with col:
            st.markdown(f"""
            <div class="stat-pill">
                <div class="stat-pill-num" style="color:{color};">{num}</div>
                <div class="stat-pill-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Recent quiz history
    st.markdown("---")
    st.markdown('<div class="section-label">Recent Quiz Results</div>', unsafe_allow_html=True)
    if st.session_state.quiz_history:
        for h in reversed(st.session_state.quiz_history[-5:]):
            pct = h["score_pct"]
            color = "#4ade80" if pct >= 80 else "#facc15" if pct >= 60 else "#f87171"
            st.markdown(f"""
            <div class="prog-bar-wrap">
                <div class="prog-bar-label">{h['date'][:10]}<br><span style="color:var(--muted);font-size:.68rem;">{h.get('topic','')[:18]}</span></div>
                <div class="prog-bar-track">
                    <div class="prog-bar-value" style="width:{pct}%;background:{color};"></div>
                </div>
                <div class="prog-bar-pct">{pct}%</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:var(--muted);font-size:.85rem;">No quizzes completed yet.</div>', unsafe_allow_html=True)

    # Achievements gallery
    st.markdown("---")
    st.markdown('<div class="section-label">🏅 Achievement Gallery</div>', unsafe_allow_html=True)
    ach_all = [
        ("first_quiz","🎯","First Quiz","Completed your first quiz"),
        ("quiz_master","🏆","Quiz Master","Completed 10 quizzes"),
        ("flashcard_fan","🃏","Flashcard Fan","Viewed 50 flashcards"),
        ("perfect_score","💯","Perfect Score","Got 100% on a quiz"),
        ("streak_3","🔥","3-Day Streak","Studied 3 days in a row"),
        ("level_5","⭐","Scholar","Reached Level 5"),
        ("multi_doc","📚","Researcher","Uploaded 3+ documents"),
        ("note_taker","📝","Note Taker","Saved 5 revision notes"),
        ("voice_user","🎤","Voice Learner","Used Voice AI Tutor"),
    ]
    ach_cols = st.columns(3)
    for idx, (key, icon, name, desc) in enumerate(ach_all):
        earned = key in st.session_state.achievements
        with ach_cols[idx % 3]:
            opacity = "1" if earned else "0.25"
            border = "var(--xp-color)" if earned else "var(--border)"
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid {border};border-radius:12px;padding:14px;text-align:center;margin-bottom:10px;opacity:{opacity};">
                <div style="font-size:2rem;">{icon}</div>
                <div style="font-weight:700;font-size:.82rem;margin:4px 0;">{name}</div>
                <div style="font-size:.7rem;color:var(--muted);">{desc}</div>
                {"<div style='font-size:.68rem;color:var(--xp-color);margin-top:4px;'>✓ Earned</div>" if earned else ""}
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – SUMMARY
# ════════════════════════════════════════════════════════════════════════════
with tab_sum:
    st.markdown('<div class="section-label">Intelligent Summary</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col2:
        gen_summary = st.button("✨ Generate", key="btn_summary")

    if gen_summary:
        if not st.session_state.api_key:
            st.warning("Enter your API key in the sidebar first.")
        else:
            chunk = chunk_text(active_text)
            if st.session_state.stream_enabled:
                st.markdown('<div class="section-label" style="margin-top:16px;">⚡ Streaming Summary</div>', unsafe_allow_html=True)
                placeholder = st.empty()
                with st.spinner(""):
                    result = run_chain_streaming(SUMMARY_PROMPT, {"text": chunk}, placeholder)
                st.session_state.summary = result
            else:
                with st.spinner("Reading and summarising…"):
                    result = run_chain(SUMMARY_PROMPT, {"text": chunk})
                    st.session_state.summary = result
            award_xp(15, "Generated summary")
            check_achievements()

    if st.session_state.summary:
        if not gen_summary:
            st.markdown(f'<div class="summary-box">{st.session_state.summary}</div>', unsafe_allow_html=True)
        st.download_button("⬇️ Download Summary", st.session_state.summary,
            file_name=f"summary_{st.session_state.active_doc or 'doc'}.txt", mime="text/plain")
    else:
        if not gen_summary:
            st.markdown('<div class="card" style="text-align:center;padding:36px;color:var(--muted);">Click <b>Generate</b> to produce an summary.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – FLASHCARDS
# ════════════════════════════════════════════════════════════════════════════
with tab_flash:
    st.markdown('<div class="section-label">Interactive Flashcards</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        gen_fc = st.button(f"✨ Generate {st.session_state.num_flashcards} Cards", key="btn_flash")

    if gen_fc:
        if not st.session_state.api_key:
            st.warning("Enter your API key in the sidebar first.")
        else:
            with st.spinner("Creating flashcards…"):
                chunk = chunk_text(active_text)
                result = run_chain(FLASHCARD_PROMPT, {"text": chunk, "num": st.session_state.num_flashcards})
                parsed = parse_json_block(result)
                if parsed and isinstance(parsed, list):
                    st.session_state.flashcards = parsed
                    st.session_state.fc_index = 0
                    st.session_state.fc_flipped = False
                    award_xp(10, "Generated flashcards")
                else:
                    st.error("Couldn't parse flashcards. Try again.")

    cards = st.session_state.flashcards
    if cards:
        idx = st.session_state.fc_index
        card = cards[idx]
        total = len(cards)
        flipped = st.session_state.fc_flipped
        topic = card.get("topic", "")
        diff = card.get("difficulty", 1)
        diff_label = {1:"🟢 Easy",2:"🟡 Medium",3:"🔴 Hard"}.get(diff,"")
        st.markdown(f'<span class="badge cyan">{topic}</span><span class="badge">{diff_label}</span>', unsafe_allow_html=True)
        st.progress((idx + 1) / total)
        st.markdown(f"<div style='text-align:right;font-size:.8rem;color:var(--muted);margin-bottom:12px;'>{idx+1} / {total}</div>", unsafe_allow_html=True)
        flip_class = "flipped" if flipped else ""
        st.markdown(f"""
        <div class="flashcard {flip_class}">
          <div class="flashcard-inner">
            <div class="flashcard-front">
              <div class="flashcard-label">Question</div>
              <div class="flashcard-text">{card['front']}</div>
            </div>
            <div class="flashcard-back">
              <div class="flashcard-label" style="color:var(--accent3);">Answer</div>
              <div class="flashcard-text">{card['back']}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("⬅️ Prev", key="fc_prev"):
                st.session_state.fc_index = max(0, idx - 1)
                st.session_state.fc_flipped = False
                st.rerun()
        with c2:
            label = "👁️ Hide" if flipped else "👁️ Reveal"
            if st.button(label, key="fc_flip"):
                st.session_state.fc_flipped = not flipped
                if not flipped:
                    st.session_state.total_flashcards_viewed += 1
                    award_xp(1, "Viewed flashcard")
                    check_achievements()
                st.rerun()
        with c3:
            if st.button("➡️ Next", key="fc_next"):
                st.session_state.fc_index = min(total - 1, idx + 1)
                st.session_state.fc_flipped = False
                st.rerun()
        with c4:
            if st.button("🔀 Shuffle", key="fc_shuffle"):
                random.shuffle(st.session_state.flashcards)
                st.session_state.fc_index = 0
                st.session_state.fc_flipped = False
                st.rerun()
        st.markdown("<div style='margin-top:16px;'><div class='section-label'>How well did you know this?</div></div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("😕 Hard – review soon", key="rate_hard"):
                award_xp(2); st.toast("Marked for review!", icon="📌")
        with r2:
            if st.button("🤔 Medium – review later", key="rate_med"):
                award_xp(3); st.toast("Got it!", icon="👍")
        with r3:
            if st.button("😊 Easy – got it!", key="rate_easy"):
                award_xp(5); st.toast("+5 XP!", icon="⭐"); st.rerun()
        with st.expander("📋 View all cards"):
            for i, c in enumerate(cards):
                diff_c = {1:"🟢",2:"🟡",3:"🔴"}.get(c.get("difficulty",1),"")
                st.markdown(f"""
                <div class="card-sm">
                    <div style="font-size:.7rem;color:var(--muted);margin-bottom:4px;">Card {i+1} {diff_c} {c.get('topic','')}</div>
                    <div style="font-weight:700;margin-bottom:6px;">{c['front']}</div>
                    <div style="color:var(--accent3);font-size:.9rem;">{c['back']}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="card" style="text-align:center;padding:36px;color:var(--muted);">Click <b>Generate Cards</b> to create interactive flashcards.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – STANDARD QUIZ
# ════════════════════════════════════════════════════════════════════════════
with tab_quiz:
    st.markdown('<div class="section-label">Knowledge Quiz</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col2:
        gen_quiz = st.button(f"✨ Generate {st.session_state.num_quiz}-Q Quiz", key="btn_quiz")

    if gen_quiz:
        if not st.session_state.api_key:
            st.warning("Enter your API key in the sidebar first.")
        else:
            with st.spinner("Writing quiz questions…"):
                chunk = chunk_text(active_text)
                result = run_chain(QUIZ_PROMPT, {"text": chunk, "num": st.session_state.num_quiz})
                parsed = parse_json_block(result)
                if parsed and isinstance(parsed, list):
                    st.session_state.quiz = parsed
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                else:
                    st.error("Couldn't parse quiz. Try again.")

    quiz = st.session_state.quiz
    if quiz:
        answered = st.session_state.quiz_answers
        submitted = st.session_state.quiz_submitted
        for i, q in enumerate(quiz):
            diff = q.get("difficulty", 1)
            diff_label = {1:"🟢 Easy",2:"🟡 Medium",3:"🔴 Hard"}.get(diff,"")
            topic = q.get("topic", "")
            st.markdown(f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <div style="font-size:.7rem;color:var(--muted);">Question {i+1} of {len(quiz)}</div>
                    <div><span class="badge cyan">{topic}</span><span class="badge">{diff_label}</span></div>
                </div>
                <div style="font-weight:700;font-size:1rem;margin-bottom:16px;">{q['question']}</div>
            </div>""", unsafe_allow_html=True)
            correct = q.get("answer", "A").strip().upper()[0]
            for opt in q.get("options", []):
                opt_letter = opt.strip()[0].upper()
                chosen = answered.get(i) == opt_letter
                if submitted:
                    if opt_letter == correct:
                        css = "quiz-option correct"
                    elif chosen:
                        css = "quiz-option wrong"
                    else:
                        css = "quiz-option"
                    st.markdown(f'<div class="{css}">{opt}</div>', unsafe_allow_html=True)
                else:
                    if st.button(opt, key=f"q{i}_{opt_letter}"):
                        st.session_state.quiz_answers[i] = opt_letter
                        st.rerun()
                    if chosen:
                        st.markdown(f'<div style="margin-top:-12px;margin-bottom:4px;font-size:.75rem;color:var(--accent);">← Your answer</div>', unsafe_allow_html=True)
            if submitted and q.get("explanation"):
                st.markdown(f'<div style="background:rgba(124,106,255,.08);border-radius:10px;padding:10px 14px;font-size:.82rem;color:var(--muted);margin-top:8px;">💡 {q["explanation"]}</div>', unsafe_allow_html=True)

        if not submitted:
            if len(answered) == len(quiz):
                if st.button("🎯 Submit Quiz", key="quiz_submit"):
                    st.session_state.quiz_submitted = True
                    score = sum(1 for i, q in enumerate(quiz) if answered.get(i) == q.get("answer","A").strip().upper()[0])
                    pct = int(score / len(quiz) * 100)
                    st.session_state.quiz_history.append({"date": date.today().isoformat(), "score_pct": pct, "topic": st.session_state.active_doc or "doc", "num_q": len(quiz), "score": score})
                    st.session_state.total_quizzes += 1
                    st.session_state.total_correct += score
                    award_xp(pct // 5 + 10, "Completed quiz")
                    wrong_topics = [quiz[i].get("topic","") for i in range(len(quiz)) if answered.get(i) != quiz[i].get("answer","A").strip().upper()[0]]
                    for t in wrong_topics:
                        if t and t not in st.session_state.weak_areas:
                            st.session_state.weak_areas.append(t)
                    correct_topics = [quiz[i].get("topic","") for i in range(len(quiz)) if answered.get(i) == quiz[i].get("answer","A").strip().upper()[0]]
                    for t in correct_topics:
                        if t and t not in st.session_state.strong_areas:
                            st.session_state.strong_areas.append(t)
                    auth_save_profile(st.session_state.username, {"total_quizzes": st.session_state.total_quizzes, "total_correct": st.session_state.total_correct, "quiz_history": st.session_state.quiz_history})
                    new_achs = check_achievements()
                    for name_a, desc_a in new_achs:
                        st.toast(f"🏅 Achievement: {name_a}!", icon="🏆")
                    st.rerun()
            else:
                st.info(f"Answer all {len(quiz)} questions to submit. ({len(answered)}/{len(quiz)} done)")
        else:
            score = sum(1 for i, q in enumerate(quiz) if answered.get(i) == q.get("answer","A").strip().upper()[0])
            pct = int(score / len(quiz) * 100)
            grade = "🏆 Excellent!" if pct >= 80 else "👍 Good effort!" if pct >= 60 else "📖 Keep studying!"
            st.markdown(f"""
            <div class="card score-ring">
                <div class="ring-container"><div class="ring-number">{pct}%</div><div class="ring-label">{grade}</div></div>
                <div>
                    <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">{score} / {len(quiz)} correct</div>
                    <div style="color:var(--muted);font-size:.85rem;">{'Great command of the material!' if pct>=80 else 'Review highlighted answers above!'}</div>
                    <div style="margin-top:8px;"><span class="badge gold">+{pct//5+10} XP earned</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Retake Quiz", key="quiz_retry"):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center;padding:36px;color:var(--muted);">Click <b>Generate Quiz</b> to create a scored multiple-choice quiz.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 – ADAPTIVE QUIZ
# ════════════════════════════════════════════════════════════════════════════
with tab_adaptive:
    st.markdown('<div class="section-label">🧠 Adaptive Quiz — Targets Your Weak Areas</div>', unsafe_allow_html=True)
    if st.session_state.weak_areas:
        st.markdown('<div style="margin-bottom:12px;">Weak areas detected:</div>', unsafe_allow_html=True)
        tags = "".join(f'<span class="weak-tag">{t}</span>' for t in st.session_state.weak_areas)
        st.markdown(tags, unsafe_allow_html=True)
    else:
        st.markdown('<div class="card-sm" style="color:var(--muted);">Complete a standard quiz first to identify weak areas.</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        adapt_diff = st.selectbox("Difficulty focus", ["Auto (based on history)", "Easy (1)", "Medium (2)", "Hard (3)"], key="adapt_diff_sel")
    with col2:
        adapt_num = st.number_input("Number of questions", 3, 15, 5, key="adapt_num")
    if st.button("🧠 Generate Adaptive Quiz", key="btn_adaptive"):
        if not st.session_state.api_key:
            st.warning("Enter your API key first.")
        else:
            weak_str = ", ".join(st.session_state.weak_areas) if st.session_state.weak_areas else "general topics"
            diff_map = {"Auto (based on history)": 2, "Easy (1)": 1, "Medium (2)": 2, "Hard (3)": 3}
            diff_val = diff_map.get(adapt_diff, 2)
            with st.spinner("Building adaptive quiz targeting your weak areas…"):
                chunk = chunk_text(active_text)
                result = run_chain(ADAPTIVE_QUIZ_PROMPT, {"text": chunk, "num": adapt_num, "weak_areas": weak_str, "difficulty": diff_val})
                parsed = parse_json_block(result)
                if parsed and isinstance(parsed, list):
                    st.session_state.adaptive_pool = parsed
                    st.session_state["adap_answers"] = {}
                    st.session_state["adap_submitted"] = False
                else:
                    st.error("Couldn't parse adaptive quiz. Try again.")
    aq = st.session_state.adaptive_pool
    if aq:
        adap_ans = st.session_state.get("adap_answers", {})
        adap_sub = st.session_state.get("adap_submitted", False)
        for i, q in enumerate(aq):
            diff = q.get("difficulty", 2)
            diff_label = {1:"🟢 Easy",2:"🟡 Medium",3:"🔴 Hard"}.get(diff,"")
            topic = q.get("topic","")
            st.markdown(f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <div style="font-size:.7rem;color:var(--accent2);">🎯 Adaptive Q{i+1}</div>
                    <div><span class="badge pink">{topic}</span><span class="badge">{diff_label}</span></div>
                </div>
                <div style="font-weight:700;font-size:1rem;margin-bottom:16px;">{q['question']}</div>
            </div>""", unsafe_allow_html=True)
            correct = q.get("answer", "A").strip().upper()[0]
            for opt in q.get("options", []):
                opt_letter = opt.strip()[0].upper()
                chosen = adap_ans.get(i) == opt_letter
                if adap_sub:
                    css = "quiz-option correct" if opt_letter == correct else ("quiz-option wrong" if chosen else "quiz-option")
                    st.markdown(f'<div class="{css}">{opt}</div>', unsafe_allow_html=True)
                else:
                    if st.button(opt, key=f"aq{i}_{opt_letter}"):
                        st.session_state["adap_answers"][i] = opt_letter
                        st.rerun()
                    if chosen:
                        st.markdown(f'<div style="margin-top:-12px;margin-bottom:4px;font-size:.75rem;color:var(--accent2);">← Your answer</div>', unsafe_allow_html=True)
            if adap_sub and q.get("explanation"):
                st.markdown(f'<div style="background:rgba(255,106,176,.06);border-radius:10px;padding:10px 14px;font-size:.82rem;color:var(--muted);margin-top:8px;">💡 {q["explanation"]}</div>', unsafe_allow_html=True)
        if not adap_sub:
            if len(adap_ans) == len(aq):
                if st.button("🎯 Submit Adaptive Quiz", key="adap_submit"):
                    score = sum(1 for i, q in enumerate(aq) if adap_ans.get(i) == q.get("answer","A").strip().upper()[0])
                    pct = int(score/len(aq)*100)
                    st.session_state["adap_submitted"] = True
                    st.session_state.total_quizzes += 1
                    st.session_state.total_correct += score
                    st.session_state.quiz_history.append({"date": date.today().isoformat(), "score_pct": pct, "topic": "Adaptive", "num_q": len(aq), "score": score})
                    correct_topics = set(aq[i].get("topic","") for i in range(len(aq)) if adap_ans.get(i) == aq[i].get("answer","A").strip().upper()[0])
                    st.session_state.weak_areas = [t for t in st.session_state.weak_areas if t not in correct_topics]
                    award_xp(pct//4 + 15, "Adaptive quiz bonus")
                    auth_save_profile(st.session_state.username, {"total_quizzes": st.session_state.total_quizzes, "quiz_history": st.session_state.quiz_history})
                    check_achievements()
                    st.rerun()
            else:
                st.info(f"Answer all {len(aq)} questions. ({len(adap_ans)}/{len(aq)} done)")
        else:
            score = sum(1 for i, q in enumerate(aq) if adap_ans.get(i) == q.get("answer","A").strip().upper()[0])
            pct = int(score/len(aq)*100)
            grade = "🏆 Excellent!" if pct>=80 else "👍 Improving!" if pct>=50 else "📖 Keep going!"
            st.markdown(f"""
            <div class="card score-ring">
                <div class="ring-container"><div class="ring-number">{pct}%</div><div class="ring-label">{grade}</div></div>
                <div>
                    <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">{score}/{len(aq)} correct</div>
                    <div style="color:var(--muted);font-size:.85rem;">Weak areas mastered are removed!</div>
                    <div style="margin-top:8px;"><span class="badge gold">+{pct//4+15} XP (Adaptive Bonus)</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Retry Adaptive Quiz", key="adap_retry"):
                st.session_state["adap_answers"] = {}
                st.session_state["adap_submitted"] = False
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 – CHAT  (with streaming)
# ════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown('<div class="section-label">AI Chat Tutor</div>', unsafe_allow_html=True)
    stream_indicator = '<span class="badge cyan">⚡ Streaming ON</span>' if st.session_state.stream_enabled else '<span class="badge">Streaming OFF</span>'
    st.markdown(f'<div style="color:var(--muted);font-size:.85rem;margin-bottom:16px;">Ask anything about your material. {stream_indicator}</div>', unsafe_allow_html=True)

    for role, msg in st.session_state.history:
        if role == "user":
            st.markdown(f'<div style="display:flex;justify-content:flex-end;margin-bottom:12px;"><div style="background:var(--accent);color:white;border-radius:16px 16px 4px 16px;padding:12px 18px;max-width:75%;font-size:.9rem;">{msg}</div></div>', unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                st.markdown(msg, unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_q = st.text_input("Your question", placeholder="e.g. What are the main causes of X?", label_visibility="collapsed")
        submitted_chat = st.form_submit_button("Send →")

    if submitted_chat and user_q.strip():
        if not st.session_state.api_key:
            st.warning("Enter your Groq API key in the sidebar.")
        else:
            history_str = "\n".join(f"{r.upper()}: {m[:500]}" for r, m in st.session_state.history[-6:])
            st.session_state.history.append(("user", user_q))
            get_llm()  # sync API key/model into env for the agent graph
            final, steps = {}, []
            with st.status("🤖 Agents at work…", expanded=True) as status:
                try:
                    state = {"task": "auto", "query": user_q, "level": "Undergraduate",
                             "context": chunk_text(active_text, 8000), "history": history_str}
                    for upd in get_agent().stream(state, stream_mode="updates"):
                        for _, delta in upd.items():
                            final.update(delta)
                            if delta.get("trace"):
                                steps = delta["trace"]
                                st.write(steps[-1])
                    status.update(label="Done", state="complete", expanded=False)
                    answer = final.get("output", "Sorry, I couldn't produce an answer.")
                    if final.get("task") == "quiz":
                        answer = "🧠 Want to be tested? Open the **Adaptive Quiz** tab - it targets your weak areas."
                except Exception as e:
                    status.update(label="Error", state="error")
                    answer = f"⚠️ {e}"
            if steps:
                answer += "\n\n<span style='font-size:.72rem;color:var(--muted)'>🧠 " + " → ".join(t.replace("**", "") for t in steps) + "</span>"
            st.session_state.history.append(("assistant", answer))
            award_xp(5, "Chat interaction")
            st.rerun()

    if st.session_state.history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.history = []
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 6 – EXPLAIN MODES (with streaming)
# ════════════════════════════════════════════════════════════════════════════
with tab_explain:
    st.markdown('<div class="section-label">🔍 Explain Any Concept — Choose Your Mode</div>', unsafe_allow_html=True)
    modes = {
        "standard": ("📖","Standard","Clear, structured explanation"),
        "eli5":     ("🧒","ELI5","Like I'm 5 — ultra simple"),
        "expert":   ("🎓","Expert","Deep technical breakdown"),
        "analogy":  ("🎭","Analogy","Pure metaphors & stories"),
        "visual":   ("🗺️","Visual","ASCII diagrams & layouts"),
    }
    cols = st.columns(5)
    for idx, (mode_key, (icon, name, desc)) in enumerate(modes.items()):
        with cols[idx]:
            selected_cls = "selected" if st.session_state.explain_mode == mode_key else ""
            st.markdown(f"""
            <div class="explain-mode {selected_cls}">
                <div class="explain-mode-icon">{icon}</div>
                <div class="explain-mode-name">{name}</div>
                <div class="explain-mode-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Select {name}", key=f"mode_{mode_key}"):
                st.session_state.explain_mode = mode_key
                st.rerun()
    st.markdown("---")
    selected_icon, selected_name, selected_desc = modes[st.session_state.explain_mode]
    st.markdown(f'<span class="badge cyan">{selected_icon} Mode: {selected_name}</span><span style="color:var(--muted);font-size:.82rem;"> — {selected_desc}</span>', unsafe_allow_html=True)
    concept = st.text_input("Concept to explain", placeholder="e.g. Photosynthesis, Recursion, The French Revolution…", value=st.session_state.concept_to_explain, key="concept_input")
    if st.button("✨ Explain This", key="btn_explain"):
        if not st.session_state.api_key:
            st.warning("Enter your API key first.")
        elif not concept.strip():
            st.warning("Enter a concept to explain.")
        else:
            template = EXPLAIN_PROMPT[st.session_state.explain_mode]
            chunk = chunk_text(active_text, 6000)
            st.session_state.concept_to_explain = concept
            if st.session_state.stream_enabled:
                st.markdown(f'<div class="section-label" style="margin-top:16px;">{selected_icon} Streaming {selected_name} Explanation</div>', unsafe_allow_html=True)
                placeholder = st.empty()
                result = run_chain_streaming(template, {"concept": concept, "text": chunk}, placeholder)
            else:
                with st.spinner(f"Generating {selected_name} explanation…"):
                    result = run_chain(template, {"concept": concept, "text": chunk})
                st.markdown(f"""
                <div class="card" style="margin-top:16px;">
                    <div class="section-label">{selected_icon} {selected_name}: {concept}</div>
                    <div style="font-family:'DM Mono',monospace;font-size:.88rem;line-height:1.8;white-space:pre-wrap;">{result}</div>
                </div>""", unsafe_allow_html=True)
            st.session_state.explain_result = result
            award_xp(8, "Used explain mode")
    elif st.session_state.explain_result:
        st.markdown(f"""
        <div class="card" style="margin-top:16px;">
            <div class="section-label">{selected_icon} {selected_name}: {st.session_state.concept_to_explain}</div>
            <div style="font-family:'DM Mono',monospace;font-size:.88rem;line-height:1.8;white-space:pre-wrap;">{st.session_state.explain_result}</div>
        </div>""", unsafe_allow_html=True)

    if st.session_state.explain_result:
        if st.button("📝 Save to Revision Notes", key="save_explain_note"):
            note = {"text": f"[{selected_name}] {st.session_state.concept_to_explain}:\n{st.session_state.explain_result}", "date": date.today().isoformat(), "doc": st.session_state.active_doc or "doc", "tags": [st.session_state.concept_to_explain, selected_name]}
            st.session_state.revision_notes.append(note)
            award_xp(3)
            check_achievements()
            st.toast("Saved to revision notes!", icon="📝")

# ════════════════════════════════════════════════════════════════════════════
# TAB 7 – REVISION NOTES
# ════════════════════════════════════════════════════════════════════════════
with tab_notes:
    st.markdown('<div class="section-label">📝 Revision Notes</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c2:
        gen_notes = st.button("🤖 AI-Generated Notes", key="btn_gen_notes")
    if gen_notes:
        if not st.session_state.api_key:
            st.warning("Enter your API key first.")
        else:
            weak_str = ", ".join(st.session_state.weak_areas) if st.session_state.weak_areas else "all key topics"
            chunk = chunk_text(active_text, 10000)
            if st.session_state.stream_enabled:
                st.markdown('<div class="section-label" style="margin-top:8px;">⚡ Generating Notes…</div>', unsafe_allow_html=True)
                placeholder = st.empty()
                result = run_chain_streaming(REVISION_NOTES_PROMPT, {"text": chunk, "weak_areas": weak_str}, placeholder)
            else:
                with st.spinner("Generating focused revision notes…"):
                    result = run_chain(REVISION_NOTES_PROMPT, {"text": chunk, "weak_areas": weak_str})
            note = {"text": result, "date": date.today().isoformat(), "doc": st.session_state.active_doc or "doc", "tags": ["AI Generated"] + st.session_state.weak_areas[:3]}
            st.session_state.revision_notes.append(note)
            award_xp(10)
            check_achievements()
            st.toast("Notes generated and saved!", icon="✅")

    with st.expander("✏️ Add Manual Note"):
        manual_note = st.text_area("Write your note", placeholder="Key concept, formula, or insight…", height=120)
        tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g. biology, cell, exam")
        if st.button("💾 Save Note", key="save_manual_note"):
            if manual_note.strip():
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                st.session_state.revision_notes.append({"text": manual_note, "date": date.today().isoformat(), "doc": st.session_state.active_doc or "doc", "tags": tags})
                award_xp(5)
                check_achievements()
                st.toast("Note saved!", icon="📝")
                st.rerun()

    notes = st.session_state.revision_notes
    if notes:
        st.markdown(f"<div style='color:var(--muted);font-size:.8rem;margin-bottom:16px;'>{len(notes)} notes saved</div>", unsafe_allow_html=True)
        search_q = st.text_input("🔍 Search notes", placeholder="Search by keyword or tag…", key="notes_search")
        all_notes_text = ""
        for i, note in enumerate(reversed(notes)):
            note_text = note.get("text","")
            note_date = note.get("date","")
            note_doc = note.get("doc","")
            note_tags = note.get("tags",[])
            if search_q and search_q.lower() not in note_text.lower() and not any(search_q.lower() in t.lower() for t in note_tags):
                continue
            tags_html = " ".join(f'<span class="badge cyan">{t}</span>' for t in note_tags)
            all_notes_text += f"--- Note {len(notes)-i} ({note_date}) ---\n{note_text}\n\n"
            col_note, col_del = st.columns([10, 1])
            with col_note:
                st.markdown(f"""
                <div class="note-item">
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                        <div style="font-size:.7rem;color:var(--muted);">📄 {note_doc} · {note_date}</div>
                        <div>{tags_html}</div>
                    </div>
                    <div style="white-space:pre-wrap;line-height:1.7;">{note_text}</div>
                </div>""", unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_note_{i}"):
                    real_idx = len(notes) - 1 - i
                    st.session_state.revision_notes.pop(real_idx)
                    st.rerun()
        if all_notes_text:
            st.download_button("⬇️ Download All Notes", all_notes_text, file_name="revision_notes.txt", mime="text/plain")
    else:
        st.markdown('<div class="card" style="text-align:center;padding:36px;color:var(--muted);">No notes yet.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 8 – PROGRESS DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab_dashboard:
    st.markdown('<div class="section-label">📊 Progress Dashboard</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    avg_pct = int(sum(h["score_pct"] for h in st.session_state.quiz_history) / len(st.session_state.quiz_history)) if st.session_state.quiz_history else 0
    with m1: st.metric("Total XP", f"{st.session_state.xp} ✨")
    with m2: st.metric("Quizzes Done", st.session_state.total_quizzes)
    with m3: st.metric("Avg Score", f"{avg_pct}%")
    with m4: st.metric("🔥 Streak", f"{st.session_state.streak} days")
    st.markdown("---")
    if st.session_state.quiz_history:
        st.markdown('<div class="section-label">Quiz Score History</div>', unsafe_allow_html=True)
        for h in st.session_state.quiz_history[-10:]:
            pct = h["score_pct"]
            color = "#4ade80" if pct >= 80 else "#facc15" if pct >= 60 else "#f87171"
            st.markdown(f"""
            <div class="prog-bar-wrap">
                <div class="prog-bar-label">{h['date'][:10]}<br><span style="color:var(--muted);font-size:.68rem;">{h.get('topic','')[:20]}</span></div>
                <div class="prog-bar-track"><div class="prog-bar-value" style="width:{pct}%;background:{color};"></div></div>
                <div class="prog-bar-pct">{pct}%</div>
            </div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-label" style="margin-top:16px;">⚠️ Weak Areas</div>', unsafe_allow_html=True)
        if st.session_state.weak_areas:
            st.markdown("".join(f'<span class="weak-tag">{t}</span>' for t in set(st.session_state.weak_areas)), unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge green">No weak areas detected</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-label" style="margin-top:16px;">✅ Strong Areas</div>', unsafe_allow_html=True)
        if st.session_state.strong_areas:
            st.markdown("".join(f'<span class="strong-tag">{t}</span>' for t in set(st.session_state.strong_areas)), unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted);font-size:.85rem;">Complete quizzes to see your strengths.</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="section-label">Activity Summary</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.markdown(f'<div class="card-sm" style="text-align:center;"><div style="font-size:1.8rem;font-weight:800;color:var(--accent3);">{st.session_state.total_flashcards_viewed}</div><div style="font-size:.72rem;color:var(--muted);text-transform:uppercase;">Cards Viewed</div></div>', unsafe_allow_html=True)
    with s2: st.markdown(f'<div class="card-sm" style="text-align:center;"><div style="font-size:1.8rem;font-weight:800;color:var(--accent2);">{len(st.session_state.revision_notes)}</div><div style="font-size:.72rem;color:var(--muted);text-transform:uppercase;">Notes Saved</div></div>', unsafe_allow_html=True)
    with s3: st.markdown(f'<div class="card-sm" style="text-align:center;"><div style="font-size:1.8rem;font-weight:800;color:var(--accent);">{len(st.session_state.documents)}</div><div style="font-size:.72rem;color:var(--muted);text-transform:uppercase;">Documents</div></div>', unsafe_allow_html=True)
    with s4: st.markdown(f'<div class="card-sm" style="text-align:center;"><div style="font-size:1.8rem;font-weight:800;color:var(--xp-color);">{len(st.session_state.achievements)}</div><div style="font-size:.72rem;color:var(--muted);text-transform:uppercase;">Achievements</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 9 – 🎤 VOICE AI TUTOR  (NEW)
# ════════════════════════════════════════════════════════════════════════════
with tab_voice:
    st.markdown('<div class="section-label">🎤 Voice AI Tutor</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color:var(--muted);font-size:.85rem;margin-bottom:20px;">
        Type or paste a spoken question, get a natural spoken-style AI answer, and use your browser's 
        Text-to-Speech to hear it read aloud. Voice-to-text input is available via the 🎙️ button on mobile.
    </div>
    """, unsafe_allow_html=True)

    # Voice conversation history
    if st.session_state.voice_history:
        st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)
        for entry in st.session_state.voice_history:
            if entry["role"] == "student":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                    <div style="background:var(--accent);color:white;border-radius:18px 18px 4px 18px;padding:14px 20px;max-width:78%;font-size:.9rem;line-height:1.6;">
                        🎤 {entry['text']}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:14px;">
                    <div>
                        <div style="font-size:.68rem;color:var(--muted);margin-bottom:4px;margin-left:4px;">🤖 AI Tutor</div>
                        <div class="voice-answer">{entry['text']}</div>
                        <div style="margin-top:8px;">
                            <button onclick="
                                var u = new SpeechSynthesisUtterance({json.dumps(entry['text'])});
                                u.rate=0.95; u.pitch=1.05;
                                window.speechSynthesis.speak(u);
                            " style="background:rgba(106,255,224,.15);border:1px solid rgba(106,255,224,.3);color:#6affe0;border-radius:8px;padding:5px 14px;font-size:.75rem;cursor:pointer;font-family:Syne,sans-serif;">
                                🔊 Read Aloud
                            </button>
                            <button onclick="window.speechSynthesis.cancel()" style="background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.3);color:#f87171;border-radius:8px;padding:5px 14px;font-size:.75rem;cursor:pointer;font-family:Syne,sans-serif;margin-left:8px;">
                                ⏹ Stop
                            </button>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Voice input area
    st.markdown('<div class="section-label">Ask Your Tutor</div>', unsafe_allow_html=True)

    # Browser speech-to-text widget
    st.components.v1.html("""
    <div style="margin-bottom:12px;">
        <button id="micBtn" onclick="startVoice()" style="
            background:linear-gradient(135deg,#7c6aff,#ff6ab0);
            color:white;border:none;border-radius:12px;
            padding:10px 22px;font-size:.85rem;cursor:pointer;
            font-family:Syne,sans-serif;font-weight:700;">
            🎙️ Click to Speak (Browser STT)
        </button>
        <span id="mic-status" style="color:#7a7f96;font-size:.8rem;margin-left:12px;">Ready</span>
        <div id="transcript-preview" style="
            margin-top:10px;background:#1a1d27;border:1px solid #232736;
            border-radius:10px;padding:12px;font-size:.85rem;color:#e8eaf0;
            font-family:'DM Mono',monospace;min-height:40px;display:none;">
        </div>
        <button id="useBtn" onclick="useTranscript()" style="
            display:none;margin-top:8px;
            background:#6affe0;color:#0d0f14;border:none;
            border-radius:10px;padding:8px 18px;font-size:.8rem;
            cursor:pointer;font-family:Syne,sans-serif;font-weight:700;">
            ✓ Use This Question
        </button>
    </div>
    <script>
    var recognition;
    var transcript = "";
    function startVoice() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            document.getElementById('mic-status').textContent = '❌ Not supported in this browser. Use Chrome.';
            return;
        }
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        document.getElementById('mic-status').textContent = '🔴 Listening…';
        document.getElementById('micBtn').textContent = '⏹ Stop';
        document.getElementById('micBtn').onclick = function(){ recognition.stop(); };
        recognition.onresult = function(e) {
            transcript = Array.from(e.results).map(r=>r[0].transcript).join('');
            var prev = document.getElementById('transcript-preview');
            prev.style.display = 'block';
            prev.textContent = transcript;
        };
        recognition.onend = function() {
            document.getElementById('mic-status').textContent = '✅ Done — review below';
            document.getElementById('micBtn').textContent = '🎙️ Click to Speak';
            document.getElementById('micBtn').onclick = startVoice;
            if(transcript){ document.getElementById('useBtn').style.display='inline-block'; }
        };
        recognition.start();
    }
    function useTranscript() {
        // Copy to clipboard so user can paste into Streamlit input
        navigator.clipboard.writeText(transcript).then(function(){
            document.getElementById('mic-status').textContent = '📋 Copied! Paste into the text box below.';
        });
    }
    </script>
    """, height=160)

    voice_q = st.text_area(
        "Your question (type or paste from voice above)",
        placeholder="e.g. Can you explain mitosis in simple terms?",
        height=80,
        key="voice_q_input"
    )

    ask_col, clear_col = st.columns([3, 1])
    with ask_col:
        ask_voice = st.button("🎤 Ask AI Tutor", key="btn_voice_ask")
    with clear_col:
        if st.button("🗑️ Clear", key="btn_voice_clear"):
            st.session_state.voice_history = []
            st.rerun()

    if ask_voice:
        if not st.session_state.api_key:
            st.warning("Enter your API key in the sidebar first.")
        elif not voice_q.strip():
            st.warning("Please enter a question.")
        else:
            context = chunk_text(active_text, 5000)
            history_str = "\n".join(f"{e['role'].upper()}: {e['text']}" for e in st.session_state.voice_history[-4:])
            st.session_state.voice_history.append({"role": "student", "text": voice_q})

            if st.session_state.stream_enabled:
                st.markdown('<div style="color:var(--muted);font-size:.8rem;margin:8px 0;">⚡ Streaming answer…</div>', unsafe_allow_html=True)
                placeholder = st.empty()
                answer = run_chain_streaming(VOICE_TUTOR_PROMPT, {
                    "context": context, "question": voice_q, "history": history_str
                }, placeholder)
            else:
                with st.spinner("🎤 Tutor is thinking…"):
                    answer = run_chain(VOICE_TUTOR_PROMPT, {
                        "context": context, "question": voice_q, "history": history_str
                    })

            st.session_state.voice_history.append({"role": "tutor", "text": answer})
            award_xp(6, "Voice tutor")
            check_achievements()
            st.rerun()

    # Tips
    st.markdown("---")
    st.markdown('<div class="section-label">💡 Voice Tutor Tips</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-sm" style="font-size:.85rem;line-height:1.8;color:var(--muted);">
        🎙️ <b>Browser STT</b>: Click <i>Click to Speak</i>, ask your question, then paste the transcript below.<br>
        🔊 <b>Read Aloud</b>: Click the <i>Read Aloud</i> button on any tutor reply to hear it spoken.<br>
        📱 <b>Mobile</b>: On iOS/Android, use the microphone key on your keyboard for voice input.<br>
        🤖 <b>Natural style</b>: The tutor replies in conversational spoken language — no bullet points or markdown.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 10 – STUDY MODE (Pomodoro)
# ════════════════════════════════════════════════════════════════════════════
with tab_study:
    st.markdown('<div class="section-label">⏱️ Study Mode — Pomodoro Timer</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.session_state.pomodoro_work_min = st.number_input("Work (minutes)", 5, 60, st.session_state.pomodoro_work_min, key="pom_work")
        st.session_state.pomodoro_break_min = st.number_input("Break (minutes)", 1, 30, st.session_state.pomodoro_break_min, key="pom_break")
    with col2:
        mode = st.session_state.study_timer_mode
        pom_done = st.session_state.pomodoros_done
        mode_label = "🟢 WORK SESSION" if mode == "work" else "🔵 BREAK TIME"
        mode_class = "work" if mode == "work" else "break"
        duration_min = st.session_state.pomodoro_work_min if mode == "work" else st.session_state.pomodoro_break_min
        elapsed_secs = 0
        if st.session_state.study_timer_active and st.session_state.study_start_time:
            elapsed_secs = int(time.time() - st.session_state.study_start_time)
        remaining_secs = max(0, duration_min * 60 - elapsed_secs)
        mins_left = remaining_secs // 60
        secs_left = remaining_secs % 60
        st.markdown(f"""
        <div class="timer-display {mode_class}">
            <div style="font-size:.9rem;margin-bottom:8px;letter-spacing:.15em;">{mode_label}</div>
            <div>{mins_left:02d}:{secs_left:02d}</div>
            <div style="font-size:.75rem;margin-top:8px;opacity:.6;">🍅 {pom_done} Pomodoros completed</div>
        </div>""", unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            if not st.session_state.study_timer_active:
                if st.button("▶️ Start", key="timer_start"):
                    st.session_state.study_timer_active = True
                    st.session_state.study_start_time = time.time()
                    update_streak()
                    st.rerun()
            else:
                if st.button("⏸️ Pause", key="timer_pause"):
                    st.session_state.study_timer_active = False
                    st.rerun()
        with tc2:
            if st.button("⏭️ Skip", key="timer_skip"):
                if mode == "work":
                    st.session_state.pomodoros_done += 1
                    st.session_state.study_timer_mode = "break"
                    award_xp(20)
                    st.toast("🍅 Pomodoro complete! +20 XP", icon="✅")
                else:
                    st.session_state.study_timer_mode = "work"
                    st.toast("Break over! Back to work!", icon="💪")
                st.session_state.study_start_time = time.time()
                st.session_state.study_timer_active = False
                st.rerun()
        with tc3:
            if st.button("🔄 Reset", key="timer_reset"):
                st.session_state.study_timer_active = False
                st.session_state.study_start_time = None
                st.rerun()
        if st.session_state.study_timer_active and remaining_secs == 0:
            if mode == "work":
                st.session_state.pomodoros_done += 1
                st.session_state.study_timer_mode = "break"
                award_xp(20)
            else:
                st.session_state.study_timer_mode = "work"
            st.session_state.study_start_time = time.time()
            st.rerun()
    if st.session_state.study_timer_active:
        time.sleep(1)
        st.rerun()
    st.markdown("---")
    tips = [
        "📵 Put your phone face-down and enable Do Not Disturb.",
        "💧 Drink water before you start — hydration boosts memory.",
        "✍️ Write key points by hand — it reinforces encoding.",
        "🎵 Try lo-fi or ambient music to enter flow state.",
        "🧩 Break complex topics into smaller chunks, then link them.",
        "🔁 After each Pomodoro, recall what you learned without looking.",
        "🌬️ Take 3 deep breaths before starting — it reduces anxiety.",
    ]
    st.markdown(f'<div class="card-sm" style="font-size:.9rem;line-height:1.8;">{random.choice(tips)}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 11 – MULTI-DOC
# ════════════════════════════════════════════════════════════════════════════
with tab_multi:
    st.markdown('<div class="section-label">📚 Multi-Document Analysis</div>', unsafe_allow_html=True)
    docs = st.session_state.documents
    if len(docs) < 2:
        st.markdown('<div class="card" style="text-align:center;padding:36px;color:var(--muted);">Upload at least <b>2 documents</b> in the sidebar to enable multi-document analysis.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="color:var(--muted);font-size:.85rem;margin-bottom:16px;">{len(docs)} documents loaded.</div>', unsafe_allow_html=True)
        selected_docs = st.multiselect("Select documents to analyze", list(docs.keys()), default=list(docs.keys())[:2], key="multi_doc_sel")
        analysis_type = st.selectbox("Analysis type", ["Compare & Contrast","Synthesize key themes","Find contradictions","Create unified summary","Timeline / chronology","Custom question"], key="multi_analysis_type")
        custom_q = ""
        if analysis_type == "Custom question":
            custom_q = st.text_input("Your question across documents")
        if st.button("🔬 Analyze Documents", key="btn_multi"):
            if not st.session_state.api_key:
                st.warning("Enter your API key first.")
            elif len(selected_docs) < 2:
                st.warning("Select at least 2 documents.")
            else:
                docs_text = ""
                for i, dname in enumerate(selected_docs):
                    docs_text += f"\n\n=== Document {i+1}: {dname} ===\n{chunk_text(docs[dname], 4000)}"
                question = custom_q if custom_q else analysis_type
                if st.session_state.stream_enabled:
                    st.markdown('<div class="section-label" style="margin-top:12px;">⚡ Streaming Analysis…</div>', unsafe_allow_html=True)
                    placeholder = st.empty()
                    result = run_chain_streaming(MULTI_DOC_PROMPT, {"docs": docs_text, "question": question}, placeholder)
                else:
                    with st.spinner(f"Analyzing {len(selected_docs)} documents…"):
                        result = run_chain(MULTI_DOC_PROMPT, {"docs": docs_text, "question": question})
                    st.markdown(f'<div class="card" style="margin-top:16px;"><div class="section-label">Analysis Result</div><div style="font-family:\'DM Mono\',monospace;font-size:.88rem;line-height:1.8;white-space:pre-wrap;">{result}</div></div>', unsafe_allow_html=True)
                st.session_state["multi_result"] = result
                award_xp(20)
                check_achievements()
        if st.session_state.get("multi_result") and not st.session_state.stream_enabled:
            if st.button("📝 Save to Revision Notes", key="save_multi_note"):
                st.session_state.revision_notes.append({"text": f"[Multi-Doc: {analysis_type}]\n" + st.session_state["multi_result"], "date": date.today().isoformat(), "doc": "Multi-Doc", "tags": ["multi-doc", analysis_type]})
                st.toast("Saved to revision notes!", icon="📝")

# ════════════════════════════════════════════════════════════════════════════
# TAB 12 – RAW TEXT
# ════════════════════════════════════════════════════════════════════════════
with tab_raw:
    st.markdown('<div class="section-label">Extracted Text</div>', unsafe_allow_html=True)
    doc_name = st.session_state.active_doc or "doc"
    st.markdown(f"<div style='color:var(--muted);font-size:.8rem;margin-bottom:12px;'>{len(active_text):,} characters from <b>{doc_name}</b></div>", unsafe_allow_html=True)
    st.text_area("Raw content", active_text, height=500, label_visibility="collapsed")
    st.download_button("⬇️ Download Raw Text", active_text, file_name=f"raw_{doc_name}.txt", mime="text/plain")