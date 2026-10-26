import streamlit as st
from src.database import init_db, list_topics, add_question, query_df, save_attempt, delete_question

st.set_page_config(page_title="Recall Quiz | RecallMap", page_icon="🧠", layout="wide")
init_db()
st.title("🧠 Recall Quiz")
st.caption("Try to answer from memory before revealing the saved answer.")
topics = list_topics()
if not topics:
    st.info("First, create a topic in the Notes page.")
    st.stop()

with st.expander("Create a recall question", expanded=False):
    with st.form("question_form", clear_on_submit=True):
        opts = {f"{r['subject']} · {r['name']} (ID {r['id']})": r['id'] for r in topics}
        chosen = st.selectbox("Topic", list(opts))
        question = st.text_area("Question / prompt", placeholder="What is the difference between a process and a thread?")
        answer = st.text_area("Expected answer", placeholder="Write the key points you want to recall.")
        submit = st.form_submit_button("Save question", type="primary")
    if submit:
        try:
            add_question(opts[chosen], question, answer)
            st.success("Question saved.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

questions = query_df("""SELECT q.id, q.question, q.answer, t.subject, t.name AS topic
FROM questions q JOIN topics t ON t.id=q.topic_id ORDER BY t.subject, t.name, q.id""")
if questions.empty:
    st.info("Create your first question above, then it will appear here.")
    st.stop()

st.markdown("### Practice")
filter_options = ["All topics"] + sorted(questions["topic"].unique().tolist())
filter_topic = st.selectbox("Filter by topic", filter_options)
if filter_topic != "All topics":
    questions = questions[questions["topic"] == filter_topic]
for _, row in questions.iterrows():
    with st.container(border=True):
        st.caption(f"{row['subject']} · {row['topic']} · Question #{row['id']}")
        st.markdown(f"**{row['question']}**")
        st.text_area("Think through your answer here (not auto-graded)", key=f"attempt_text_{row['id']}", height=90)
        reveal_key = f"reveal_{row['id']}"
        if st.button("Reveal answer", key=f"reveal_btn_{row['id']}"):
            st.session_state[reveal_key] = True
        if st.session_state.get(reveal_key, False):
            st.success("Expected answer")
            st.write(row["answer"])
            with st.form(f"score_form_{row['id']}"):
                score = st.slider("How well did you recall it?", min_value=0, max_value=5, value=3, key=f"score_{row['id']}")
                save = st.form_submit_button("Save recall score")
            if save:
                save_attempt(row["id"], score)
                st.success("Recall attempt saved.")
                st.rerun()
        with st.expander("Attempt history"):
            history = query_df("SELECT score, attempted_at FROM recall_attempts WHERE question_id=? ORDER BY attempted_at DESC", (int(row["id"]),))
            if history.empty:
                st.caption("No attempts recorded yet.")
            else:
                st.dataframe(history, use_container_width=True, hide_index=True)
        if st.button("Delete question", key=f"delete_question_{row['id']}"):
            delete_question(row["id"])
            st.success("Question and its attempt history deleted.")
            st.rerun()
