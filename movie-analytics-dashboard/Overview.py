# app.py

import streamlit as st

from config.settings import APP_CONFIG
from utils.helpers import load_stylesheet, render_app_navigation, render_page_banner, render_section_heading

st.set_page_config(
    page_title="Overview - Movie Analytics Dashboard",
    layout="wide"
)

load_stylesheet()
render_app_navigation("overview")

render_page_banner(
    "Overview",
    "Movie Analytics Overview",
    "A curated workspace for reading movie performance through audience ratings, voting volume, and long-term release trends.",
    ["Chart-driven storytelling", "Business-friendly metrics", "Interactive exploration"],
)

render_section_heading(
    "Purpose",
    "What This System Helps You Understand",
    "The platform is built to turn raw movie metrics into readable signals about title quality, audience engagement, and how reception changes over time.",
)

intro_col1, intro_col2 = st.columns([1.25, 1])

with intro_col1:
    st.markdown(
        """
        <div class="content-card">
            <h3>Why it matters</h3>
            <p>
                A movie dataset is usually full of low-level fields such as ratings, vote counts,
                years, and identifiers. This dashboard restructures those fields into a decision-friendly
                layer so users can quickly answer which titles stand out, whether high ratings are
                supported by enough audience participation, and which release periods perform better.
            </p>
            <p>
                Instead of scanning rows one by one, users can move from summary KPIs to visual patterns,
                then validate the details inside the catalog tables on the dedicated pages.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with intro_col2:
    st.markdown(
        """
        <div class="content-card highlight-card">
            <p class="eyebrow">Navigation</p>
            <h3>Recommended Flow</h3>
            <div class="info-stack">
                <div><strong>Dashboard:</strong> review KPIs and compare the main analytical charts.</div>
                <div><strong>Movies:</strong> inspect the underlying title-level catalog with cleaner labels.</div>
                <div><strong>Trends:</strong> focus on the release-year trendline and yearly summary table.</div>
            </div>
            <p class="helper-copy">Use the sidebar to switch between these sections during exploration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

render_section_heading(
    "Chart Guide",
    "How to Read the Visuals",
    "Each chart answers a different analytical question, so the pages work best when they are read together rather than in isolation.",
)

guide_col1, guide_col2 = st.columns(2)

with guide_col1:
    st.markdown(
        """
        <div class="content-card">
            <h3>Top 10 Titles by Weighted Rating</h3>
            <p>
                This bar chart highlights the strongest-performing movies after balancing rating quality
                with vote volume. It is more reliable than using average rating alone because it reduces
                the impact of titles with too few votes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="content-card">
            <h3>Votes Compared with Rating</h3>
            <p>
                This scatter plot shows whether highly rated movies also attract meaningful audience
                participation. It helps separate broadly supported titles from niche titles with limited
                engagement.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with guide_col2:
    st.markdown(
        """
        <div class="content-card">
            <h3>Rating Distribution</h3>
            <p>
                This histogram reveals where most movies cluster on the rating scale. It helps identify
                whether the catalog is concentrated around average titles or skewed toward stronger or
                weaker audience reception.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="content-card">
            <h3>Weighted Rating Trend Over Time</h3>
            <p>
                This line chart tracks how audience-weighted performance changes across release years.
                It is useful for spotting stronger eras, long-term decline or growth, and broader shifts
                in catalog quality.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

render_section_heading(
    "Outputs",
    "What You Can Take Away",
    "The system is designed not only to display charts, but to support interpretation and decision-making from multiple angles.",
)

outcome_col1, outcome_col2, outcome_col3 = st.columns(3)

for column, title, description in (
    (
        outcome_col1,
        "Performance Signal",
        "Identify titles that remain strong after balancing audience score and vote credibility.",
    ),
    (
        outcome_col2,
        "Engagement Context",
        "Understand whether popularity and quality move together or diverge for different movies.",
    ),
    (
        outcome_col3,
        "Temporal Insight",
        "Track how reception changes by release period to support comparative historical analysis.",
    ),
):
    column.markdown(
        f"""
        <div class="metric-card landing-metric">
            <p>{title}</p>
            <span>{description}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
