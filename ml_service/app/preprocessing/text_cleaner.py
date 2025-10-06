"""
Text Preprocessing Utilities

Этот модуль содержит функции для предобработки текста перед ML моделями.

ЗАЧЕМ НУЖЕН PREPROCESSING?
- Модели работают лучше с чистыми данными
- Удаляем шум (HTML теги, спецсимволы)
- Нормализуем текст (lowercase, убираем лишние пробелы)
- Токенизация (разбиваем на слова)
"""

import re
import string
from typing import List, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# ===== ИНИЦИАЛИЗАЦИЯ NLTK =====
# Загружаем необходимые данные NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


# ===== ОСНОВНЫЕ ФУНКЦИИ =====

def remove_html_tags(text: str) -> str:
    """Удаляет HTML теги из текста.
    
    Зачем: Новости часто содержат HTML разметку (<p>, <div>, и т.д.)
    Нужно убрать, чтобы модель видела только текст.
    
    Args:
        text: Текст с HTML тегами
        
    Returns:
        Текст без HTML
        
    Example:
        >>> text = "<p>Hello <b>world</b>!</p>"
        >>> remove_html_tags(text)
        "Hello world!"
    """
    # Регулярное выражение: <любые символы>
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text


def remove_urls(text: str) -> str:
    """Удаляет URLs из текста.
    
    Зачем: Ссылки не несут смысловой нагрузки для классификации.
    
    Args:
        text: Текст с URLs
        
    Returns:
        Текст без URLs
        
    Example:
        >>> text = "Check this https://example.com"
        >>> remove_urls(text)
        "Check this"
    """
    # Паттерн для поиска URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    clean_text = re.sub(url_pattern, '', text)
    return clean_text


def remove_special_characters(text: str, keep_numbers: bool = True) -> str:
    """Удаляет спецсимволы, оставляя только буквы и цифры.
    
    Зачем: Спецсимволы (@, #, $) не помогают в классификации.
    
    Args:
        text: Исходный текст
        keep_numbers: Оставить цифры или нет
        
    Returns:
        Очищенный текст
        
    Example:
        >>> text = "Price: $100! Amazing deal..."
        >>> remove_special_characters(text)
        "Price 100 Amazing deal"
    """
    if keep_numbers:
        # Оставляем буквы, цифры и пробелы
        pattern = r'[^a-zA-Z0-9\s]'
    else:
        # Оставляем только буквы и пробелы
        pattern = r'[^a-zA-Z\s]'
    
    clean_text = re.sub(pattern, ' ', text)
    
    # Убираем множественные пробелы
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()


def to_lowercase(text: str) -> str:
    """Приводит текст к нижнему регистру.
    
    Зачем: "Apple" и "apple" - одно слово для модели.
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст в lowercase
    """
    return text.lower()


def remove_stopwords(text: str, language: str = 'english') -> str:
    """Удаляет стоп-слова (частые слова без смысловой нагрузки).
    
    Зачем: Слова "the", "is", "and" встречаются везде и не помогают
    в классификации. Удаляем их, чтобы модель фокусировалась на важном.
    
    Args:
        text: Исходный текст
        language: Язык стоп-слов
        
    Returns:
        Текст без стоп-слов
        
    Example:
        >>> text = "This is a great article about AI"
        >>> remove_stopwords(text)
        "great article AI"
    """
    # Получаем список стоп-слов для языка
    stop_words = set(stopwords.words(language))
    
    # Токенизируем (разбиваем на слова)
    words = word_tokenize(text)
    
    # Оставляем только слова, которые НЕ в списке стоп-слов
    filtered_words = [word for word in words if word.lower() not in stop_words]
    
    return ' '.join(filtered_words)


def lemmatize_text(text: str) -> str:
    """Лемматизация - приведение слов к базовой форме.
    
    Зачем: "running", "ran", "runs" → "run"
    Модель понимает, что это одно и то же слово.
    
    Args:
        text: Исходный текст
        
    Returns:
        Лемматизированный текст
        
    Example:
        >>> text = "The cats are running quickly"
        >>> lemmatize_text(text)
        "The cat be run quickly"
    """
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
    
    # Лемматизируем каждое слово
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    
    return ' '.join(lemmatized_words)


def remove_extra_whitespace(text: str) -> str:
    """Удаляет лишние пробелы.
    
    Зачем: Нормализация для консистентности.
    
    Args:
        text: Текст с лишними пробелами
        
    Returns:
        Нормализованный текст
    """
    # Заменяем множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    """Токенизация - разбиение текста на слова.
    
    Зачем: ML модели работают с отдельными словами, а не со строками.
    
    Args:
        text: Исходный текст
        
    Returns:
        Список токенов (слов)
        
    Example:
        >>> text = "Hello, world!"
        >>> tokenize(text)
        ['Hello', ',', 'world', '!']
    """
    return word_tokenize(text)


# ===== ПОЛНЫЙ PIPELINE =====

def preprocess_text(
    text: str,
    lowercase: bool = True,
    remove_html: bool = True,
    remove_url: bool = True,
    remove_special_chars: bool = True,
    remove_stops: bool = False,  # По умолчанию НЕ удаляем (для BERT)
    lemmatize: bool = False,      # По умолчанию НЕ лемматизируем (для BERT)
    keep_numbers: bool = True
) -> str:
    """Полный pipeline предобработки текста.
    
    Применяет все шаги preprocessing в правильном порядке.
    Можно настраивать, какие шаги использовать.
    
    Args:
        text: Исходный текст
        lowercase: Привести к нижнему регистру
        remove_html: Удалить HTML теги
        remove_url: Удалить URLs
        remove_special_chars: Удалить спецсимволы
        remove_stops: Удалить стоп-слова (для TF-IDF, не для BERT!)
        lemmatize: Лемматизировать (для TF-IDF, не для BERT!)
        keep_numbers: Оставить цифры
        
    Returns:
        Обработанный текст
        
    Example:
        >>> text = "<p>Check this out: https://example.com Amazing!</p>"
        >>> preprocess_text(text)
        "check this out amazing"
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Шаг 1: Удаляем HTML
    if remove_html:
        text = remove_html_tags(text)
    
    # Шаг 2: Удаляем URLs
    if remove_url:
        text = remove_urls(text)
    
    # Шаг 3: Lowercase (до удаления стоп-слов)
    if lowercase:
        text = to_lowercase(text)
    
    # Шаг 4: Удаляем спецсимволы
    if remove_special_chars:
        text = remove_special_characters(text, keep_numbers=keep_numbers)
    
    # Шаг 5: Удаляем стоп-слова (опционально)
    # ВАЖНО: Для BERT не удаляем! Контекст важен.
    if remove_stops:
        text = remove_stopwords(text)
    
    # Шаг 6: Лемматизация (опционально)
    # ВАЖНО: Для BERT не нужно! Он понимает формы слов.
    if lemmatize:
        text = lemmatize_text(text)
    
    # Шаг 7: Убираем лишние пробелы
    text = remove_extra_whitespace(text)
    
    return text


def preprocess_for_tfidf(text: str) -> str:
    """Preprocessing специально для TF-IDF моделей.
    
    TF-IDF работает лучше с:
    - Lowercase
    - Без стоп-слов
    - С лемматизацией
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст для TF-IDF
    """
    return preprocess_text(
        text,
        lowercase=True,
        remove_stops=True,
        lemmatize=True
    )


def preprocess_for_bert(text: str) -> str:
    """Preprocessing специально для BERT моделей.
    
    BERT работает лучше с:
    - Минимальной обработкой
    - БЕЗ удаления стоп-слов (контекст важен)
    - БЕЗ лемматизации (понимает формы слов)
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст для BERT
    """
    return preprocess_text(
        text,
        lowercase=True,
        remove_stops=False,   # НЕ удаляем
        lemmatize=False       # НЕ лемматизируем
    )


# ===== UTILITY FUNCTIONS =====

def truncate_text(text: str, max_length: int = 512) -> str:
    """Обрезает текст до максимальной длины.
    
    Зачем: BERT models имеют лимит 512 токенов.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина в токенах
        
    Returns:
        Обрезанный текст
    """
    tokens = tokenize(text)
    
    if len(tokens) <= max_length:
        return text
    
    # Берем первые max_length токенов
    truncated_tokens = tokens[:max_length]
    return ' '.join(truncated_tokens)


def get_text_stats(text: str) -> dict:
    """Получает статистику текста.
    
    Полезно для анализа и debugging.
    
    Args:
        text: Текст
        
    Returns:
        Словарь со статистикой
    """
    tokens = tokenize(text)
    
    return {
        'length': len(text),
        'tokens': len(tokens),
        'words': len([t for t in tokens if t.isalpha()]),
        'sentences': len(re.split(r'[.!?]+', text)),
        'avg_word_length': sum(len(t) for t in tokens) / len(tokens) if tokens else 0
    }


# ===== USAGE EXAMPLES =====
"""
Примеры использования:

# Для классического ML (TF-IDF):
text = "<p>Apple releases new iPhone! Check it out: http://apple.com</p>"
clean_text = preprocess_for_tfidf(text)
print(clean_text)  # "apple release new iphone check"

# Для BERT моделей:
text = "<p>Apple releases new iPhone! Check it out: http://apple.com</p>"
clean_text = preprocess_for_bert(text)
print(clean_text)  # "apple releases new iphone check it out"

# Кастомный pipeline:
text = "The BEST product EVER!!! $$$"
clean_text = preprocess_text(
    text,
    lowercase=True,
    remove_special_chars=True,
    remove_stops=False
)
print(clean_text)  # "the best product ever"

# Статистика:
stats = get_text_stats("Hello world! This is a test.")
print(stats)
# {'length': 28, 'tokens': 7, 'words': 6, 'sentences': 2, ...}
"""