import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import streamlit as st

from config.settings import APP_CONFIG
from data.loader import load_all_movies
from components.sidebar import render_sidebar
from components.kpi import render_kpis
from components.charts import *
from components.tables import render_table
from services.analytics import apply_filters
from utils.helpers import load_stylesheet, render_page_banner, render_section_heading

st.set_page_config(page_title=APP_CONFIG["title"], layout="wide")
load_stylesheet()

render_page_banner(
    "Dashboard",
    APP_CONFIG["title"],
    "Explore release performance, audience behavior, and long-term rating trends through a cleaner analytical workspace.",
    ["Curated film intelligence", "Interactive filtering", "Executive-ready visuals"],
)

df = load_all_movies()

filters = render_sidebar(df)
df_filtered = apply_filters(df, filters)

render_section_heading(
    "Snapshot",
    "Current Selection",
    "Key performance indicators update instantly from the active filters.",
)
render_kpis(df_filtered)

st.divider()

render_section_heading(
    "Analysis",
    "Ratings and Audience Patterns",
    "Compare top titles, distribution, engagement, and historical movement in one view.",
)

col1, col2 = st.columns(2)

with col1:
    plot_top_movies(df_filtered)
    plot_votes_vs_rating(df_filtered)

with col2:
    plot_rating_distribution(df_filtered)
    plot_yearly_trend(df_filtered)

st.divider()

render_table(df_filtered)
