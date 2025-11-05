"""
ML Service - FastAPI Application

Это главный файл ML сервиса, который предоставляет API endpoints
для всех ML моделей.

Запуск:
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict

from app.config import settings
from app import schemas

# Импортируем модели (будут загружены при старте)
from app.models import (
    TfidfClassifier,
    NERModel,
    TransformerSentimentAnalyzer,
    SimpleSentimentAnalyzer,
    ExtractiveSummarizer,
    AbstractiveSummarizer,
    HybridSummarizer,
    TextEmbeddingModel
)


# ===== LOGGING =====

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===== GLOBAL MODEL INSTANCES =====

# Эти переменные будут хранить загруженные модели
ml_models: Dict[str, any] = {}


# ===== LIFESPAN EVENTS =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager для FastAPI.
    
    Это новый способ (FastAPI 0.109+) управления startup/shutdown событиями.
    
    startup: Загружаем ML модели в память
    shutdown: Очищаем ресурсы
    """
    # ===== STARTUP =====
    logger.info("🚀 Starting ML Service...")
    logger.info(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Загружаем NER модель
        logger.info("Loading NER model...")
        ml_models['ner'] = NERModel(settings.SPACY_MODEL)
        
        # Загружаем Sentiment модель (простую - быстрее)
        logger.info("Loading Sentiment model...")
        ml_models['sentiment'] = SimpleSentimentAnalyzer()
        # Для production: TransformerSentimentAnalyzer()
        
        # Загружаем Summarizer (extractive - быстрее)
        logger.info("Loading Summarization model...")
        ml_models['summarizer_extractive'] = ExtractiveSummarizer()
        # Опционально: AbstractiveSummarizer (медленнее)
        # ml_models['summarizer_abstractive'] = AbstractiveSummarizer()
        
        # Загружаем Embedding модель
        logger.info("Loading Embedding model...")
        ml_models['embeddings'] = TextEmbeddingModel(settings.EMBEDDING_MODEL)
        
        # Classifier (если есть обученная модель)
        # ml_models['classifier'] = TfidfClassifier()
        # ml_models['classifier'].load(settings.CLASSIFIER_MODEL_PATH)
        
        logger.info("✅ All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
        raise
    
    yield  # Приложение работает
    
    # ===== SHUTDOWN =====
    logger.info("🛑 Shutting down ML Service...")
    ml_models.clear()
    logger.info("✅ Cleanup complete")


# ===== APP INITIALIZATION =====

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ML/AI Service для обработки текста новостей",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc UI
    lifespan=lifespan
)


# ===== CORS MIDDLEWARE =====

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production: указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== ENDPOINTS =====

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get(
    "/health",
    response_model=schemas.HealthResponse,
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.
    
    Проверяет что все модели загружены и готовы к работе.
    """
    models_status = {
        "ner": "ner" in ml_models,
        "sentiment": "sentiment" in ml_models,
        "summarizer": "summarizer_extractive" in ml_models,
        "embeddings": "embeddings" in ml_models,
    }
    
    all_loaded = all(models_status.values())
    
    return schemas.HealthResponse(
        status="healthy" if all_loaded else "unhealthy",
        models_loaded=models_status,
        version=settings.APP_VERSION
    )


# ===== NER ENDPOINTS =====

@app.post(
    "/api/extract-entities",
    response_model=schemas.NERResponse,
    tags=["NER"]
)
async def extract_entities(request: schemas.TextRequest):
    """
    Извлечь именованные сущности из текста.
    
    Находит PERSON, ORGANIZATION, LOCATION, DATE, MONEY и другие.
    """
    try:
        ner_model = ml_models.get('ner')
        if not ner_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NER model not loaded"
            )
        
        # Извлекаем сущности
        entities = ner_model.extract_entities(request.text)
        
        # Подсчитываем типы
        entity_counts = {}
        for ent in entities:
            ent_type = ent["type"]
            entity_counts[ent_type] = entity_counts.get(ent_type, 0) + 1
        
        # Форматируем для response
        entity_responses = [
            schemas.EntityResponse(**ent) for ent in entities
        ]
        
        return schemas.NERResponse(
            entities=entity_responses,
            entity_counts=entity_counts
        )
        
    except Exception as e:
        logger.error(f"Error in extract_entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== SENTIMENT ENDPOINTS =====

@app.post(
    "/api/analyze-sentiment",
    response_model=schemas.SentimentResponse,
    tags=["Sentiment"]
)
async def analyze_sentiment(request: schemas.TextRequest):
    """
    Анализ тональности текста.
    
    Определяет: positive, negative, или neutral.
    """
    try:
        sentiment_model = ml_models.get('sentiment')
        if not sentiment_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sentiment model not loaded"
            )
        
        # Анализируем
        result = sentiment_model.analyze(request.text)
        
        return schemas.SentimentResponse(
            label=result["label"],
            score=result["score"],
            confidence=result["confidence"]
        )
        
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== SUMMARIZATION ENDPOINTS =====

@app.post(
    "/api/summarize",
    response_model=schemas.SummarizationResponse,
    tags=["Summarization"]
)
async def summarize_text(request: schemas.SummarizationRequest):
    """
    Создать краткое резюме текста.
    
    Методы:
    - extractive: выбирает важные предложения (быстро)
    - abstractive: генерирует новый текст (медленно, требует модель)
    - hybrid: комбинация (требует обе модели)
    """
    try:
        method = request.method
        
        if method == "extractive":
            summarizer = ml_models.get('summarizer_extractive')
            if not summarizer:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Extractive summarizer not loaded"
                )
            
            summary = summarizer.summarize(
                request.text,
                num_sentences=request.num_sentences or 3
            )
            
        elif method == "abstractive":
            summarizer = ml_models.get('summarizer_abstractive')
            if not summarizer:
                # Если abstractive модель не загружена, используем extractive
                logger.warning("Abstractive summarizer not loaded, using extractive")
                summarizer = ml_models.get('summarizer_extractive')
                summary = summarizer.summarize(request.text, num_sentences=3)
            else:
                summary = summarizer.summarize(
                    request.text,
                    max_length=request.max_length,
                    min_length=request.min_length
                )
        
        else:  # hybrid
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Hybrid summarization not yet implemented"
            )
        
        # Статистика
        orig_words = len(request.text.split())
        summ_words = len(summary.split())
        compression = summ_words / orig_words if orig_words > 0 else 0.0
        
        return schemas.SummarizationResponse(
            summary=summary,
            original_length=orig_words,
            summary_length=summ_words,
            compression_ratio=compression,
            method=method
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in summarize_text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== EMBEDDINGS ENDPOINTS =====

@app.post(
    "/api/create-embedding",
    response_model=schemas.EmbeddingResponse,
    tags=["Embeddings"]
)
async def create_embedding(request: schemas.TextRequest):
    """
    Создать векторное представление текста.
    
    Возвращает embedding (вектор чисел), который можно использовать для:
    - Semantic search
    - Similarity вычисления
    - Clustering
    """
    try:
        embeddings_model = ml_models.get('embeddings')
        if not embeddings_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embeddings model not loaded"
            )
        
        # Создаем embedding
        embedding = embeddings_model.encode(request.text)
        
        return schemas.EmbeddingResponse(
            embedding=embedding.tolist(),
            dimension=len(embedding)
        )
        
    except Exception as e:
        logger.error(f"Error in create_embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post(
    "/api/compute-similarity",
    response_model=schemas.SimilarityResponse,
    tags=["Embeddings"]
)
async def compute_similarity(request: schemas.SimilarityRequest):
    """
    Вычислить семантическую похожесть двух текстов.
    
    Возвращает score от 0.0 (не похожи) до 1.0 (идентичны).
    """
    try:
        embeddings_model = ml_models.get('embeddings')
        if not embeddings_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embeddings model not loaded"
            )
        
        # Вычисляем similarity
        similarity = embeddings_model.compute_similarity(
            request.text1,
            request.text2
        )
        
        return schemas.SimilarityResponse(similarity=similarity)
        
    except Exception as e:
        logger.error(f"Error in compute_similarity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post(
    "/api/semantic-search",
    response_model=schemas.SemanticSearchResponse,
    tags=["Embeddings"]
)
async def semantic_search(request: schemas.SemanticSearchRequest):
    """
    Semantic search по списку текстов.
    
    Находит тексты наиболее релевантные к query,
    даже если используются разные слова.
    """
    try:
        embeddings_model = ml_models.get('embeddings')
        if not embeddings_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embeddings model not loaded"
            )
        
        # Поиск
        results = embeddings_model.find_most_similar(
            request.query,
            request.candidates,
            top_k=request.top_k
        )
        
        # Форматируем
        search_results = [
            schemas.SearchResultResponse(
                index=idx,
                text=text,
                score=score
            )
            for idx, text, score in results
        ]
        
        return schemas.SemanticSearchResponse(
            results=search_results,
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Error in semantic_search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== COMPLETE PREDICTION =====

@app.post(
    "/api/predict-complete",
    response_model=schemas.CompletePredictionResponse,
    tags=["Complete"]
)
async def predict_complete(request: schemas.TextRequest):
    """
    Полная обработка текста всеми моделями сразу.
    
    Возвращает:
    - Classification (если модель обучена)
    - NER entities
    - Sentiment analysis
    - Summary
    - Embedding (опционально)
    
    Это основной endpoint для backend сервиса!
    """
    try:
        text = request.text
        
        # NER
        ner_model = ml_models.get('ner')
        if not ner_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NER model not loaded"
            )
        
        entities = ner_model.extract_entities(text)
        entity_counts = {}
        for ent in entities:
            ent_type = ent["type"]
            entity_counts[ent_type] = entity_counts.get(ent_type, 0) + 1
        
        ner_response = schemas.NERResponse(
            entities=[schemas.EntityResponse(**e) for e in entities],
            entity_counts=entity_counts
        )
        
        # Sentiment
        sentiment_model = ml_models.get('sentiment')
        if not sentiment_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sentiment model not loaded"
            )
        
        sentiment_result = sentiment_model.analyze(text)
        sentiment_response = schemas.SentimentResponse(**sentiment_result)
        
        # Summary
        summarizer = ml_models.get('summarizer_extractive')
        if not summarizer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Summarizer not loaded"
            )
        
        summary = summarizer.summarize(text, num_sentences=3)
        orig_words = len(text.split())
        summ_words = len(summary.split())
        
        summary_response = schemas.SummarizationResponse(
            summary=summary,
            original_length=orig_words,
            summary_length=summ_words,
            compression_ratio=summ_words / orig_words if orig_words > 0 else 0.0,
            method="extractive"
        )
        
        # Classification (если есть)
        # Пока заглушка, т.к. модель не обучена
        classification_response = schemas.ClassificationResponse(
            category="unknown",
            confidence=0.0,
            all_probabilities=None
        )
        
        return schemas.CompletePredictionResponse(
            classification=classification_response,
            ner=ner_response,
            sentiment=sentiment_response,
            summary=summary_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predict_complete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== ERROR HANDLERS =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик ошибок."""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )