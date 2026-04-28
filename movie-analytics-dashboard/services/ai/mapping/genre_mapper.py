# services/ai/mapping/genre_mapper.py

from services.ai.config.constants import GENRE_KEYWORDS
from services.ai.repository.movie_repo import get_all_genres
from services.ai.nlp.normalizer import clean_text


def build_keyword_to_genre_map():
    mapping = {}

    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            kw_clean = clean_text(kw)
            mapping[kw_clean] = genre
            

    return mapping


KEYWORD_TO_GENRE = build_keyword_to_genre_map()

def map_keywords_to_genres(keywords: list) -> list:
    """
    Map keywords → genres

    Input:
        ["hai huoc", "tre em", "hanh dong"]

    Output:
        ["Comedy", "Children", "Action"]
    """

    genres = []

    for kw in keywords:
        genre = KEYWORD_TO_GENRE.get(kw)
        if genre:
            genres.append(genre)

    # remove duplicate
    return list(set(genres))


def validate_genres(genres: list) -> list:
    """
    Chỉ giữ lại genre tồn tại trong DB
    """
    if not genres:
        return []

    db_genres = get_all_genres()

    valid = [g for g in genres if g in db_genres]

    return valid


def map_to_valid_genres(keywords: list) -> list:
    """
    Full pipeline mapping

    keywords → genres → validated genres
    """

    genres = map_keywords_to_genres(keywords)

    valid_genres = validate_genres(genres)

    return valid_genres