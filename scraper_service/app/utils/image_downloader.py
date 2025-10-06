"""
Image Downloader

Утилиты для скачивания и обработки изображений новостей.

====== ФУНКЦИИ ======

1. Download images - скачивание по URL
2. Resize images - изменение размера
3. Validate images - проверка валидности
4. Extract dominant color - определение основного цвета
5. Upload to storage - загрузка в хранилище
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
import io

import requests
from PIL import Image

from app.config import settings


logger = logging.getLogger(__name__)


# ===== IMAGE DOWNLOAD =====

def download_image(
    url: str,
    save_dir: Optional[str] = None,
    timeout: int = 30
) -> Optional[str]:
    """Скачать изображение по URL.
    
    Args:
        url: URL изображения
        save_dir: Директория для сохранения
        timeout: Таймаут запроса
    
    Returns:
        Путь к сохраненному файлу или None
        
    Example:
        >>> url = "https://example.com/image.jpg"
        >>> path = download_image(url)
        >>> print(path)
        './data/images/abc123.jpg'
    """
    if not url:
        return None
    
    try:
        logger.debug(f"Downloading image: {url}")
        
        # Скачиваем
        response = requests.get(
            url,
            timeout=timeout,
            headers={'User-Agent': settings.USER_AGENT}
        )
        
        response.raise_for_status()
        
        # Проверяем размер
        content_length = int(response.headers.get('content-length', 0))
        max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        
        if content_length > max_size_bytes:
            logger.warning(f"Image too large: {content_length} bytes")
            return None
        
        # Проверяем content-type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"Invalid content type: {content_type}")
            return None
        
        # Генерируем имя файла
        filename = generate_image_filename(url, response.content)
        
        # Определяем директорию
        if save_dir is None:
            save_dir = settings.IMAGES_DIR
        
        # Создаем директорию
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу
        filepath = os.path.join(save_dir, filename)
        
        # Сохраняем
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Image saved: {filepath}")
        
        return filepath
        
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        return None
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return None


def generate_image_filename(url: str, content: bytes) -> str:
    """Сгенерировать уникальное имя файла.
    
    Использует MD5 hash контента для уникальности.
    
    Args:
        url: URL изображения
        content: Бинарный контент
    
    Returns:
        Имя файла
        
    Example:
        >>> generate_image_filename("https://example.com/photo.jpg", b"...")
        'abc123def456.jpg'
    """
    # MD5 hash контента
    hash_obj = hashlib.md5(content)
    file_hash = hash_obj.hexdigest()
    
    # Расширение из URL
    parsed = urlparse(url)
    path = parsed.path
    ext = os.path.splitext(path)[1] or '.jpg'
    
    return f"{file_hash}{ext}"


# ===== IMAGE PROCESSING =====

def resize_image(
    image_path: str,
    max_width: int = 1200,
    max_height: int = 800,
    quality: int = 85
) -> Optional[str]:
    """Изменить размер изображения.
    
    Сохраняет aspect ratio.
    
    Args:
        image_path: Путь к изображению
        max_width: Максимальная ширина
        max_height: Максимальная высота
        quality: Качество JPEG (1-100)
    
    Returns:
        Путь к измененному изображению
        
    Example:
        >>> resize_image('photo.jpg', max_width=800)
        'photo_resized.jpg'
    """
    try:
        # Открываем
        img = Image.open(image_path)
        
        # Текущий размер
        width, height = img.size
        
        # Проверяем нужно ли изменять
        if width <= max_width and height <= max_height:
            logger.debug("Image already within size limits")
            return image_path
        
        # Рассчитываем новый размер (сохраняя aspect ratio)
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        
        # Resize
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Новое имя файла
        base, ext = os.path.splitext(image_path)
        new_path = f"{base}_resized{ext}"
        
        # Сохраняем
        if img_resized.mode == 'RGBA':
            # Конвертируем RGBA в RGB для JPEG
            img_resized = img_resized.convert('RGB')
        
        img_resized.save(new_path, quality=quality, optimize=True)
        
        logger.info(f"Image resized: {new_size}")
        
        return new_path
        
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return None


def create_thumbnail(
    image_path: str,
    size: Tuple[int, int] = (300, 200)
) -> Optional[str]:
    """Создать thumbnail (миниатюру).
    
    Args:
        image_path: Путь к изображению
        size: Размер thumbnail (width, height)
    
    Returns:
        Путь к thumbnail
    """
    try:
        img = Image.open(image_path)
        
        # Создаем thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Новый путь
        base, ext = os.path.splitext(image_path)
        thumb_path = f"{base}_thumb{ext}"
        
        # Сохраняем
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        img.save(thumb_path, quality=85, optimize=True)
        
        logger.info(f"Thumbnail created: {thumb_path}")
        
        return thumb_path
        
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None


# ===== IMAGE VALIDATION =====

def validate_image(image_path: str) -> bool:
    """Проверить что файл - валидное изображение.
    
    Args:
        image_path: Путь к файлу
    
    Returns:
        True если валидное
    """
    try:
        img = Image.open(image_path)
        img.verify()  # Проверка целостности
        return True
    except Exception as e:
        logger.error(f"Invalid image: {e}")
        return False


def get_image_info(image_path: str) -> Optional[dict]:
    """Получить информацию об изображении.
    
    Args:
        image_path: Путь к изображению
    
    Returns:
        Словарь с информацией
        
    Example:
        >>> get_image_info('photo.jpg')
        {
            'format': 'JPEG',
            'mode': 'RGB',
            'size': (1920, 1080),
            'width': 1920,
            'height': 1080,
            'file_size': 245678
        }
    """
    try:
        img = Image.open(image_path)
        
        file_size = os.path.getsize(image_path)
        
        return {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.size[0],
            'height': img.size[1],
            'file_size': file_size
        }
        
    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        return None


# ===== IMAGE ANALYSIS =====

def get_dominant_color(image_path: str) -> Optional[Tuple[int, int, int]]:
    """Определить доминирующий цвет изображения.
    
    Args:
        image_path: Путь к изображению
    
    Returns:
        RGB tuple или None
        
    Example:
        >>> get_dominant_color('photo.jpg')
        (45, 123, 200)  # RGB
    """
    try:
        img = Image.open(image_path)
        
        # Resize для ускорения
        img = img.resize((150, 150))
        
        # Конвертируем в RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Получаем все цвета
        pixels = list(img.getdata())
        
        # Самый частый цвет
        from collections import Counter
        most_common = Counter(pixels).most_common(1)[0][0]
        
        return most_common
        
    except Exception as e:
        logger.error(f"Error getting dominant color: {e}")
        return None


def is_image_too_dark(image_path: str, threshold: int = 50) -> bool:
    """Проверить не слишком ли темное изображение.
    
    Args:
        image_path: Путь к изображению
        threshold: Порог яркости (0-255)
    
    Returns:
        True если слишком темное
    """
    try:
        img = Image.open(image_path)
        
        # Конвертируем в grayscale
        img_gray = img.convert('L')
        
        # Средняя яркость
        import numpy as np
        pixels = np.array(img_gray)
        avg_brightness = pixels.mean()
        
        return avg_brightness < threshold
        
    except Exception as e:
        logger.error(f"Error checking brightness: {e}")
        return False


# ===== BATCH OPERATIONS =====

def download_images_batch(urls: list, save_dir: Optional[str] = None) -> list:
    """Скачать несколько изображений.
    
    Args:
        urls: Список URLs
        save_dir: Директория для сохранения
    
    Returns:
        Список путей к скачанным файлам
    """
    results = []
    
    for url in urls:
        filepath = download_image(url, save_dir)
        if filepath:
            results.append(filepath)
    
    logger.info(f"Downloaded {len(results)}/{len(urls)} images")
    
    return results


def process_image(
    image_path: str,
    resize_to: Optional[Tuple[int, int]] = None,
    create_thumb: bool = True
) -> dict:
    """Полная обработка изображения.
    
    Args:
        image_path: Путь к изображению
        resize_to: Размер для resize
        create_thumb: Создать thumbnail
    
    Returns:
        Словарь с путями к обработанным файлам
    """
    result = {
        'original': image_path,
        'resized': None,
        'thumbnail': None,
        'info': None
    }
    
    # Валидация
    if not validate_image(image_path):
        logger.error(f"Invalid image: {image_path}")
        return result
    
    # Info
    result['info'] = get_image_info(image_path)
    
    # Resize
    if resize_to:
        resized = resize_image(image_path, *resize_to)
        result['resized'] = resized
    
    # Thumbnail
    if create_thumb:
        thumb = create_thumbnail(image_path)
        result['thumbnail'] = thumb
    
    return result


# ===== USAGE EXAMPLES =====
"""
# ===== Download Image =====

from app.utils.image_downloader import download_image

url = "https://example.com/news-photo.jpg"
filepath = download_image(url, save_dir='./data/images')

if filepath:
    print(f"Image saved: {filepath}")


# ===== Resize Image =====

from app.utils.image_downloader import resize_image

resized = resize_image(
    filepath,
    max_width=800,
    max_height=600
)


# ===== Create Thumbnail =====

from app.utils.image_downloader import create_thumbnail

thumb = create_thumbnail(filepath, size=(300, 200))


# ===== Get Image Info =====

from app.utils.image_downloader import get_image_info

info = get_image_info(filepath)
print(f"Size: {info['width']}x{info['height']}")
print(f"Format: {info['format']}")
print(f"File size: {info['file_size']} bytes")


# ===== Batch Download =====

from app.utils.image_downloader import download_images_batch

urls = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg",
]

downloaded = download_images_batch(urls)
print(f"Downloaded: {len(downloaded)} images")


# ===== Full Processing =====

from app.utils.image_downloader import process_image

result = process_image(
    filepath,
    resize_to=(1200, 800),
    create_thumb=True
)

print(f"Original: {result['original']}")
print(f"Resized: {result['resized']}")
print(f"Thumbnail: {result['thumbnail']}")
print(f"Info: {result['info']}")


# ===== Image Analysis =====

from app.utils.image_downloader import get_dominant_color, is_image_too_dark

color = get_dominant_color(filepath)
print(f"Dominant color (RGB): {color}")

too_dark = is_image_too_dark(filepath)
if too_dark:
    print("Warning: Image is too dark")
"""