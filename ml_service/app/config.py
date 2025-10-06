"""
ML Service Configuration

Этот файл содержит все настройки для ML сервиса.
Объяснение каждой настройки и зачем она нужна.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Settings для ML сервиса.
    
    Pydantic автоматически:
    1. Загружает переменные из .env файла
    2. Валидирует типы данных
    3. Предоставляет значения по умолчанию
    """
    
    # ===== API SETTINGS =====
    # Базовые настройки FastAPI приложения
    
    APP_NAME: str = "Smart News ML Service"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False  # True для development, False для production
    
    # ===== SERVER SETTINGS =====
    # Где запускается сервис
    
    HOST: str = "0.0.0.0"  # 0.0.0.0 = доступен со всех IP
    PORT: int = 8001        # Порт (backend на 8000, ml на 8001)
    
    # ===== BACKEND INTEGRATION =====
    # URL backend сервиса для отправки результатов
    
    BACKEND_URL: str = "http://backend:8000"  # В Docker: имя контейнера
    # Для локальной разработки: "http://localhost:8000"
    
    # ===== MODEL PATHS =====
    # Где хранятся обученные модели
    
    # Корневая директория для моделей
    MODELS_DIR: str = "./saved_models"
    
    # Пути к конкретным моделям
    CLASSIFIER_MODEL_PATH: str = f"{MODELS_DIR}/classifier.joblib"
    VECTORIZER_PATH: str = f"{MODELS_DIR}/vectorizer.joblib"
    SENTIMENT_MODEL_PATH: str = f"{MODELS_DIR}/sentiment.joblib"
    
    # ===== SPACY SETTINGS =====
    # Настройки для spaCy (NER)
    
    SPACY_MODEL: str = "en_core_web_sm"  # Маленькая модель (быстрая)
    # Альтернативы:
    # "en_core_web_md" - средняя модель (точнее)
    # "en_core_web_lg" - большая модель (самая точная, но медленная)
    
    # ===== TRANSFORMERS SETTINGS =====
    # Настройки для Hugging Face моделей
    
    # Модель для классификации
    CLASSIFICATION_MODEL: str = "distilbert-base-uncased"
    # Это легкая версия BERT, быстрая и точная
    # Альтернативы: "bert-base-uncased", "roberta-base"
    
    # Модель для sentiment analysis
    SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    # Специально обученная для sentiment analysis
    
    # Модель для суммаризации
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    # BART модель от Facebook, обученная на новостях CNN
    # Альтернатива: "google/pegasus-xsum"
    
    # Модель для embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    # Быстрая и эффективная модель для векторизации
    # Создает 384-мерные векторы
    # Альтернативы: "all-mpnet-base-v2" (лучше, но медленнее)
    
    # ===== MODEL PARAMETERS =====
    # Параметры для обработки
    
    # Максимальная длина текста для моделей
    MAX_LENGTH: int = 512  # BERT models имеют лимит 512 токенов
    
    # Batch size для обработки множества текстов
    BATCH_SIZE: int = 32  # Обрабатываем по 32 текста за раз
    
    # Minimum confidence threshold
    MIN_CONFIDENCE: float = 0.5  # Игнорируем результаты с уверенностью < 50%
    
    # ===== CATEGORIES =====
    # Категории новостей для классификации
    
    NEWS_CATEGORIES: List[str] = [
        "technology",      # Технологии
        "business",        # Бизнес
        "politics",        # Политика
        "sports",          # Спорт
        "entertainment",   # Развлечения
        "science",         # Наука
        "health",          # Здоровье
        "world",           # Мировые новости
        "education",       # Образование
        "environment"      # Экология
    ]
    
    # ===== ENTITY TYPES =====
    # Типы сущностей для NER
    
    ENTITY_TYPES: List[str] = [
        "PERSON",          # Люди (Elon Musk)
        "ORGANIZATION",    # Организации (Tesla, Google)
        "LOCATION",        # Места (New York, Europe)
        "DATE",            # Даты (January 1st, 2024)
        "MONEY",           # Деньги ($1 million)
        "PRODUCT",         # Продукты (iPhone, Windows)
        "EVENT"            # События (Olympics, World Cup)
    ]
    
    # ===== CACHING =====
    # Кэширование результатов для ускорения
    
    ENABLE_CACHE: bool = True  # Включить кэширование
    CACHE_TTL: int = 3600      # Time to live = 1 час
    
    # ===== LOGGING =====
    # Настройки логирования
    
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FORMAT: str = "json"  # "json" или "text"
    
    # ===== MONITORING =====
    # Prometheus метрики
    
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # ===== PERFORMANCE =====
    # Оптимизация производительности
    
    # Количество worker процессов
    WORKERS: int = 4  # Для production: CPU cores * 2
    
    # Использовать GPU если доступен
    USE_GPU: bool = False  # True если есть CUDA
    DEVICE: str = "cpu"    # "cuda" для GPU
    
    # ===== TRAINING SETTINGS =====
    # Настройки для обучения моделей
    
    # Путь к тренировочным данным
    TRAINING_DATA_PATH: str = "./data/training_data.csv"
    
    # Размер тестовой выборки
    TEST_SIZE: float = 0.2  # 20% данных для тестирования
    
    # Random seed для воспроизводимости
    RANDOM_SEED: int = 42
    
    # Количество эпох обучения
    EPOCHS: int = 10
    
    # Learning rate
    LEARNING_RATE: float = 2e-5
    
    class Config:
        """Pydantic config."""
        env_file = ".env"  # Загружать из .env файла
        case_sensitive = False  # Не чувствителен к регистру


# Создаем глобальный экземпляр настроек
settings = Settings()


# ===== HELPER FUNCTIONS =====

def get_device():
    """Определить device (CPU или GPU).
    
    Returns:
        str: "cuda" если доступен GPU, иначе "cpu"
    """
    if settings.USE_GPU:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    return "cpu"


def get_model_path(model_name: str) -> str:
    """Получить полный путь к модели.
    
    Args:
        model_name: Имя модели
        
    Returns:
        str: Полный путь
    """
    import os
    return os.path.join(settings.MODELS_DIR, f"{model_name}.joblib")


# ===== USAGE EXAMPLES =====
"""
Примеры использования:

# В других файлах импортируем:
from app.config import settings

# Получаем настройки:
model_name = settings.SPACY_MODEL
categories = settings.NEWS_CATEGORIES
max_len = settings.MAX_LENGTH

# Проверяем device:
device = get_device()
print(f"Using device: {device}")

# Получаем путь к модели:
path = get_model_path("classifier")
"""