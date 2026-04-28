# components/sidebar.py

import streamlit as st
from utils.helpers import render_app_navigation


def render_sidebar(df):
    render_app_navigation("dashboard")

    st.sidebar.markdown(
        """
        <div class="sidebar-intro">
            <p class="eyebrow">Explore</p>
            <h2>Filters</h2>
            <p>Refine the catalog by release period and audience engagement.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Genre (optional nếu bạn join thêm sau)
    # genre = st.sidebar.selectbox("Genre", ["All"])

    # Year range
    min_year = int(df["year"].min()) if df["year"].notna().any() else 1900
    max_year = int(df["year"].max()) if df["year"].notna().any() else 2025

    year_range = st.sidebar.slider(
        "Release Window",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Min votes
    min_votes = st.sidebar.slider(
        "Minimum Votes",
        min_value=0,
        max_value=int(df["num_votes"].max()),
        value=100
    )

    return {
        "year_range": year_range,
        "min_votes": min_votes
    }
