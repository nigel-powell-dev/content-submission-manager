import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Stratford Oaks | Content Submissions", page_icon="🍂", layout="centered", initial_sidebar_state="collapsed")
BASE = Path(__file__).parent
DB_PATH = Path(os.environ.get("SUBMISSIONS_DB", str(BASE / "submissions.db")))
TYPES = ["Members' Weekly Update", "Non-Members' What's On", "Individual Marketing Campaign", "Club Newsletter", "Other Announcement"]

@st.cache_resource
def connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL, publication_date TEXT, notes TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
    conn.commit()
    return conn

conn = connection()

# Native Streamlit theme handles the white background and compact controls.
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    st.image(str(BASE / "logo.jpg"), width=75)
with col_title:
    st.markdown("### Content Submission Manager")
    st.caption("Stratford Oaks Golf Club")

page = st.segmented_control("View", ["My Submissions", "New Submission"], default="My Submissions", label_visibility="collapsed")

if page == "New Submission":
    st.subheader("New submission")
    st.caption("One item at a time. Provide the facts and save a draft or submit when ready.")
    with st.form("new_submission", clear_on_submit=True):
        title = st.text_input("What is this about?", placeholder="e.g. TrackMan fitting day")
        category = st.selectbox("Intended use", TYPES)
        publication_date = st.date_input("Preferred publication date (optional)", value=None, format="DD/MM/YYYY")
        notes = st.text_area("Tell us about it", height=190, placeholder="Type or use your computer's dictation to explain your idea. Include any dates, prices, times, links and booking details you know.")
        left, right = st.columns(2)
        save = left.form_submit_button("Save Draft", use_container_width=True)
        submit = right.form_submit_button("Submit", type="primary", use_container_width=True)
    if save or submit:
        if not title.strip() or not notes.strip():
            st.error("Please enter a title and some information.")
        else:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("INSERT INTO submissions (title, category, publication_date, notes, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (title.strip(), category, publication_date.isoformat() if publication_date else "", notes.strip(), "Submitted" if submit else "Draft", now, now))
            conn.commit()
            st.success("Submission saved. Note: cloud persistence and delivery must be configured before live use.")
else:
    st.subheader("My submissions")
    rows = conn.execute("SELECT id, title, category, publication_date, notes, status FROM submissions ORDER BY updated_at DESC").fetchall()
    if not rows:
        st.info("No submissions yet. Choose New Submission to get started.")
    for item_id, title, category, publication_date, notes, status in rows:
        with st.expander(f"{title}  ·  {status}"):
            st.caption(category + (f"  |  Preferred date: {publication_date}" if publication_date else ""))
            with st.form(f"edit_{item_id}"):
                updated_title = st.text_input("Title", title, key=f"title_{item_id}")
                updated_category = st.selectbox("Intended use", TYPES, index=TYPES.index(category) if category in TYPES else 0, key=f"category_{item_id}")
                updated_notes = st.text_area("Information", notes, height=180, key=f"notes_{item_id}")
                a, b = st.columns(2)
                save = a.form_submit_button("Save Changes", use_container_width=True)
                submit = b.form_submit_button("Submit", type="primary", use_container_width=True, disabled=status == "Submitted")
            if save or submit:
                if not updated_title.strip() or not updated_notes.strip():
                    st.error("Title and information are required.")
                else:
                    conn.execute("UPDATE submissions SET title=?, category=?, notes=?, status=?, updated_at=? WHERE id=?", (updated_title.strip(), updated_category, updated_notes.strip(), "Submitted" if submit else status, datetime.now(timezone.utc).isoformat(), item_id))
                    conn.commit()
                    st.rerun()
            if status == "Submitted":
                payload = {"title": title, "intended_use": category, "publication_date": publication_date, "information": notes}
                st.download_button("Download submission", data=json.dumps(payload, indent=2, ensure_ascii=False), file_name=f"submission_{item_id}.json", mime="application/json", key=f"download_{item_id}")

st.divider()
st.caption("Prototype only · AI conversation, reliable cloud storage and email delivery are not yet connected.")
