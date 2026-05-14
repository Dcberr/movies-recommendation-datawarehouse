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
from services.streaming.utils.streamlit_tracking import (
    ensure_streaming_session,
    render_debug_panel,
    track_movie_view,
    track_page_visit,
    track_rating,
)
from utils.helpers import load_stylesheet, render_page_banner, render_section_heading

st.set_page_config(page_title=APP_CONFIG["title"], layout="wide")
load_stylesheet()
ensure_streaming_session()
track_page_visit("dashboard")

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

render_section_heading(
    "Interaction",
    "Featured Movie Actions",
    "Use the controls below to generate real streaming view and rating events directly from the dashboard.",
)

featured_df = df_filtered.sort_values("weighted_rating", ascending=False).head(3)

if featured_df.empty:
    st.info("No featured titles are available for interaction in the current filter view.")
else:
    featured_cols = st.columns(len(featured_df))
    for column, (_, movie) in zip(featured_cols, featured_df.iterrows()):
        with column:
            st.markdown(
                f"""
                <div class="content-card">
                    <p class="eyebrow">Featured</p>
                    <h3>{movie['title']}</h3>
                    <p>Movie ID: {int(movie['movie_id'])}</p>
                    <p>Weighted Rating: {movie['weighted_rating']:.2f}</p>
                    <p>Votes: {int(movie['num_votes']):,}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Track View", key=f"dashboard_view_{int(movie['movie_id'])}", use_container_width=True):
                track_movie_view(movie["movie_id"], source_page="dashboard")

            with st.form(f"dashboard_rate_form_{int(movie['movie_id'])}"):
                rating_value = st.slider(
                    "Rate this movie",
                    min_value=1.0,
                    max_value=5.0,
                    value=4.0,
                    step=0.5,
                    key=f"dashboard_rating_{int(movie['movie_id'])}",
                )
                if st.form_submit_button("Stream Rating", use_container_width=True):
                    track_rating(movie["movie_id"], rating_value, source="dashboard")

st.divider()

render_table(df_filtered)

st.divider()

render_debug_panel()
