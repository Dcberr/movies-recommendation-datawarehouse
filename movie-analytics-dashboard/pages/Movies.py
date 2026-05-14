import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import pandas as pd
import streamlit as st
from data.loader import load_all_movies
from services.streaming.utils.streamlit_tracking import (
    ensure_streaming_session,
    render_debug_panel,
    track_movie_view,
    track_page_visit,
    track_rating,
    track_search,
)
from utils.helpers import (
    get_display_dataframe,
    load_stylesheet,
    render_app_navigation,
    render_page_banner,
    render_section_heading,
)

load_stylesheet()
render_app_navigation("movies")
ensure_streaming_session()
track_page_visit("movies")

render_page_banner(
    "Library",
    "Movies Explorer",
    "Search, browse, and review the catalog with the same presentation language as the main analytics dashboard.",
    ["Searchable catalog", "Readable metadata", "Consistent presentation"],
)

df = load_all_movies()

if "movies_search_query" not in st.session_state:
    st.session_state.movies_search_query = ""

with st.form("movies_search_form"):
    search = st.text_input(
        "Search movie",
        value=st.session_state.movies_search_query,
        placeholder="Search by movie title",
    )
    search_submitted = st.form_submit_button("Search Catalog", use_container_width=True)

if search_submitted:
    st.session_state.movies_search_query = search
    if search.strip():
        track_search(search, source_page="movies")

active_search = st.session_state.movies_search_query

if active_search:
    df = df[df["title"].str.contains(active_search, case=False, na=False)]

render_section_heading(
    "Browse",
    "Movie Catalog",
    "Use the search bar to narrow the title list and inspect the cleaned dataset fields.",
)

summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.markdown(
    f"""
    <div class="metric-card">
        <p>Titles</p>
        <h3>{df['movie_id'].nunique():,}</h3>
        <span>Movies matching the current search</span>
    </div>
    """,
    unsafe_allow_html=True,
)
summary_col2.markdown(
    f"""
    <div class="metric-card">
        <p>Average Rating</p>
        <h3>{df['avg_rating'].mean():.2f}</h3>
        <span>Mean rating across displayed records</span>
    </div>
    """,
    unsafe_allow_html=True,
)
summary_col3.markdown(
    f"""
    <div class="metric-card">
        <p>Vote Count</p>
        <h3>{int(df['num_votes'].sum()):,}</h3>
        <span>Total audience votes in view</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

render_section_heading(
    "Streaming Actions",
    "Interactive Movie Cards",
    "These cards write real view and rating events into the streaming tables so the realtime dashboard can react immediately.",
)

interactive_df = df.sort_values("weighted_rating", ascending=False).head(6)

if interactive_df.empty:
    st.info("No movies are available for the current search.")
else:
    movie_rows = [interactive_df.iloc[i:i + 3] for i in range(0, len(interactive_df), 3)]
    for row_index, movie_chunk in enumerate(movie_rows):
        columns = st.columns(len(movie_chunk))
        for column, (_, movie) in zip(columns, movie_chunk.iterrows()):
            movie_id = int(movie["movie_id"])
            with column:
                st.markdown(
                    f"""
                    <div class="content-card">
                        <p class="eyebrow">Movie</p>
                        <h3>{movie['title']}</h3>
                        <p>Movie ID: {movie_id}</p>
                        <p>Release Year: {int(movie['year']) if pd.notna(movie['year']) else 'Unknown'}</p>
                        <p>Average Rating: {movie['avg_rating']:.2f}</p>
                        <p>Weighted Rating: {movie['weighted_rating']:.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button("View Movie", key=f"movies_view_{row_index}_{movie_id}", use_container_width=True):
                    track_movie_view(movie_id, source_page="movies")

                with st.form(f"movies_rate_form_{row_index}_{movie_id}"):
                    rating_value = st.slider(
                        "Rate movie",
                        min_value=1.0,
                        max_value=5.0,
                        value=4.0,
                        step=0.5,
                        key=f"movies_rating_slider_{row_index}_{movie_id}",
                    )
                    if st.form_submit_button("Stream Rating", use_container_width=True):
                        track_rating(movie_id, rating_value, source="movies")

st.divider()

st.dataframe(get_display_dataframe(df), use_container_width=True)

st.divider()

render_debug_panel()
