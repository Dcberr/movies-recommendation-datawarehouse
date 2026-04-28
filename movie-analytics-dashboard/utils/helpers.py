from pathlib import Path

import pandas as pd
import streamlit as st


DISPLAY_COLUMN_NAMES = {
    "movie_id": "Movie ID",
    "user_id": "User ID",
    "title": "Title",
    "year": "Release Year",
    "avg_rating": "Average Rating",
    "num_votes": "Vote Count",
    "weighted_rating": "Weighted Rating",
    "genre_name": "Genre",
    "total_movies": "Total Movies",
    "avg_weighted_rating": "Average Weighted Rating",
}

APP_PAGES = [
    {
        "id": "overview",
        "path": "Overview.py",
        "label": "Overview",
        "description": "System purpose and chart guide",
    },
    {
        "id": "dashboard",
        "path": "pages/1_📊_Dashboard.py",
        "label": "Dashboard",
        "description": "KPI snapshot and core analytics",
    },
    {
        "id": "movies",
        "path": "pages/2_🎬_Movies.py",
        "label": "Movies",
        "description": "Browse the cleaned movie catalog",
    },
    {
        "id": "trends",
        "path": "pages/3_📈_Trends.py",
        "label": "Trends",
        "description": "Release-year performance view",
    },
    {
        "id": "ai_recommendation",
        "path": "pages/4_🤖_AI_Recommendation.py",
        "label": "AI Recommendation",
        "description": "Natural-language movie discovery",
    },
]


def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def safe_filter(df, column, value):
    if value:
        return df[df[column] == value]
    return df


def normalize_year(df):
    return df[df["year"].notna()]


def load_stylesheet():
    stylesheet_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    with stylesheet_path.open() as stylesheet:
        st.markdown(f"<style>{stylesheet.read()}</style>", unsafe_allow_html=True)


def render_page_banner(eyebrow, title, description, meta_items=None):
    meta_markup = ""
    if meta_items:
        chips = "".join(f"<span>{item}</span>" for item in meta_items)
        meta_markup = f'<div class="hero-meta">{chips}</div>'

    st.markdown(
        f"""
        <section class="hero-panel">
            <div>
                <p class="eyebrow">{eyebrow}</p>
                <h1>{title}</h1>
                <p class="hero-copy">{description}</p>
            </div>
            {meta_markup}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="section-heading">
            <p class="eyebrow">{eyebrow}</p>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_navigation(active_page_id):
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <p class="eyebrow">Navigation</p>
            <h2>Movie Analytics</h2>
            <p>Move across insight views, catalog exploration, and AI-driven recommendation workflows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="sidebar-nav-section">
            <p class="sidebar-nav-section__label">Workspace</p>
            <span class="sidebar-nav-section__count">5 views</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, page in enumerate(APP_PAGES, start=1):
        if page["id"] == active_page_id:
            st.sidebar.markdown(
                f"""
                <div class="nav-card active">
                    <div class="nav-card__index">{index:02d}</div>
                    <div class="nav-card__eyebrow">Current View</div>
                    <div class="nav-card__title">{page["label"]}</div>
                    <div class="nav-card__description">{page["description"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.sidebar.markdown(
                f"""
                <div class="nav-item-meta">
                    <span class="nav-item-meta__index">{index:02d}</span>
                    <span class="nav-item-meta__label">{page["description"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.sidebar.button(page["label"], key=f"nav_{page['id']}", use_container_width=True):
                st.switch_page(page["path"])
            st.sidebar.markdown(
                f"""
                <div class="nav-support">
                    <div class="nav-support__hint">Open {page["label"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def get_display_dataframe(df):
    renamed_df = df.rename(columns=DISPLAY_COLUMN_NAMES).copy()

    if "Release Year" in renamed_df.columns:
        renamed_df["Release Year"] = renamed_df["Release Year"].astype("Int64")

    return renamed_df
