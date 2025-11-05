"""
Model Loader Utilities

Утилиты для загрузки и управления ML моделями.
Реализует lazy loading и caching моделей.
"""

import logging
from typing import Dict, Optional, Any
from pathlib import Path
import joblib
from functools import lru_cache

from app.config import settings


logger = logging.getLogger(__name__)


# ===== MODEL REGISTRY =====

class ModelRegistry:
    """Реестр всех доступных моделей.
    
    Singleton pattern для централизованного управления моделями.
    """
    
    _instance = None
    _models: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Инициализация реестра."""
        if not hasattr(self, 'initialized'):
            self._models = {}
            self.initialized = True
            logger.info("Model registry initialized")
    
    def register(self, name: str, model: Any):
        """Зарегистрировать модель.
        
        Args:
            name: Название модели
            model: Экземпляр модели
        """
        self._models[name] = model
        logger.info(f"Model registered: {name}")
    
    def get(self, name: str) -> Optional[Any]:
        """Получить модель по имени.
        
        Args:
            name: Название модели
        
        Returns:
            Модель или None
        """
        return self._models.get(name)
    
    def unregister(self, name: str):
        """Удалить модель из реестра.
        
        Args:
            name: Название модели
        """
        if name in self._models:
            del self._models[name]
            logger.info(f"Model unregistered: {name}")
    
    def list_models(self) -> list:
        """Список всех зарегистрированных моделей."""
        return list(self._models.keys())
    
    def clear(self):
        """Очистить все модели."""
        self._models.clear()
        logger.info("Model registry cleared")


# ===== LAZY MODEL LOADER =====

class LazyModelLoader:
    """Ленивая загрузка моделей - загружаются только при первом обращении."""
    
    def __init__(self):
        """Инициализация."""
        self.registry = ModelRegistry()
        self._loaders = {}
    
    def register_loader(self, name: str, loader_func):
        """Зарегистрировать функцию загрузки модели.
        
        Args:
            name: Название модели
            loader_func: Функция загрузки (callable)
        """
        self._loaders[name] = loader_func
        logger.info(f"Loader registered for: {name}")
    
    def load(self, name: str, force_reload: bool = False) -> Any:
        """Загрузить модель.
        
        Если модель уже загружена, вернет закешированную версию.
        
        Args:
            name: Название модели
            force_reload: Принудительная перезагрузка
        
        Returns:
            Модель
        """
        # Проверяем кеш
        if not force_reload:
            cached = self.registry.get(name)
            if cached is not None:
                logger.debug(f"Model loaded from cache: {name}")
                return cached
        
        # Загружаем
        if name not in self._loaders:
            raise ValueError(f"No loader registered for model: {name}")
        
        logger.info(f"Loading model: {name}")
        
        loader_func = self._loaders[name]
        model = loader_func()
        
        # Кешируем
        self.registry.register(name, model)
        
        return model
    
    def unload(self, name: str):
        """Выгрузить модель из памяти.
        
        Args:
            name: Название модели
        """
        self.registry.unregister(name)


# ===== SPECIFIC LOADERS =====

@lru_cache(maxsize=1)
def load_spacy_model(model_name: str = settings.SPACY_MODEL):
    """Загрузить spaCy модель с кешированием.
    
    Args:
        model_name: Название модели
    
    Returns:
        spaCy nlp object
    """
    import spacy
    
    logger.info(f"Loading spaCy model: {model_name}")
    
    try:
        nlp = spacy.load(model_name)
        logger.info(f"✅ spaCy model loaded: {model_name}")
        return nlp
    except OSError:
        logger.error(f"❌ spaCy model not found: {model_name}")
        logger.info(f"Install with: python -m spacy download {model_name}")
        raise


@lru_cache(maxsize=1)
def load_sentence_transformer(model_name: str = settings.EMBEDDING_MODEL):
    """Загрузить Sentence Transformer модель.
    
    Args:
        model_name: Название модели
    
    Returns:
        SentenceTransformer object
    """
    from sentence_transformers import SentenceTransformer
    
    logger.info(f"Loading Sentence Transformer: {model_name}")
    
    model = SentenceTransformer(model_name)
    
    logger.info(f"✅ Sentence Transformer loaded: {model_name}")
    
    return model


def load_classifier_from_file(filepath: str):
    """Загрузить обученный классификатор из файла.
    
    Args:
        filepath: Путь к модели
    
    Returns:
        Классификатор
    """
    logger.info(f"Loading classifier from: {filepath}")
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Model file not found: {filepath}")
    
    model_data = joblib.load(filepath)
    
    # Создаем экземпляр классификатора
    from app.models.classifier import TfidfClassifier
    
    classifier = TfidfClassifier()
    classifier.vectorizer = model_data['vectorizer']
    classifier.model = model_data['model']
    classifier.label_to_category = model_data['label_to_category']
    classifier.category_to_label = model_data['category_to_label']
    
    logger.info("✅ Classifier loaded successfully")
    
    return classifier


# ===== MODEL HEALTH CHECK =====

def check_model_health(model_name: str) -> Dict[str, Any]:
    """Проверить что модель работает корректно.
    
    Args:
        model_name: Название модели
    
    Returns:
        Статус модели
    """
    registry = ModelRegistry()
    model = registry.get(model_name)
    
    if model is None:
        return {
            'name': model_name,
            'status': 'not_loaded',
            'loaded': False
        }
    
    # Простая проверка - пытаемся вызвать метод
    try:
        # Разные модели имеют разные методы
        if hasattr(model, 'encode'):
            # Embedding модель
            _ = model.encode("test")
        elif hasattr(model, 'extract_entities'):
            # NER модель
            _ = model.extract_entities("test")
        elif hasattr(model, 'analyze'):
            # Sentiment модель
            _ = model.analyze("test")
        
        return {
            'name': model_name,
            'status': 'healthy',
            'loaded': True
        }
        
    except Exception as e:
        return {
            'name': model_name,
            'status': 'error',
            'loaded': True,
            'error': str(e)
        }


def get_all_models_status() -> Dict[str, Dict]:
    """Получить статус всех моделей.
    
    Returns:
        Словарь со статусами
    """
    registry = ModelRegistry()
    models = registry.list_models()
    
    status = {}
    for model_name in models:
        status[model_name] = check_model_health(model_name)
    
    return status


# ===== GLOBAL INSTANCE =====

# Singleton loader
model_loader = LazyModelLoader()


# ===== USAGE EXAMPLES =====
"""
# ===== Basic Usage =====

from app.utils.model_loader import model_loader, load_spacy_model

# Регистрируем loader
model_loader.register_loader('ner', lambda: load_spacy_model())

# Загружаем (ленивая загрузка)
ner_model = model_loader.load('ner')

# Повторная загрузка - вернет из кеша
ner_model_cached = model_loader.load('ner')  # Быстро!


# ===== Model Registry =====

from app.utils.model_loader import ModelRegistry

registry = ModelRegistry()

# Регистрируем
registry.register('my_model', my_model_instance)

# Получаем
model = registry.get('my_model')

# Список всех моделей
models = registry.list_models()


# ===== Health Check =====

from app.utils.model_loader import get_all_models_status

status = get_all_models_status()
print(status)
# {
#     'ner': {'name': 'ner', 'status': 'healthy', 'loaded': True},
#     'sentiment': {'name': 'sentiment', 'status': 'healthy', 'loaded': True}
# }


# ===== Load Classifier =====

from app.utils.model_loader import load_classifier_from_file

classifier = load_classifier_from_file('./saved_models/classifier.joblib')
category, conf = classifier.predict("News about AI")
"""