"""
Text Utilities

Утилиты для обработки текста новостей.

====== ЧТО ЗДЕСЬ? ======

1. Text cleaning - очистка HTML, спецсимволов
2. Text extraction - извлечение главного контента
3. Readability - определение читабельности
4. Word counting - подсчет слов
5. Summary generation - краткое описание
"""

import re
import html
from typing import Optional, List
from bs4 import BeautifulSoup
import logging

# Для извлечения главного контента
try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False
    
try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False


logger = logging.getLogger(__name__)


# ===== HTML CLEANING =====

def remove_html_tags(text: str) -> str:
    """Удалить все HTML теги.
    
    Args:
        text: Текст с HTML
    
    Returns:
        Чистый текст
        
    Example:
        >>> text = "<p>Hello <b>world</b></p>"
        >>> remove_html_tags(text)
        'Hello world'
    """
    # BeautifulSoup - самый надежный способ
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


def html_to_markdown(html_content: str) -> str:
    """Конвертировать HTML в Markdown.
    
    Сохраняет структуру (заголовки, списки, ссылки).
    
    Args:
        html_content: HTML контент
    
    Returns:
        Markdown текст
    """
    if not HTML2TEXT_AVAILABLE:
        return remove_html_tags(html_content)
    
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    
    return h.handle(html_content)


def extract_main_content(html_content: str) -> str:
    """Извлечь главный контент статьи из HTML.
    
    Использует readability для удаления навигации, рекламы, и т.д.
    
    Args:
        html_content: Полный HTML страницы
    
    Returns:
        Главный контент статьи
        
    Example:
        >>> html = "<html>...navigation...<article>Main content</article>...ads...</html>"
        >>> extract_main_content(html)
        'Main content'
    """
    if not READABILITY_AVAILABLE:
        logger.warning("readability-lxml not available, using basic extraction")
        return remove_html_tags(html_content)
    
    try:
        # readability извлекает главный контент
        doc = Document(html_content)
        
        # Получаем чистый HTML главного контента
        main_html = doc.summary()
        
        # Конвертируем в текст
        return remove_html_tags(main_html)
        
    except Exception as e:
        logger.error(f"Error extracting main content: {e}")
        return remove_html_tags(html_content)


# ===== TEXT CLEANING =====

def clean_text(text: str) -> str:
    """Полная очистка текста.
    
    Удаляет:
    - HTML теги
    - Лишние пробелы
    - Спецсимволы
    - HTML entities (&nbsp;, &amp;, и т.д.)
    
    Args:
        text: Исходный текст
    
    Returns:
        Очищенный текст
    """
    # 1. Декодируем HTML entities
    text = html.unescape(text)
    
    # 2. Удаляем HTML теги
    text = remove_html_tags(text)
    
    # 3. Удаляем URLs
    text = re.sub(r'http\S+', '', text)
    
    # 4. Удаляем email
    text = re.sub(r'\S+@\S+', '', text)
    
    # 5. Удаляем множественные пробелы
    text = re.sub(r'\s+', ' ', text)
    
    # 6. Удаляем множественные переносы строк
    text = re.sub(r'\n+', '\n', text)
    
    # 7. Trim
    text = text.strip()
    
    return text


def remove_extra_whitespace(text: str) -> str:
    """Удалить лишние пробелы и переносы.
    
    Args:
        text: Текст
    
    Returns:
        Текст без лишних пробелов
    """
    # Множественные пробелы → один пробел
    text = re.sub(r' +', ' ', text)
    
    # Множественные переносы → один перенос
    text = re.sub(r'\n+', '\n', text)
    
    # Пробелы в начале/конце строк
    lines = [line.strip() for line in text.split('\n')]
    
    return '\n'.join(lines).strip()


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """Удалить спецсимволы.
    
    Args:
        text: Текст
        keep_punctuation: Сохранить пунктуацию (. , ! ? и т.д.)
    
    Returns:
        Очищенный текст
    """
    if keep_punctuation:
        # Оставляем буквы, цифры, пробелы и пунктуацию
        pattern = r'[^a-zA-Z0-9\s.,!?;:\'\"-]'
    else:
        # Оставляем только буквы, цифры и пробелы
        pattern = r'[^a-zA-Z0-9\s]'
    
    return re.sub(pattern, '', text)


# ===== TEXT ANALYSIS =====

def count_words(text: str) -> int:
    """Подсчитать количество слов.
    
    Args:
        text: Текст
    
    Returns:
        Количество слов
    """
    return len(text.split())


def count_sentences(text: str) -> int:
    """Подсчитать количество предложений.
    
    Args:
        text: Текст
    
    Returns:
        Количество предложений
    """
    # Простой подсчет по точкам, восклицательным и вопросительным знакам
    sentences = re.split(r'[.!?]+', text)
    # Убираем пустые
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Оценить время чтения.
    
    Args:
        text: Текст
        words_per_minute: Скорость чтения (слов/мин)
    
    Returns:
        Время чтения в минутах
        
    Example:
        >>> text = "..." * 500  # 500 слов
        >>> estimate_reading_time(text)
        3  # минуты
    """
    word_count = count_words(text)
    minutes = word_count / words_per_minute
    return max(1, int(minutes))  # Минимум 1 минута


def get_flesch_reading_ease(text: str) -> float:
    """Рассчитать Flesch Reading Ease score.
    
    Шкала:
    - 90-100: Very Easy (5th grade)
    - 80-90: Easy (6th grade)
    - 70-80: Fairly Easy (7th grade)
    - 60-70: Standard (8th-9th grade)
    - 50-60: Fairly Difficult (10th-12th grade)
    - 30-50: Difficult (College)
    - 0-30: Very Difficult (College graduate)
    
    Args:
        text: Текст
    
    Returns:
        Score (0-100)
    """
    words = count_words(text)
    sentences = count_sentences(text)
    
    if sentences == 0 or words == 0:
        return 0.0
    
    # Подсчет слогов (упрощенно - по гласным)
    syllables = sum(len(re.findall(r'[aeiouAEIOU]+', word)) for word in text.split())
    
    # Формула Flesch
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    
    return max(0, min(100, score))


# ===== TEXT TRUNCATION =====

def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """Обрезать текст до определенной длины.
    
    Обрезает по словам, не разрывая слова.
    
    Args:
        text: Текст
        max_length: Максимальная длина
        suffix: Что добавить в конце
    
    Returns:
        Обрезанный текст
        
    Example:
        >>> text = "This is a very long text that needs truncation"
        >>> truncate_text(text, max_length=20)
        'This is a very...'
    """
    if len(text) <= max_length:
        return text
    
    # Обрезаем с запасом
    truncated = text[:max_length - len(suffix)]
    
    # Находим последний пробел
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix


def extract_first_paragraph(text: str) -> str:
    """Извлечь первый параграф.
    
    Args:
        text: Текст
    
    Returns:
        Первый параграф
    """
    paragraphs = text.split('\n\n')
    return paragraphs[0].strip() if paragraphs else ""


def extract_sentences(text: str, n: int = 3) -> str:
    """Извлечь первые N предложений.
    
    Args:
        text: Текст
        n: Количество предложений
    
    Returns:
        Первые N предложений
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    selected = sentences[:n]
    return '. '.join(selected) + '.'


# ===== TEXT EXTRACTION FROM HTML =====

def extract_text_from_element(
    html: str,
    selector: str,
    multiple: bool = False
) -> Optional[str]:
    """Извлечь текст по CSS селектору.
    
    Args:
        html: HTML контент
        selector: CSS selector
        multiple: Вернуть все совпадения
    
    Returns:
        Текст или None
        
    Example:
        >>> html = "<div class='article'><p>Text</p></div>"
        >>> extract_text_from_element(html, 'div.article p')
        'Text'
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    if multiple:
        elements = soup.select(selector)
        return ' '.join(el.get_text(strip=True) for el in elements)
    else:
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None


# ===== DOMAIN EXTRACTION =====

def extract_domain(url: str) -> str:
    """Извлечь домен из URL.
    
    Args:
        url: URL
    
    Returns:
        Домен
        
    Example:
        >>> extract_domain("https://www.bbc.co.uk/news/article")
        'bbc.co.uk'
    """
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Убираем www.
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain


# ===== USAGE EXAMPLES =====
"""
# ===== HTML Cleaning =====

from app.utils.text_utils import remove_html_tags, extract_main_content

html = '''
<html>
<body>
    <nav>Navigation</nav>
    <article>
        <h1>Article Title</h1>
        <p>This is the <b>main content</b> of the article.</p>
    </article>
    <aside>Advertisement</aside>
</body>
</html>
'''

# Убрать все теги
clean = remove_html_tags(html)
print(clean)

# Извлечь главный контент
main = extract_main_content(html)
print(main)


# ===== Text Cleaning =====

from app.utils.text_utils import clean_text

messy_text = "  Check   this  out:  https://example.com  &nbsp;  contact@email.com  "
clean = clean_text(messy_text)
print(clean)  # "Check this out:"


# ===== Text Analysis =====

from app.utils.text_utils import (
    count_words,
    count_sentences,
    estimate_reading_time,
    get_flesch_reading_ease
)

article = "This is a sample article. It has multiple sentences. Let's analyze it!"

print(f"Words: {count_words(article)}")
print(f"Sentences: {count_sentences(article)}")
print(f"Reading time: {estimate_reading_time(article)} min")
print(f"Readability: {get_flesch_reading_ease(article)}")


# ===== Text Truncation =====

from app.utils.text_utils import truncate_text, extract_sentences

long_text = "This is a very long article about various topics. " * 10

# Обрезать до 100 символов
short = truncate_text(long_text, max_length=100)
print(short)

# Первые 2 предложения
summary = extract_sentences(long_text, n=2)
print(summary)
"""