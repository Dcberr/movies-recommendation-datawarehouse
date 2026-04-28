# services/ai/nlp/parser.py

import re

from services.ai.config.constants import GENRE_KEYWORDS
from services.ai.nlp.normalizer import clean_text


def extract_keywords(user_input: str) -> list:
    text = clean_text(user_input)

    matched_keywords = []

    for genre, keywords in GENRE_KEYWORDS.items():
        for keyword in keywords:
            kw_clean = clean_text(keyword)

            if contains_phrase(text, kw_clean):
                matched_keywords.append(kw_clean)

    matched_keywords = list(set(matched_keywords))

    # 🔥 remove noise
    matched_keywords = remove_sub_keywords(matched_keywords)

    return matched_keywords

def contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None

def remove_sub_keywords(keywords: list) -> list:
    """
    Loại bỏ keyword bị chứa trong keyword khác
    ví dụ:
    ['vui', 'vui nhon'] → ['vui nhon']
    """
    keywords = sorted(keywords, key=len, reverse=True)

    result = []

    for kw in keywords:
        if not any(kw in existing for existing in result):
            result.append(kw)

    return result