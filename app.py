import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.database import init_db, query_df

st.set_page_config(
    page_title="RecallMap | Learning OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

st.markdown("""
<style>
    .block-container { padding-top: 2.0rem; padding-bottom: 3rem; max-width: 1440px; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(148,163,184,.14); }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(139,124,255,.11), rgba(23,27,38,.55));
        border: 1px solid rgba(148,163,184,.16); padding: 18px 20px;
        border-radius: 16px; min-height: 124px;
    }
    [data-testid="stMetricLabel"] p { color: #A8B1C4; font-size: .86rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; }
    .eyebrow { color: #A99EFF; text-transform: uppercase; letter-spacing: .16em;
        font-size: .73rem; font-weight: 700; margin-bottom: .45rem; }
    .hero-title { font-size: clamp(2.1rem, 4vw, 3.25rem); line-height: 1.06;
        font-weight: 800; letter-spacing: -.045em; margin: 0; }
    .hero-copy { color: #A8B1C4; font-size: 1.02rem; margin-top: .7rem; max-width: 680px; }
    .hero-card { padding: 30px 32px; border: 1px solid rgba(139,124,255,.25);
        border-radius: 22px; background: radial-gradient(circle at 85% 20%, rgba(139,124,255,.2), transparent 34%),
        linear-gradient(135deg, rgba(25,29,43,.98), rgba(15,18,28,.98)); margin-bottom: 1.35rem; }
    .section-kicker { color: #A8B1C4; font-size: .84rem; margin-top: -.5rem; }
    .mini-card { background: rgba(23,27,38,.72); border: 1px solid rgba(148,163,184,.15);
        border-radius: 16px; padding: 18px 20px; min-height: 142px; }
    .mini-icon { font-size: 1.35rem; margin-bottom: .5rem; }
    .mini-title { font-weight: 700; font-size: 1.02rem; margin-bottom: .25rem; }
    .mini-copy { color: #A8B1C4; font-size: .87rem; line-height: 1.45; }
    div[data-testid="stButton"] button { border-radius: 10px; }
    hr { border-color: rgba(148,163,184,.14); }
</style>
""", unsafe_allow_html=True)

topics_count = int(query_df("SELECT COUNT(*) AS n FROM topics").iloc[0]["n"])
notes_count = int(query_df("SELECT COUNT(*) AS n FROM notes").iloc[0]["n"])
questions_count = int(query_df("SELECT COUNT(*) AS n FROM questions").iloc[0]["n"])
attempts_count = int(query_df("SELECT COUNT(*) AS n FROM recall_attempts").iloc[0]["n"])

attempts = query_df("""
    SELECT t.id AS topic_id, t.subject, t.name AS topic,
           q.id AS question_id, q.question, a.score, a.attempted_at
    FROM recall_attempts a
    JOIN questions q ON q.id = a.question_id
    JOIN topics t ON t.id = q.topic_id
    ORDER BY a.attempted_at
""")
recent = query_df("""
    SELECT t.subject, t.name AS topic, q.question, a.score, a.attempted_at
    FROM recall_attempts a
    JOIN questions q ON q.id = a.question_id
    JOIN topics t ON t.id = q.topic_id
    ORDER BY a.attempted_at DESC, a.id DESC LIMIT 6
""")

left, right = st.columns([4.5, 1.3], vertical_alignment="center")
with left:
    st.markdown("""
    <div class="hero-card">
      <div class="eyebrow">YOUR PERSONAL LEARNING OS</div>
      <div class="hero-title">Make knowledge<br>stick. <span style="color:#A99EFF">See your progress.</span></div>
      <div class="hero-copy">A home for your notes, active recall, and the connections between ideas.
      Build a clearer picture of what you know and what deserves another look.</div>
    </div>
    """, unsafe_allow_html=True)
with right:
    st.markdown("<div style='text-align:center;font-size:5rem;padding:12px 0 22px'>🧠</div>", unsafe_allow_html=True)
    st.caption("Small sessions. Stronger recall.")

st.markdown("<div class='eyebrow'>AT A GLANCE</div>", unsafe_allow_html=True)
a, b, c, d = st.columns(4, gap="medium")
a.metric("Topics", topics_count, help="Concepts organized across your subjects")
b.metric("Study notes", notes_count, help="Notes saved in your local database")
c.metric("Recall questions", questions_count, help="Prompts available for self-testing")
d.metric("Recall attempts", attempts_count, help="Saved self-assessment attempts")

st.divider()

main_col, side_col = st.columns([1.65, 1], gap="large")
with main_col:
    st.markdown("### 📈 Recall pulse")
    st.markdown("<div class='section-kicker'>Your recorded self-assessment scores over time</div>", unsafe_allow_html=True)
    if attempts.empty:
        st.info("Your chart will appear after your first recall attempt.")
        st.markdown("**Start with one topic, one question, and one honest score.** That's enough to begin building your learning history.")
    else:
        chart_df = attempts.copy()
        chart_df["attempted_at"] = __import__("pandas").to_datetime(chart_df["attempted_at"], errors="coerce")
        chart_df = chart_df.dropna(subset=["attempted_at"])
        if chart_df.empty:
            st.info("Saved attempts do not have readable timestamps yet.")
        else:
            fig = px.line(
                chart_df, x="attempted_at", y="score", color="topic", markers=True,
                custom_data=["subject", "question"],
                labels={"attempted_at": "Date", "score": "Recall score (0–5)", "topic": "Topic"},
            )
            fig.update_traces(hovertemplate="%{customdata[0]} · %{fullData.name}<br>Score: %{y}/5<extra></extra>")
            fig.update_layout(
                height=330, margin=dict(l=8, r=8, t=18, b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#A8B1C4"), legend_title_text="Topic",
                hoverlabel=dict(bgcolor="#171B26", font_color="#F0F2F6"),
            )
            fig.update_yaxes(range=[0, 5], dtick=1, gridcolor="rgba(148,163,184,.12)", zeroline=False)
            fig.update_xaxes(gridcolor="rgba(148,163,184,.08)", zeroline=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("### 🕘 Recent recall activity")
    if recent.empty:
        st.caption("No attempts recorded yet. Your first quiz will show up here.")
    else:
        display = recent.copy()
        display["Score"] = display["score"].astype(int).astype(str) + " / 5"
        display = display.rename(columns={"subject": "Subject", "topic": "Topic", "question": "Question", "attempted_at": "Attempted"})
        st.dataframe(display[["Subject", "Topic", "Question", "Score", "Attempted"]], use_container_width=True, hide_index=True)

with side_col:
    st.markdown("### 🎯 Focus for your next session")
    st.markdown("<div class='section-kicker'>A few useful next moves</div>", unsafe_allow_html=True)
    if attempts.empty:
        st.markdown("""
        <div class="mini-card"><div class="mini-icon">📝</div><div class="mini-title">Capture a concept</div>
        <div class="mini-copy">Start with a subject and one topic. Keep notes short enough to revisit.</div></div><br>
        <div class="mini-card"><div class="mini-icon">🧠</div><div class="mini-title">Make it retrievable</div>
        <div class="mini-copy">Turn one important idea into a question, then try answering from memory.</div></div>
        """, unsafe_allow_html=True)
    else:
        latest = attempts.sort_values("attempted_at").groupby(["topic_id", "topic", "subject"], as_index=False).tail(1).copy()
        weak = latest[latest["score"] <= 3].sort_values("score")
        if weak.empty:
            st.success("Your latest recorded scores are looking strong. Keep revisiting topics over time to check that they stay familiar.")
        else:
            for _, row in weak.head(4).iterrows():
                score = int(row["score"])
                st.markdown(f"<div class='mini-card' style='min-height:0;margin-bottom:10px'><div class='mini-title'>{row['topic']}</div><div class='mini-copy'>{row['subject']} · Latest recall: <b>{score}/5</b></div></div>", unsafe_allow_html=True)
            st.caption("Suggested focus based on your latest self-assessed score, not a prediction of memory.")

    st.markdown("### 🧭 Your workspace")
    st.markdown("""
    <div class="mini-card"><div class="mini-icon">📚</div><div class="mini-title">Notes & Topics</div>
    <div class="mini-copy">Organize your learning into subjects and concepts.</div></div><br>
    <div class="mini-card"><div class="mini-icon">🕸️</div><div class="mini-title">Knowledge Map</div>
    <div class="mini-copy">Connect concepts and see how your ideas relate.</div></div>
    """, unsafe_allow_html=True)
    st.caption("Use the pages in the sidebar to open each workspace.")

st.divider()
st.markdown("<div style='text-align:center;color:#7F899D;font-size:.8rem'>RECALLMAP · Learn deliberately · Recall actively · Connect ideas</div>", unsafe_allow_html=True)
