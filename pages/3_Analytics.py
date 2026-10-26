import streamlit as st
from src.database import init_db, query_df
from src.analytics import load_attempts, get_metrics, topic_summary, score_trend

st.set_page_config(page_title="Analytics | RecallMap", page_icon="📊", layout="wide")
init_db()
st.title("📊 Learning Analytics")
st.caption("Explore recorded recall performance. Scores are self-assessments, not objective memory measurements.")
df = load_attempts()
metrics = get_metrics(df)
a, b, c = st.columns(3)
a.metric("Recall attempts", metrics["attempts"])
b.metric("Average recall score", f"{metrics['average_score']:.1f}%")
c.metric("Topics reviewed", metrics["topics_reviewed"])
if df.empty:
    st.info("Complete a recall quiz to populate your analytics.")
    st.stop()
fig = score_trend(df)
if fig is not None:
    st.plotly_chart(fig, use_container_width=True)
st.subheader("Topic performance")
summary = topic_summary(df)
st.bar_chart(summary, x="topic", y="average_score", horizontal=True)
st.dataframe(summary, use_container_width=True, hide_index=True)
st.subheader("Topics to consider reviewing")
latest = df.sort_values("attempted_at").groupby("topic", as_index=False).tail(1).copy()
latest["latest_score_out_of_100"] = latest["score"] * 20
weak = latest[latest["score"] <= 3][["subject", "topic", "score", "attempted_at"]]
if weak.empty:
    st.success("No topics currently meet the basic review rule (latest score ≤ 3). Keep reviewing periodically.")
else:
    st.dataframe(weak.sort_values("score"), use_container_width=True, hide_index=True)
st.download_button("Export recall history as CSV", df.to_csv(index=False).encode("utf-8"), "recall_history.csv", "text/csv")
