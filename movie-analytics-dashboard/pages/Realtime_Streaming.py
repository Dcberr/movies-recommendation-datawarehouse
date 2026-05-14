import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ModuleNotFoundError:
    AUTOREFRESH_AVAILABLE = False

    def st_autorefresh(interval=0, key=None):
        if key and key not in st.session_state:
            st.session_state[key] = 0
        elif key:
            st.session_state[key] += 1
        return st.session_state.get(key, 0)

from services.streaming.analytics.realtime_analytics import (
    get_active_users,
    get_hot_genres,
    get_live_events,
    get_live_searches,
    get_trending_movies,
)
from services.streaming.analytics.trending_service import compute_trending_scores
from services.streaming.utils.streamlit_tracking import (
    ensure_streaming_session,
    render_debug_panel,
    track_page_visit,
)
from utils.helpers import format_number, load_stylesheet, render_app_navigation, render_page_banner, render_section_heading


st.set_page_config(
    page_title="Realtime Streaming Dashboard",
    page_icon="🔥",
    layout="wide",
)


REFRESH_INTERVAL_MS = 5_000
LOOKBACK_MINUTES = 5
EVENT_FEED_LIMIT = 25
TRENDING_LIMIT = 10
SEARCH_LIMIT = 15


def apply_realtime_page_styles():
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background:
                linear-gradient(180deg, rgba(19, 28, 39, 0.96), rgba(13, 20, 30, 0.92));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem 1rem;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22);
            min-height: 130px;
        }

        div[data-testid="stMetricLabel"] {
            color: #aeb9c7;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: #f7f1e7;
            font-size: 2rem;
        }

        .realtime-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1rem;
        }

        .realtime-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.55rem 0.8rem;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            color: #f5ede0;
            font-size: 0.88rem;
        }

        .monitor-panel {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1rem 1rem 0.35rem 1rem;
            background: linear-gradient(180deg, rgba(18, 27, 38, 0.92), rgba(11, 18, 26, 0.88));
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.2);
            margin-bottom: 1rem;
        }

        .feed-item {
            display: grid;
            grid-template-columns: minmax(0, 120px) minmax(0, 90px) minmax(0, 1fr) minmax(0, 160px);
            gap: 0.85rem;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .feed-item:last-child {
            border-bottom: none;
        }

        .feed-badge {
            display: inline-flex;
            justify-content: center;
            padding: 0.35rem 0.6rem;
            border-radius: 999px;
            background: rgba(200, 169, 107, 0.16);
            border: 1px solid rgba(200, 169, 107, 0.22);
            color: #f7f1e7;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .feed-muted {
            color: #a6afbb;
            font-size: 0.88rem;
        }

        .feed-main {
            color: #f5ede0;
            font-weight: 600;
            overflow-wrap: anywhere;
        }

        .feed-time {
            color: #d9e1ea;
            font-size: 0.84rem;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=5, show_spinner=False)
def load_active_user_metrics(minutes):
    return get_active_users(minutes=minutes)


@st.cache_data(ttl=5, show_spinner=False)
def load_trending_movies(minutes, top_k):
    return get_trending_movies(minutes=minutes, top_k=top_k)


@st.cache_data(ttl=5, show_spinner=False)
def load_hot_genres(minutes):
    return get_hot_genres(minutes=minutes)


@st.cache_data(ttl=5, show_spinner=False)
def load_live_searches(minutes, top_k):
    return get_live_searches(minutes=minutes, top_k=top_k)


@st.cache_data(ttl=5, show_spinner=False)
def load_live_events(limit):
    return get_live_events(limit=limit)


@st.cache_data(ttl=5, show_spinner=False)
def load_trending_scores(minutes):
    return compute_trending_scores(minutes=minutes)


def build_plotly_layout(height):
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,16,24,0.55)",
        font=dict(color="#f5ede0", family="Inter, sans-serif"),
        margin=dict(l=16, r=16, t=50, b=16),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )


def safe_dataframe(df):
    if df is None:
        return pd.DataFrame()
    return df.copy()


def prepare_live_events(df):
    events_df = safe_dataframe(df)
    if events_df.empty:
        return events_df

    if "event_time" in events_df.columns:
        events_df["event_time"] = pd.to_datetime(events_df["event_time"], errors="coerce")
        events_df = events_df.sort_values("event_time", ascending=False)

    return events_df.reset_index(drop=True)


def render_kpi_cards(active_metrics, searches_df, events_df):
    active_sessions = int(active_metrics.get("active_sessions", 0) or 0)
    active_users = int(active_metrics.get("active_users", 0) or 0)
    total_live_events = int(len(events_df.index))
    total_searches = int(searches_df["total_searches"].sum()) if not searches_df.empty else 0

    kpi_columns = st.columns(4)
    kpis = [
        ("🎬 Active Sessions", format_number(active_sessions), "Current viewing activity"),
        ("🧑 Active Users", format_number(active_users), "Unique users in the last 5 minutes"),
        ("⚡ Total Live Events", format_number(total_live_events), "Latest monitored event stream"),
        ("🔎 Total Searches", format_number(total_searches), "Search traffic in the last 5 minutes"),
    ]

    for column, (label, value, help_text) in zip(kpi_columns, kpis):
        with column:
            st.metric(label=label, value=value, help=help_text)


def render_trending_movies_section(df):
    render_section_heading(
        "Section C",
        "Trending Movies",
        "Top titles by view volume over the rolling five-minute window.",
    )

    if df.empty:
        st.info("No trending movie activity is available right now.")
        return

    trending_df = df.sort_values("total_views", ascending=False).copy()
    fig = px.bar(
        trending_df,
        x="total_views",
        y="title",
        orientation="h",
        color="total_views",
        color_continuous_scale=["#5b8ff9", "#c8a96b", "#ff7a59"],
        text="total_views",
        labels={"title": "Movie Title", "total_views": "Total Views"},
    )
    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Views: %{x}<extra></extra>",
    )
    fig.update_layout(**build_plotly_layout(height=430))
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False),
        yaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})


def render_hot_genres_section(df):
    render_section_heading(
        "Section D",
        "Hot Genres",
        "Genre activity reflects what audiences are actively exploring in the current stream.",
    )

    if df.empty:
        st.info("No genre interaction data is available right now.")
        return

    genres_df = df.sort_values("total_events", ascending=False).copy()
    fig = px.pie(
        genres_df,
        names="genre_name",
        values="total_events",
        hole=0.55,
        color_discrete_sequence=[
            "#c8a96b",
            "#5b8ff9",
            "#61d9a7",
            "#ff7a59",
            "#8d6dfc",
            "#f6c85f",
            "#6ec5ff",
            "#ff9d4d",
            "#7fd1b9",
            "#d97af5",
        ],
    )
    fig.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Events: %{value}<extra></extra>",
    )
    fig.update_layout(**build_plotly_layout(height=430))
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})


def render_live_searches_section(df):
    render_section_heading(
        "Section E",
        "Live Searches",
        "Search demand updates every refresh cycle and stays searchable inside the table view.",
    )

    if df.empty:
        st.info("No search activity has been recorded in the last 5 minutes.")
        return

    search_df = df.rename(
        columns={"query_text": "Query Text", "total_searches": "Total Searches"}
    ).copy()
    st.dataframe(
        search_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Query Text": st.column_config.TextColumn(width="large"),
            "Total Searches": st.column_config.NumberColumn(format="%d"),
        },
    )


def render_live_events_feed(df):
    render_section_heading(
        "Section F",
        "Live Events Feed",
        "A compact monitoring stream for the latest audience actions across the platform.",
    )

    if df.empty:
        st.warning("The live events feed is empty at the moment.")
        return

    st.markdown('<div class="monitor-panel">', unsafe_allow_html=True)

    for _, row in df.iterrows():
        event_time = row.get("event_time")
        event_time_display = (
            event_time.strftime("%Y-%m-%d %H:%M:%S")
            if pd.notna(event_time)
            else "Unknown time"
        )
        movie_id = row.get("movie_id")
        movie_label = f"Movie #{int(movie_id)}" if pd.notna(movie_id) else "No movie id"
        source_page = row.get("source_page") or "Unknown source"
        event_type = str(row.get("event_type") or "event").replace("_", " ")
        st.markdown(
            f"""
            <div class="feed-item">
                <div class="feed-badge">{event_type}</div>
                <div class="feed-muted">{movie_label}</div>
                <div class="feed-main">{source_page}</div>
                <div class="feed-time">{event_time_display}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_trending_score_section(df):
    render_section_heading(
        "Section G",
        "Trending Score Analytics",
        "A blended score combines live view momentum with recent audience rating quality.",
    )

    if df.empty:
        st.info("Trending score analytics are unavailable until new rating activity arrives.")
        return

    score_df = df.copy()
    if "avg_rating" not in score_df.columns:
        score_df["avg_rating"] = 0.0

    score_df["avg_rating"] = score_df["avg_rating"].fillna(0.0)
    fig = px.scatter(
        score_df,
        x="total_views",
        y="trending_score",
        size="trending_score",
        color="avg_rating",
        hover_name="title",
        text="title",
        size_max=32,
        color_continuous_scale=["#5b8ff9", "#61d9a7", "#ffb84d"],
        labels={
            "total_views": "Total Views",
            "trending_score": "Trending Score",
            "avg_rating": "Average Rating",
        },
    )
    fig.update_traces(
        mode="markers+text",
        textposition="top center",
        marker=dict(line=dict(width=1, color="rgba(255,255,255,0.22)")),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Views: %{x}<br>"
            "Trending Score: %{y:.2f}<br>"
            "Avg Rating: %{marker.color:.2f}<extra></extra>"
        ),
    )
    fig.update_layout(**build_plotly_layout(height=470))
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False),
    )

    benchmark_line = go.Scatter(
        x=score_df["total_views"],
        y=[score_df["trending_score"].mean()] * len(score_df.index),
        mode="lines",
        line=dict(color="rgba(255,255,255,0.25)", dash="dash"),
        name="Average Score",
        hoverinfo="skip",
    )
    fig.add_trace(benchmark_line)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})


load_stylesheet()
apply_realtime_page_styles()
render_app_navigation("realtime_streaming")
ensure_streaming_session()
track_page_visit("streaming")

refresh_count = st_autorefresh(interval=REFRESH_INTERVAL_MS, key="realtime_streaming_refresh")

if not AUTOREFRESH_AVAILABLE:
    st.warning(
        "Package `streamlit_autorefresh` is not installed. The dashboard is running without true auto-refresh."
    )

render_page_banner(
    "Realtime Analytics",
    "Realtime Streaming Dashboard",
    "Monitor live audience behavior, search demand, content momentum, and event flow through a production-style streaming analytics workspace.",
    ["5-second auto refresh", "Streaming event intelligence", "Operations-ready monitoring"],
)

st.markdown(
    f"""
    <div class="realtime-chip-row">
        <span class="realtime-chip">Refresh Cycle #{refresh_count + 1}</span>
        <span class="realtime-chip">Rolling Window: {LOOKBACK_MINUTES} minutes</span>
        <span class="realtime-chip">Feed Limit: {EVENT_FEED_LIMIT} events</span>
    </div>
    """,
    unsafe_allow_html=True,
)

active_metrics = load_active_user_metrics(LOOKBACK_MINUTES)
trending_movies_df = safe_dataframe(load_trending_movies(LOOKBACK_MINUTES, TRENDING_LIMIT))
hot_genres_df = safe_dataframe(load_hot_genres(LOOKBACK_MINUTES))
live_searches_df = safe_dataframe(load_live_searches(LOOKBACK_MINUTES, SEARCH_LIMIT))
live_events_df = prepare_live_events(load_live_events(EVENT_FEED_LIMIT))
trending_scores_df = safe_dataframe(load_trending_scores(LOOKBACK_MINUTES))

render_section_heading(
    "Section B",
    "Realtime KPIs",
    "Critical activity indicators update automatically to keep the monitoring surface current.",
)
render_kpi_cards(active_metrics, live_searches_df, live_events_df)

st.divider()

chart_col1, chart_col2 = st.columns([1.2, 1])
with chart_col1:
    render_trending_movies_section(trending_movies_df)
with chart_col2:
    render_hot_genres_section(hot_genres_df)

st.divider()

render_live_searches_section(live_searches_df)

st.divider()

render_live_events_feed(live_events_df)

st.divider()

render_trending_score_section(trending_scores_df)

st.divider()

render_debug_panel()
