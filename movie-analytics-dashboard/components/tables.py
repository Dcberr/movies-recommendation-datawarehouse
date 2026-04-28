# components/tables.py

import streamlit as st
from utils.helpers import get_display_dataframe, render_section_heading


def render_table(df):
    render_section_heading(
        "Catalog",
        "Movie List",
        "Review the ranked dataset behind the charts.",
    )

    st.dataframe(
        get_display_dataframe(df.sort_values("weighted_rating", ascending=False)),
        use_container_width=True
    )
