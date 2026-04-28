# services/ai/nlp/normalizer.py

import re
import unicodedata


def remove_accents(text: str) -> str:
    """
    Bỏ dấu tiếng Việt nhưng giữ 'đ' → 'd'
    """
    text = text.replace("đ", "d").replace("Đ", "D")

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text if unicodedata.category(char) != "Mn"
    )

    return text


def clean_text(text: str) -> str:
    """
    Clean text:
    - lowercase
    - remove accents
    - remove special characters
    - normalize spaces
    """
    text = text.lower()
    text = remove_accents(text)

    # giữ lại chữ + số + space
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text