import streamlit as st
from src.database import init_db, get_connection, list_topics, add_topic, add_note, query_df, delete_note

st.set_page_config(page_title="Notes | RecallMap", page_icon="📝", layout="wide")
init_db()
st.title("📝 Notes & Topics")
st.caption("Create topics and keep your study notes organized.")

with st.expander("Create a subject and topic", expanded=not bool(list_topics())):
    with st.form("topic_form", clear_on_submit=True):
        subject = st.text_input("Subject", placeholder="e.g. Operating Systems")
        topic = st.text_input("Topic", placeholder="e.g. CPU Scheduling")
        submitted = st.form_submit_button("Save topic", type="primary")
    if submitted:
        try:
            add_topic(topic, subject)
            st.success("Topic saved.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

topics = list_topics()
if not topics:
    st.info("Create your first subject and topic above.")
    st.stop()

with st.expander("Add a note", expanded=True):
    with st.form("note_form", clear_on_submit=True):
        topic_options = {f"{r['subject']} · {r['name']} (ID {r['id']})": r['id'] for r in topics}
        chosen = st.selectbox("Topic", list(topic_options))
        title = st.text_input("Note title")
        content = st.text_area("Note content", height=160, placeholder="Write your explanation, examples, and key points...")
        submitted = st.form_submit_button("Save note", type="primary")
    if submitted:
        try:
            add_note(topic_options[chosen], title, content)
            st.success("Note saved to SQLite.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

st.markdown("### Your notes")
search = st.text_input("Search notes", placeholder="Search title, content, subject, or topic")
notes = query_df("""SELECT n.id, t.subject, t.name AS topic, n.title, n.content, n.created_at
FROM notes n JOIN topics t ON t.id=n.topic_id ORDER BY n.created_at DESC""")
if search:
    mask = notes.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
    notes = notes[mask]
if notes.empty:
    st.caption("No matching notes yet.")
else:
    for _, row in notes.iterrows():
        with st.expander(f"{row['title']} · {row['subject']} / {row['topic']}"):
            st.write(row["content"])
            st.caption(f"Created: {row['created_at']} · Note ID: {row['id']}")
            if st.button("Delete note", key=f"delete_note_{row['id']}"):
                delete_note(row["id"])
                st.success("Note deleted.")
                st.rerun()

st.markdown("### Topics")
st.dataframe(query_df("SELECT id, subject, name AS topic, created_at FROM topics ORDER BY subject, name"), use_container_width=True, hide_index=True)
