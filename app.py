"""Streamlit web app.  Run:  streamlit run app.py"""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.document_loader import load_json_entries
from src.rag_pipeline import Conversation, WellnessCompanion

st.set_page_config(page_title="Ember - Wellness Companion", page_icon="🌱", layout="wide")


@st.cache_resource
def get_companion() -> WellnessCompanion:
    return WellnessCompanion()


companion = get_companion()
if "convo" not in st.session_state:
    st.session_state.convo = Conversation()
if "consented" not in st.session_state:
    st.session_state.consented = False

# ---------- Consent gate ----------
if not st.session_state.consented:
    st.title("🌱 Ember - AI Companion for Emotional Wellness")
    st.markdown(
        """
**Before you begin**

- Ember is an AI companion for self-reflection and evidence-informed coping skills.
- It is **not** a therapist, medical provider, or crisis service and cannot diagnose or treat.
- Chat messages are sent to the OpenAI API to generate replies. Journal entries and
  mood logs are stored **only on this device** and can be exported or deleted at any time.
- **If you are in crisis:** call **911**, or call/text **988** (US Suicide & Crisis Lifeline),
  or visit **findahelpline.com**.
"""
    )
    if st.checkbox("I understand and want to continue (I am 18 or older)."):
        if st.button("Start"):
            st.session_state.consented = True
            st.rerun()
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("🌱 Ember")
    st.caption(f"Mode: {'OpenAI · ' + companion.cfg.llm_model if companion.llm.online else 'Offline demo'}")
    st.error("Crisis? Call/text **988** (US) or **911**. Elsewhere: findahelpline.com")
    if st.button("New conversation"):
        st.session_state.convo = Conversation()
        st.rerun()

tab_chat, tab_toolkit, tab_journal, tab_insights, tab_privacy = st.tabs(
    ["💬 Chat", "🧰 Toolkit", "📓 Journal", "📈 Insights", "🔒 Privacy"])

# ---------- Chat ----------
with tab_chat:
    convo: Conversation = st.session_state.convo
    if not convo.transcript:
        st.info("Hi, I'm Ember. How are you feeling today? You can share as much or as little as you like.")
    for m in convo.transcript:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Share what's on your mind..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Ember is reflecting..."):
                r = companion.chat(prompt, convo)
            st.markdown(r.text)
            with st.expander(f"Detected emotion: {r.emotion} · sources used"):
                st.write(f"Intensity: {r.intensity}")
                for s in r.sources:
                    st.write(f"- {s['title']} (similarity {s['score']})")

# ---------- Toolkit (structured JSON knowledge) ----------
@st.cache_data
def load_toolkit() -> list[dict]:
    entries = []
    for path in sorted(companion.cfg.documents_dir.glob("*.json")):
        entries.extend(load_json_entries(path))
    return entries


with tab_toolkit:
    st.subheader("Coping toolkit")
    toolkit = load_toolkit()
    if not toolkit:
        st.write("No JSON toolkit entries found in data/wellness_documents.")
    else:
        all_emotions = sorted({e for t in toolkit for e in t.get("emotions", [])})
        c1, c2 = st.columns([1, 2])
        with c1:
            chosen = st.multiselect("Filter by feeling", all_emotions)
        with c2:
            search = st.text_input("Search", placeholder="e.g. panic, sleep, procrastination")
        shown = [t for t in toolkit
                 if (not chosen or set(chosen) & set(t.get("emotions", [])))
                 and (not search or search.lower() in json.dumps(t).lower())]
        st.caption(f"{len(shown)} of {len(toolkit)} strategies")
        for t in shown:
            mins = t.get("duration_minutes")
            label = f"{t['title']}" + (f" · ~{mins} min" if mins else "")
            with st.expander(label):
                st.write(t.get("summary", ""))
                for i, step in enumerate(t.get("steps", []), 1):
                    st.markdown(f"{i}. {step}")
                if t.get("when_to_seek_help"):
                    st.warning(t["when_to_seek_help"])
                if t.get("emotions"):
                    st.caption("Helpful for: " + ", ".join(t["emotions"]))

# ---------- Journal ----------
with tab_journal:
    st.subheader("Private journal")
    st.write(f"**Prompt:** {companion.journal.reflection_prompt()}")
    with st.form("journal", clear_on_submit=True):
        text = st.text_area("Write freely...", height=200)
        mood = st.slider("How is your mood right now? (1 = very low, 10 = great)", 1, 10, 5)
        if st.form_submit_button("Save entry") and text.strip():
            e = companion.journal.add_entry(companion.user_id, text, "journal", mood)
            st.success(f"Saved. It sounds like {e['emotion']} came up. "
                       f"Reflect: {companion.journal.reflection_prompt(e['emotion'])}")
    for e in reversed(companion.journal.entries(companion.user_id, 30, kind="journal")[-10:]):
        with st.expander(f"{e['created_at']} · {e['emotion']} · mood {e['mood_rating']}"):
            st.write(e["text"])

# ---------- Insights ----------
with tab_insights:
    st.subheader("Your patterns (last 30 days)")
    rows = companion.journal.entries(companion.user_id, 30)
    if not rows:
        st.write("No data yet. Chat or journal to see patterns here.")
    else:
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["created_at"]).dt.date
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Emotions noticed**")
            st.bar_chart(df["emotion"].value_counts())
        with c2:
            st.write("**Self-rated mood (journal)**")
            mood = df.dropna(subset=["mood_rating"]).groupby("date")["mood_rating"].mean()
            if len(mood):
                st.line_chart(mood)
            else:
                st.write("Add a mood rating in the Journal tab.")
        s = companion.journal.mood_summary(companion.user_id, 7)
        if s["count"]:
            st.info(f"This week the emotion that came up most was **{s['top_emotion']}**. "
                    f"{companion.journal.reflection_prompt(s['top_emotion'])}")

# ---------- Privacy ----------
with tab_privacy:
    st.subheader("Your data")
    st.download_button("Export my data (JSON)", companion.journal.export(companion.user_id),
                       file_name="my_wellness_data.json")
    if st.button("Delete all my data", type="primary"):
        n = companion.journal.delete_all(companion.user_id)
        st.session_state.convo = Conversation()
        st.success(f"Deleted {n} records.")
