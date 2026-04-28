import streamlit as st

from services.ai.pipeline.recommender import recommend_with_context
from utils.helpers import load_stylesheet, render_app_navigation, render_page_banner, render_section_heading

DEFAULT_PROMPT = "Phim hài hành động cho trẻ em"
EXAMPLE_PROMPTS = [
    "Phim hài hành động cho trẻ em",
    "Phim tình cảm lãng mạn nhẹ nhàng",
    "Phim kinh dị giật gân",
    "Phim phiêu lưu giả tưởng",
]


def run_recommendation(prompt: str, top_k: int):
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        return None

    with st.spinner("Generating recommendations..."):
        return recommend_with_context(cleaned_prompt, top_k=top_k)


def render_tag_list(items, empty_text):
    if items:
        tags = "".join(f'<span class="insight-tag">{item}</span>' for item in items)
        st.markdown(f'<div class="tag-group">{tags}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="empty-state-inline">{empty_text}</div>',
            unsafe_allow_html=True,
        )


def render_summary_tile(label, value, note):
    st.markdown(
        f"""
        <div class="summary-tile">
            <p>{label}</p>
            <h3>{value}</h3>
            <span>{note}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_panel(title, description, items, empty_text):
    st.markdown(
        f"""
        <div class="info-panel">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_tag_list(items, empty_text)


def render_result_card(index, item):
    year = item.get("year")
    year_text = f" ({int(year)})" if year is not None else ""
    match_score = item.get("match_score")
    match_markup = (
        f'<span class="result-chip">Genre Match {int(match_score)}</span>'
        if match_score is not None
        else '<span class="result-chip muted-chip">Popular Pick</span>'
    )
    score_markup = ""
    if item.get("score") is not None:
        score_markup = f'<span class="result-chip">AI Score {item["score"]:.3f}</span>'

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-rank">#{index}</div>
            <div class="result-body">
                <div class="result-header">
                    <h3>{item["title"]}{year_text}</h3>
                    <div class="result-chip-row">
                        {match_markup}
                        {score_markup}
                    </div>
                </div>
                <div class="result-stats">
                    <div>
                        <p>Weighted Rating</p>
                        <strong>{item["weighted_rating"]:.2f}</strong>
                    </div>
                    <div>
                        <p>Vote Count</p>
                        <strong>{int(item["num_votes"]):,}</strong>
                    </div>
                </div>
                <p class="result-reason">{item["reason"]}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="AI Recommendation", layout="wide")
load_stylesheet()
render_app_navigation("ai_recommendation")

if "ai_prompt" not in st.session_state:
    st.session_state.ai_prompt = DEFAULT_PROMPT

render_page_banner(
    "Recommendation",
    "AI Movie Recommendation",
    "Describe the kind of movie you want in natural language, then review how the recommendation engine interprets that request before selecting the final titles.",
    ["Natural-language input", "Readable recommendation logic", "Presentation-ready results"],
)

render_section_heading(
    "Workspace",
    "Recommendation Console",
    "A cleaner interface for entering requests, checking detected intent, and scanning the ranked movie list.",
)

control_col, explain_col = st.columns([1.25, 0.75], gap="large")

with control_col:
    st.markdown(
        """
        <div class="control-shell">
            <div class="control-shell__header">
                <p class="eyebrow">Input</p>
                <h3>Describe Your Movie Preference</h3>
                <p>Write a request in Vietnamese or English. The engine will detect genre intent, map it to the warehouse, and rank the strongest candidates.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_example = None
    st.markdown('<div class="example-label">Quick examples</div>', unsafe_allow_html=True)
    example_cols = st.columns(2, gap="small")
    for idx, example in enumerate(EXAMPLE_PROMPTS):
        target_col = example_cols[idx % 2]
        if target_col.button(example, key=f"example_prompt_{idx}", use_container_width=True):
            selected_example = example

    if selected_example:
        st.session_state.ai_prompt = selected_example

    with st.form("ai_recommendation_form"):
        prompt = st.text_area(
            "Describe what kind of movie you want",
            value=st.session_state.ai_prompt,
            placeholder="Ví dụ: phim hài hành động cho trẻ em",
            height=150,
        )
        top_k = st.slider("Number of recommendations", min_value=5, max_value=20, value=10)
        submitted = st.form_submit_button("Generate Recommendations", use_container_width=True)

    if submitted:
        st.session_state.ai_prompt = prompt
        st.session_state.ai_results = run_recommendation(prompt, top_k)
        st.session_state.ai_top_k = top_k

with explain_col:
    st.markdown(
        """
        <div class="content-card highlight-card compact-card">
            <p class="eyebrow">Engine</p>
            <h3>How Ranking Works</h3>
            <div class="logic-list">
                <div><strong>Interpret</strong><span>Extract keywords from the request.</span></div>
                <div><strong>Validate</strong><span>Map them to supported genres in the warehouse.</span></div>
                <div><strong>Rank</strong><span>Score candidates by match strength, weighted rating, and vote credibility.</span></div>
            </div>
            <p class="helper-copy">If no valid genre is found, the system falls back to popular titles.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

result_context = st.session_state.get("ai_results")

if result_context:
    render_section_heading(
        "Summary",
        "Request Interpretation",
        "Review what the engine understood from the prompt before moving to the recommendations.",
    )

    mode_label = "Fallback Popular Titles" if result_context["fallback_used"] else "Genre-Matched Ranking"
    request_text = result_context["input"] if result_context["input"].strip() else "Empty request"
    summary_col1, summary_col2 = st.columns([1.35, 0.95], gap="large")
    with summary_col1:
        st.markdown(
            f"""
            <div class="request-summary request-summary--stacked">
                <p class="eyebrow">Current Request</p>
                <h3>{request_text}</h3>
                <p class="request-summary__copy">
                    The recommendation engine uses this prompt as the single source of intent before parsing keywords and mapping genres.
                </p>
                <span class="request-mode">{mode_label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with summary_col2:
        stats_col1, stats_col2, stats_col3 = st.columns(3, gap="small")
        with stats_col1:
            render_summary_tile(
                "Keywords",
                len(result_context["keywords"]),
                "Detected",
            )
        with stats_col2:
            render_summary_tile(
                "Genres",
                len(result_context["genres"]),
                "Validated",
            )
        with stats_col3:
            render_summary_tile(
                "Titles",
                len(result_context["results"]),
                "Returned",
            )

    diag_col1, diag_col2 = st.columns(2, gap="large")
    with diag_col1:
        render_info_panel(
            "Detected Keywords",
            "Cleaned intent signals extracted from the natural-language request.",
            result_context["keywords"],
            "No keywords were extracted from the request.",
        )

    with diag_col2:
        render_info_panel(
            "Validated Genres",
            "Genres preserved for ranking after checking against the warehouse.",
            result_context["genres"],
            "No valid genres detected. The system used popular-title fallback.",
        )

    st.divider()

    render_section_heading(
        "Results",
        "Recommended Titles",
        "Each result is presented with enough context to understand why it surfaced without overwhelming the page.",
    )

    results = result_context["results"]
    if results:
        page_size = 4
        total_results = len(results)
        total_pages = (total_results + page_size - 1) // page_size
        current_page = st.selectbox(
            "Results page",
            options=list(range(1, total_pages + 1)),
            index=0,
            key="ai_results_page",
        )
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_results)

        st.markdown(
            f"""
            <div class="results-toolbar">
                <span>Showing <strong>{start_idx + 1}-{end_idx}</strong> of <strong>{total_results}</strong> recommendations</span>
                <span>Page <strong>{current_page}</strong> / <strong>{total_pages}</strong></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="results-window">', unsafe_allow_html=True)
        for idx, item in enumerate(results[start_idx:end_idx], start=start_idx + 1):
            render_result_card(idx, item)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No recommendations were returned for this request.")
else:
    st.markdown(
        """
        <div class="empty-hero">
            <p class="eyebrow">Ready</p>
            <h3>Start with a movie request</h3>
            <p>Submit a prompt to see detected keywords, mapped genres, and the ranked recommendation list.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
