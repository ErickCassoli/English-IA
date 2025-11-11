from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="English IA", page_icon="???")
st.title("English IA Chat Coach")

message = st.text_area("Learner message", value="Hi teacher, how I can improve?")
level = st.selectbox("Level", ["A2", "B1", "B2", "C1"], index=1)
focus = st.multiselect("Focus", ["fluency", "grammar", "tone"], default=["grammar"])

if st.button("Correct message", type="primary"):
    if not message.strip():
        st.warning("Enter a message to correct.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/api/chat/correct",
                json={"message": message, "learner_level": level, "focus": focus},
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            st.success(f"Trace: {payload['trace_id']}")
            st.subheader("Corrected")
            st.write(payload["corrected"])
            st.subheader("Explanation")
            st.write(payload["explanation"])
            if payload["highlights"]:
                st.subheader("Highlights")
                st.json(payload["highlights"])
        except requests.RequestException as exc:
            st.error(f"API error: {exc}")
