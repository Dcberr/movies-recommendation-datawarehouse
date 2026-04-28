# components/charts.py

import streamlit as st
import plotly.express as px

CHART_COLORS = ["#c8a96b", "#8fb7a3", "#d97b66", "#6c88c4", "#b8a1d9"]
CHART_LABELS = {
    "title": "Title",
    "weighted_rating": "Weighted Rating",
    "avg_rating": "Average Rating",
    "num_votes": "Vote Count",
    "year": "Release Year",
}


def _apply_chart_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#11161d",
        font=dict(color="#f3efe6", family="Inter, sans-serif"),
        title=dict(font=dict(size=18, color="#f5ede0")),
        margin=dict(l=12, r=12, t=56, b=12),
        hoverlabel=dict(
            bgcolor="#1a212b",
            bordercolor="#2f3947",
            font_color="#f5ede0",
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.08)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.08)",
    )
    return fig


def plot_top_movies(df):
    df_top = df.sort_values("weighted_rating", ascending=False).head(10)

    fig = px.bar(
        df_top,
        x="weighted_rating",
        y="title",
        orientation="h",
        title="Top 10 Titles by Weighted Rating",
        color_discrete_sequence=[CHART_COLORS[0]],
        labels=CHART_LABELS,
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    _apply_chart_theme(fig)

    st.plotly_chart(fig, use_container_width=True)


def plot_rating_distribution(df):
    fig = px.histogram(
        df,
        x="avg_rating",
        nbins=30,
        title="Rating Distribution",
        color_discrete_sequence=[CHART_COLORS[1]],
        labels=CHART_LABELS,
    )
    _apply_chart_theme(fig)

    st.plotly_chart(fig, use_container_width=True)


def plot_votes_vs_rating(df):
    fig = px.scatter(
        df,
        x="num_votes",
        y="avg_rating",
        title="Votes Compared with Rating",
        hover_data=["title"],
        color_discrete_sequence=[CHART_COLORS[2]],
        labels=CHART_LABELS,
    )
    fig.update_traces(marker=dict(size=9, opacity=0.72, line=dict(width=0)))
    _apply_chart_theme(fig)

    st.plotly_chart(fig, use_container_width=True)


def plot_yearly_trend(df):
    df_trend = df.groupby("year")["weighted_rating"].mean().reset_index()

    fig = px.line(
        df_trend,
        x="year",
        y="weighted_rating",
        title="Weighted Rating Trend Over Time",
        labels=CHART_LABELS,
    )
    fig.update_traces(line=dict(color=CHART_COLORS[3], width=3))
    _apply_chart_theme(fig)

    st.plotly_chart(fig, use_container_width=True)
