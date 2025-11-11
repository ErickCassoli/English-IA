from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

API_URL = os.getenv("API_URL") or st.secrets.get("api_url", "http://localhost:8000")

st.set_page_config(page_title="English IA", page_icon="🗣️")
st.title("English IA Demo")


def call_api(method: str, path: str, **kwargs) -> dict[str, Any] | None:
    url = f"{API_URL.rstrip('/')}{path}"
    try:
        response = requests.request(method, url, timeout=15, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:  # pragma: no cover - UI helper
        st.error(f"API error: {exc}")
        return None


tab_chat, tab_stats = st.tabs(["Chat Corrector", "Stats"])

with tab_chat:
    st.subheader("Chat correction")
    message = st.text_area("Learner message", height=150)
    level = st.selectbox("Learner level", ["A2", "B1", "B2", "C1"], index=1)
    focus = st.multiselect("Focus tags", ["fluency", "grammar", "pronunciation", "tone"])
    if st.button("Correct message", type="primary"):
        if not message.strip():
            st.warning("Please enter a message to correct.")
        else:
            payload = {"message": message, "learner_level": level, "focus": focus}
            data = call_api("POST", "/api/chat/correct", json=payload)
            if data:
                st.success(f"Trace ID: {data['trace_id']}")
                st.markdown("### Corrected")
                st.write(data["corrected"])
                st.markdown("### Explanation")
                st.write(data["explanation"])
                st.markdown("### Highlights")
                st.json(data["highlights"])

with tab_stats:
    st.subheader("Usage stats")
    if st.button("Refresh stats"):
        stats = call_api("GET", "/api/stats/summary")
        if stats:
            st.metric("Chats", stats["chats"])
            st.metric("Quizzes", stats["quizzes"])
            st.metric("Flashcard Reviews", stats["flashcards"])
            st.metric("Flashcards Due", stats["flashcards_due"])
            st.metric("Total Flashcards", stats["total_flashcards"])
