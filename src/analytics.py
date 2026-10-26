import pandas as pd
import plotly.express as px
from src.database import query_df


def load_attempts():
    return query_df("""
        SELECT t.id AS topic_id, t.name AS topic, t.subject,
               q.id AS question_id, q.question, a.score, a.attempted_at
        FROM recall_attempts a
        JOIN questions q ON q.id = a.question_id
        JOIN topics t ON t.id = q.topic_id
        ORDER BY a.attempted_at
    """)


def get_metrics(df):
    if df.empty:
        return {"attempts": 0, "average_score": 0.0, "topics_reviewed": 0, "questions": 0}
    return {"attempts": int(len(df)), "average_score": float(df.score.mean() * 20),
            "topics_reviewed": int(df.topic.nunique()), "questions": int(df.question_id.nunique())}


def topic_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["topic", "subject", "average_score", "attempts"])
    out = df.groupby(["topic", "subject"], as_index=False).agg(
        average_score=("score", "mean"), attempts=("score", "count"))
    out["average_score"] = out["average_score"] * 20
    return out.sort_values("average_score")


def score_trend(df):
    if df.empty:
        return None
    data = df.copy()
    data["attempted_at"] = pd.to_datetime(data["attempted_at"], errors="coerce")
    data = data.dropna(subset=["attempted_at"])
    if data.empty:
        return None
    fig = px.line(data, x="attempted_at", y="score", color="topic", markers=True,
                  title="Recall performance over time",
                  labels={"attempted_at": "Attempt date", "score": "Recall score (0–5)", "topic": "Topic"})
    fig.update_yaxes(range=[0, 5], dtick=1)
    return fig
