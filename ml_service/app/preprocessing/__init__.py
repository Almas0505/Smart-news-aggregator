"""
Text Preprocessing Module

Утилиты для предобработки текста перед ML моделями.
"""

from app.preprocessing.text_cleaner import (
    remove_html_tags,
    remove_urls,
    remove_special_characters,
    to_lowercase,
    remove_stopwords,
    lemmatize_text,
    tokenize,
    preprocess_text,
    preprocess_for_tfidf,
    preprocess_for_bert,
    truncate_text,
    get_text_stats
)


__all__ = [
    "remove_html_tags",
    "remove_urls",
    "remove_special_characters",
    "to_lowercase",
    "remove_stopwords",
    "lemmatize_text",
    "tokenize",
    "preprocess_text",
    "preprocess_for_tfidf",
    "preprocess_for_bert",
    "truncate_text",
    "get_text_stats",
]