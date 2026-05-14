import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import streamlit as st
import plotly.express as px
from data.loader import load_all_movies
from utils.helpers import get_display_dataframe, load_stylesheet, render_app_navigation, render_page_banner, render_section_heading

load_stylesheet()
render_app_navigation("trends")

render_page_banner(
    "Timeline",
    "Trends",
    "Track how weighted audience reception evolves across release years with the same analytical styling as the main dashboard.",
    ["Long-term movement", "Release-year focus", "Presentation-ready trend view"],
)

df = load_all_movies()

df_trend = df.groupby("year")["weighted_rating"].mean().reset_index()

render_section_heading(
    "Trendline",
    "Weighted Rating Over Time",
    "The chart highlights how aggregate audience reception shifts between release years.",
)

fig = px.line(
    df_trend,
    x="year",
    y="weighted_rating",
    title="Weighted Rating Trend",
    labels={"year": "Release Year", "weighted_rating": "Weighted Rating"},
)
fig.update_traces(line=dict(color="#6c88c4", width=3))
fig.update_layout(
    height=420,
    autosize=True,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#11161d",
    font=dict(color="#f3efe6", family="Inter, sans-serif"),
    title=dict(font=dict(size=18, color="#f5ede0")),
    margin=dict(l=12, r=12, t=56, b=12),
)
fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)
fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"responsive": True, "displaylogo": False},
)

st.divider()

render_section_heading(
    "Reference",
    "Yearly Summary",
    "The table below mirrors the chart with clearer business-friendly column names.",
)

st.dataframe(get_display_dataframe(df_trend), use_container_width=True)
