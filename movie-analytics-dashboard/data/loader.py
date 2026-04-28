# data/loader.py

import pandas as pd
import streamlit as st
from data.db import get_connection
from data import queries


@st.cache_data
def load_top_movies():
    conn = get_connection()
    df = pd.read_sql(queries.TOP_MOVIES, conn)
    conn.close()
    return df


@st.cache_data
def load_genre_distribution():
    conn = get_connection()
    df = pd.read_sql(queries.GENRE_DISTRIBUTION, conn)
    conn.close()
    return df


@st.cache_data
def load_rating_distribution():
    conn = get_connection()
    df = pd.read_sql(queries.RATING_DISTRIBUTION, conn)
    conn.close()
    return df


@st.cache_data
def load_votes_vs_rating():
    conn = get_connection()
    df = pd.read_sql(queries.VOTES_VS_RATING, conn)
    conn.close()
    return df


@st.cache_data
def load_yearly_trend():
    conn = get_connection()
    df = pd.read_sql(queries.YEARLY_TREND, conn)
    conn.close()
    return df


@st.cache_data
def load_all_movies():
    conn = get_connection()
    df = pd.read_sql(queries.MOVIE_FULL, conn)
    conn.close()
    return df