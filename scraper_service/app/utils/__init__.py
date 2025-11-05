"""
Utils Module

Вспомогательные утилиты для Scraper Service.
"""

from app.utils.text_utils import (
    remove_html_tags,
    clean_text,
    count_words,
    count_sentences,
    truncate_text,
    extract_sentences,
    estimate_reading_time,
    extract_main_content
)

from app.utils.image_downloader import (
    download_image,
    download_images_batch,
    resize_image,
    create_thumbnail,
    validate_image,
    get_image_info,
    process_image
)


__all__ = [
    # Text utils
    "remove_html_tags",
    "clean_text",
    "count_words",
    "count_sentences",
    "truncate_text",
    "extract_sentences",
    "estimate_reading_time",
    "extract_main_content",
    
    # Image utils
    "download_image",
    "download_images_batch",
    "resize_image",
    "create_thumbnail",
    "validate_image",
    "get_image_info",
    "process_image",
]