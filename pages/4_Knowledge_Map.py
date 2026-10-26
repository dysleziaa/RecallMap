import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from src.database import init_db, list_topics, add_topic_link, query_df

st.set_page_config(page_title="Knowledge Map | RecallMap", page_icon="🕸️", layout="wide")
init_db()
st.title("🕸️ Knowledge Map")
st.caption("Connect concepts you consider related. Edges represent links you add manually.")
topics = list_topics()
if len(topics) < 2:
    st.info("Create at least two topics in Notes to connect them here.")
    st.stop()
opts = {f"{r['subject']} · {r['name']} (ID {r['id']})": r['id'] for r in topics}
with st.expander("Connect two topics", expanded=True):
    with st.form("link_form"):
        source_label = st.selectbox("From topic", list(opts), key="source_topic")
        target_label = st.selectbox("Related topic", list(opts), index=1, key="target_topic")
        relationship = st.text_input("Relationship label", value="related", placeholder="prerequisite, part of, related")
        submitted = st.form_submit_button("Save connection", type="primary")
    if submitted:
        try:
            add_topic_link(opts[source_label], opts[target_label], relationship)
            st.success("Connection saved.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

topics_df = query_df("SELECT id, name, subject FROM topics")
links_df = query_df("SELECT source_topic_id, target_topic_id, relationship FROM topic_links")
graph = nx.Graph()
for _, row in topics_df.iterrows():
    graph.add_node(int(row.id), label=row["name"], subject=row["subject"])
for _, row in links_df.iterrows():
    graph.add_edge(int(row.source_topic_id), int(row.target_topic_id), relationship=row.relationship)
if graph.number_of_nodes():
    pos = nx.spring_layout(graph, seed=42)
    edge_x, edge_y = [], []
    for u, v in graph.edges():
        edge_x += [pos[u][0], pos[v][0], None]
        edge_y += [pos[u][1], pos[v][1], None]
    node_x = [pos[n][0] for n in graph.nodes()]
    node_y = [pos[n][1] for n in graph.nodes()]
    labels = [graph.nodes[n]["label"] for n in graph.nodes()]
    subjects = [graph.nodes[n]["subject"] for n in graph.nodes()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", text=labels, textposition="top center",
                             customdata=subjects, hovertemplate="%{text}<br>%{customdata}<extra></extra>",
                             marker=dict(size=20), showlegend=False))
    fig.update_layout(title="Your knowledge map", xaxis=dict(visible=False), yaxis=dict(visible=False),
                      margin=dict(l=20, r=20, t=60, b=20), height=550)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{graph.number_of_nodes()} topics · {graph.number_of_edges()} connections")
if not links_df.empty:
    st.subheader("Saved connections")
    st.dataframe(links_df, use_container_width=True, hide_index=True)
