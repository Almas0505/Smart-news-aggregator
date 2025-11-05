"""
Pydantic Schemas для ML Service API

Эти схемы определяют формат входных и выходных данных для API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal


# ===== REQUEST SCHEMAS =====

class TextRequest(BaseModel):
    """Базовый запрос с одним текстом."""
    
    text: str = Field(
        ...,
        description="Текст для обработки",
        min_length=1,
        max_length=10000,
        examples=["Apple announces new iPhone with AI features"]
    )


class TextBatchRequest(BaseModel):
    """Запрос с множеством текстов."""
    
    texts: List[str] = Field(
        ...,
        description="Список текстов для обработки",
        min_items=1,
        max_items=100
    )
    batch_size: int = Field(
        default=32,
        description="Размер батча для обработки",
        ge=1,
        le=128
    )


class ClassificationRequest(TextRequest):
    """Запрос на классификацию текста."""
    
    min_confidence: float = Field(
        default=0.0,
        description="Минимальная уверенность для возврата результата",
        ge=0.0,
        le=1.0
    )


class SummarizationRequest(TextRequest):
    """Запрос на суммаризацию."""
    
    max_length: int = Field(
        default=130,
        description="Максимальная длина summary (в токенах)",
        ge=20,
        le=500
    )
    min_length: int = Field(
        default=30,
        description="Минимальная длина summary (в токенах)",
        ge=10,
        le=100
    )
    method: Literal["extractive", "abstractive", "hybrid"] = Field(
        default="extractive",
        description="Метод суммаризации"
    )
    num_sentences: Optional[int] = Field(
        default=3,
        description="Количество предложений (для extractive)",
        ge=1,
        le=10
    )


class SimilarityRequest(BaseModel):
    """Запрос на вычисление similarity."""
    
    text1: str = Field(..., description="Первый текст")
    text2: str = Field(..., description="Второй текст")


class SemanticSearchRequest(BaseModel):
    """Запрос на semantic search."""
    
    query: str = Field(..., description="Поисковый запрос")
    candidates: List[str] = Field(
        ...,
        description="Список текстов для поиска",
        min_items=1
    )
    top_k: int = Field(
        default=5,
        description="Количество результатов",
        ge=1,
        le=100
    )


# ===== RESPONSE SCHEMAS =====

class ClassificationResponse(BaseModel):
    """Результат классификации."""
    
    category: str = Field(..., description="Категория новости")
    confidence: float = Field(..., description="Уверенность (0.0-1.0)")
    all_probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Вероятности всех категорий"
    )


class EntityResponse(BaseModel):
    """Одна извлеченная сущность."""
    
    text: str = Field(..., description="Текст сущности")
    type: str = Field(..., description="Тип (PERSON, ORG, LOC, и т.д.)")
    start: int = Field(..., description="Начальная позиция в тексте")
    end: int = Field(..., description="Конечная позиция в тексте")
    confidence: float = Field(..., description="Уверенность")


class NERResponse(BaseModel):
    """Результат NER."""
    
    entities: List[EntityResponse] = Field(..., description="Найденные сущности")
    entity_counts: Dict[str, int] = Field(
        ...,
        description="Количество каждого типа сущностей"
    )


class SentimentResponse(BaseModel):
    """Результат sentiment analysis."""
    
    label: Literal["positive", "negative", "neutral"] = Field(
        ...,
        description="Sentiment label"
    )
    score: float = Field(
        ...,
        description="Score (-1.0 = очень негативный, +1.0 = очень позитивный)"
    )
    confidence: float = Field(..., description="Уверенность (0.0-1.0)")


class SummarizationResponse(BaseModel):
    """Результат суммаризации."""
    
    summary: str = Field(..., description="Сгенерированное резюме")
    original_length: int = Field(..., description="Длина оригинала (слова)")
    summary_length: int = Field(..., description="Длина резюме (слова)")
    compression_ratio: float = Field(
        ...,
        description="Степень сжатия (0.0-1.0)"
    )
    method: str = Field(..., description="Использованный метод")


class EmbeddingResponse(BaseModel):
    """Результат создания embedding."""
    
    embedding: List[float] = Field(
        ...,
        description="Векторное представление"
    )
    dimension: int = Field(..., description="Размерность вектора")


class SimilarityResponse(BaseModel):
    """Результат вычисления similarity."""
    
    similarity: float = Field(
        ...,
        description="Similarity score (0.0-1.0)"
    )


class SearchResultResponse(BaseModel):
    """Один результат поиска."""
    
    index: int = Field(..., description="Индекс в исходном списке")
    text: str = Field(..., description="Найденный текст")
    score: float = Field(..., description="Relevance score")


class SemanticSearchResponse(BaseModel):
    """Результаты semantic search."""
    
    results: List[SearchResultResponse] = Field(
        ...,
        description="Найденные результаты"
    )
    query: str = Field(..., description="Исходный запрос")


class CompletePredictionResponse(BaseModel):
    """Полный результат обработки новости (все модели сразу)."""
    
    classification: ClassificationResponse
    ner: NERResponse
    sentiment: SentimentResponse
    summary: SummarizationResponse
    embedding: Optional[List[float]] = None


# ===== ERROR RESPONSES =====

class ErrorResponse(BaseModel):
    """Сообщение об ошибке."""
    
    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(default=None, description="Детали")


# ===== HEALTH CHECK =====

class HealthResponse(BaseModel):
    """Статус сервиса."""
    
    status: str = Field(..., description="Статус (healthy/unhealthy)")
    models_loaded: Dict[str, bool] = Field(
        ...,
        description="Какие модели загружены"
    )
    version: str = Field(..., description="Версия API")