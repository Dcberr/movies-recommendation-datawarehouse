import streamlit as st
from data.loader import load_all_movies
from utils.helpers import (
    get_display_dataframe,
    load_stylesheet,
    render_app_navigation,
    render_page_banner,
    render_section_heading,
)

load_stylesheet()
render_app_navigation("movies")

render_page_banner(
    "Library",
    "Movies Explorer",
    "Search, browse, and review the catalog with the same presentation language as the main analytics dashboard.",
    ["Searchable catalog", "Readable metadata", "Consistent presentation"],
)

df = load_all_movies()

search = st.text_input("Search movie")

if search:
    df = df[df["title"].str.contains(search, case=False)]

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

st.dataframe(get_display_dataframe(df), use_container_width=True)
