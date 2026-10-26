# RecallMap 🧠

A visual memory analytics engine built with Python, Streamlit, Pandas, Plotly, NetworkX, and SQLite.

## Features
- Topic and notes management
- Recall questions with answer reveal and self-scored attempts
- SQLite persistence
- Recall analytics and topic performance charts
- Rule-based review suggestions
- Manually linked knowledge graph
- CSV export

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The database is created automatically at `data/recallmap.db`. It is excluded from Git by `.gitignore`.

## Notes
Recall scores are self-assessments. The current graph uses manually saved links; it does not automatically infer semantic relationships. This is a local single-user starter app, not a multi-user authenticated service.
