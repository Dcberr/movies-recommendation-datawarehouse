# components/kpi.py

import streamlit as st


def render_kpis(df):
    total_movies = df["movie_id"].nunique()
    avg_rating = round(df["avg_rating"].mean(), 2)
    total_votes = int(df["num_votes"].sum())

    col1, col2, col3 = st.columns(3)

    metrics = [
        ("Catalog Size", f"{total_movies:,}", "Films in current selection"),
        ("Average Rating", f"{avg_rating:.2f}", "Mean audience score"),
        ("Audience Votes", f"{total_votes:,}", "Total vote volume"),
    ]

    for column, (label, value, note) in zip((col1, col2, col3), metrics):
        column.markdown(
            f"""
            <div class="metric-card">
                <p>{label}</p>
                <h3>{value}</h3>
                <span>{note}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
