"""
Processing Tasks

Задачи обработки новостей через ML Service.

====== PIPELINE ======

1. Получить статью
2. Отправить в ML Service для:
   - Classification (категория)
   - NER (извлечение сущностей)
   - Sentiment analysis
   - Summarization
3. Обогатить статью ML данными
4. Вернуть обработанную статью
"""

from typing import Dict, List, Optional
import logging

from app.celery_app import app
from app.config import settings
import httpx


logger = logging.getLogger(__name__)


# ===== ML PROCESSING TASKS =====

@app.task(
    name='app.tasks.processing_tasks.process_article',
    bind=True,
    max_retries=3
)
def process_article(self, article: Dict) -> Dict:
    """Обработать статью через ML Service.
    
    Args:
        article: Словарь со статьей
    
    Returns:
        Обогащенная статья с ML данными
        
    Example:
        Input:
        {
            'title': 'Apple releases new iPhone',
            'content': '...',
        }
        
        Output:
        {
            'title': 'Apple releases new iPhone',
            'content': '...',
            'category': 'technology',
            'sentiment': 'positive',
            'entities': ['Apple', 'iPhone'],
            'summary': 'Short summary...'
        }
    """
    if not settings.SEND_TO_ML_SERVICE:
        logger.debug("ML processing disabled")
        return article
    
    logger.info(f"Processing article: {article.get('title', 'Unknown')[:50]}...")
    
    try:
        # Отправляем в ML Service
        ml_data = send_to_ml_service(article)
        
        # Обогащаем статью
        article.update({
            'category': ml_data.get('category'),
            'sentiment': ml_data.get('sentiment'),
            'entities': ml_data.get('entities', []),
            'summary': ml_data.get('summary', article.get('summary')),
            'ml_processed': True
        })
        
        logger.info(f"✅ ML processing complete: {ml_data.get('category')}")
        
        return article
        
    except Exception as e:
        logger.error(f"ML processing error: {e}")
        # Возвращаем без ML данных
        article['ml_processed'] = False
        return article


@app.task(
    name='app.tasks.processing_tasks.process_articles_batch',
    bind=True
)
def process_articles_batch(self, articles: List[Dict]) -> List[Dict]:
    """Обработать батч статей.
    
    Args:
        articles: Список статей
    
    Returns:
        Обработанные статьи
    """
    logger.info(f"Processing batch of {len(articles)} articles...")
    
    processed = []
    
    for article in articles:
        try:
            processed_article = process_article(article)
            processed.append(processed_article)
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            # Добавляем без обработки
            processed.append(article)
    
    logger.info(f"✅ Processed {len(processed)} articles")
    
    return processed


# ===== ML SERVICE INTEGRATION =====

def send_to_ml_service(article: Dict) -> Dict:
    """Отправить статью в ML Service для обработки.
    
    Args:
        article: Статья
    
    Returns:
        ML данные
        
    Raises:
        httpx.HTTPError: При ошибке запроса
    """
    ml_url = f"{settings.ML_SERVICE_URL}/api/predict-complete"
    
    # Подготовка payload
    payload = {
        'text': article.get('content', ''),
        'title': article.get('title', '')
    }
    
    logger.debug(f"Sending to ML Service: {ml_url}")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                ml_url,
                json=payload
            )
            
            response.raise_for_status()
            
            ml_data = response.json()
            
            return ml_data
            
    except httpx.HTTPError as e:
        logger.error(f"ML Service error: {e}")
        raise


# ===== CATEGORY CLASSIFICATION =====

@app.task(
    name='app.tasks.processing_tasks.classify_article',
    bind=True
)
def classify_article(self, text: str) -> Dict:
    """Классифицировать статью (определить категорию).
    
    Args:
        text: Текст статьи
    
    Returns:
        {'category': 'technology', 'confidence': 0.95}
    """
    ml_url = f"{settings.ML_SERVICE_URL}/api/classify"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                ml_url,
                json={'text': text}
            )
            
            response.raise_for_status()
            
            return response.json()
            
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return {'category': 'general', 'confidence': 0.0}


# ===== SENTIMENT ANALYSIS =====

@app.task(
    name='app.tasks.processing_tasks.analyze_sentiment',
    bind=True
)
def analyze_sentiment(self, text: str) -> Dict:
    """Анализ тональности статьи.
    
    Args:
        text: Текст статьи
    
    Returns:
        {'sentiment': 'positive', 'score': 0.85}
    """
    ml_url = f"{settings.ML_SERVICE_URL}/api/analyze-sentiment"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                ml_url,
                json={'text': text}
            )
            
            response.raise_for_status()
            
            return response.json()
            
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return {'sentiment': 'neutral', 'score': 0.0}


# ===== NER (Named Entity Recognition) =====

@app.task(
    name='app.tasks.processing_tasks.extract_entities',
    bind=True
)
def extract_entities(self, text: str) -> List[Dict]:
    """Извлечь именованные сущности.
    
    Args:
        text: Текст статьи
    
    Returns:
        [
            {'text': 'Apple', 'type': 'ORG'},
            {'text': 'Tim Cook', 'type': 'PERSON'},
        ]
    """
    ml_url = f"{settings.ML_SERVICE_URL}/api/extract-entities"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                ml_url,
                json={'text': text}
            )
            
            response.raise_for_status()
            
            result = response.json()
            return result.get('entities', [])
            
    except Exception as e:
        logger.error(f"NER error: {e}")
        return []


# ===== SUMMARIZATION =====

@app.task(
    name='app.tasks.processing_tasks.generate_summary',
    bind=True
)
def generate_summary(self, text: str, max_length: int = 3) -> str:
    """Сгенерировать краткое описание.
    
    Args:
        text: Текст статьи
        max_length: Максимум предложений
    
    Returns:
        Краткое описание
    """
    ml_url = f"{settings.ML_SERVICE_URL}/api/summarize"
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                ml_url,
                json={
                    'text': text,
                    'num_sentences': max_length
                }
            )
            
            response.raise_for_status()
            
            result = response.json()
            return result.get('summary', '')
            
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        # Fallback - первые N предложений
        from app.utils.text_utils import extract_sentences
        return extract_sentences(text, max_length)


# ===== USAGE EXAMPLES =====
"""
# ===== Process Article =====

from app.tasks.processing_tasks import process_article

article = {
    'title': 'Apple announces new AI features',
    'content': 'Apple Inc. today announced...',
    'url': 'https://example.com/article'
}

# Async processing
task = process_article.delay(article)
processed = task.get()

print(processed)
# {
#     'title': 'Apple announces new AI features',
#     'content': '...',
#     'category': 'technology',
#     'sentiment': 'positive',
#     'entities': [
#         {'text': 'Apple', 'type': 'ORG'},
#         {'text': 'AI', 'type': 'PRODUCT'}
#     ],
#     'summary': 'Apple introduces new AI...',
#     'ml_processed': True
# }


# ===== Batch Processing =====

from app.tasks.processing_tasks import process_articles_batch

articles = [article1, article2, article3]

task = process_articles_batch.delay(articles)
processed_articles = task.get()


# ===== Individual ML Tasks =====

from app.tasks.processing_tasks import (
    classify_article,
    analyze_sentiment,
    extract_entities,
    generate_summary
)

text = "Apple releases new iPhone with advanced AI capabilities..."

# Classification
category_task = classify_article.delay(text)
category_data = category_task.get()
print(f"Category: {category_data['category']}")

# Sentiment
sentiment_task = analyze_sentiment.delay(text)
sentiment_data = sentiment_task.get()
print(f"Sentiment: {sentiment_data['sentiment']}")

# Entities
entities_task = extract_entities.delay(text)
entities = entities_task.get()
for entity in entities:
    print(f"{entity['text']} ({entity['type']})")

# Summary
summary_task = generate_summary.delay(text, max_length=2)
summary = summary_task.get()
print(f"Summary: {summary}")


# ===== Chaining Tasks =====

from celery import chain
from app.tasks.scraping_tasks import scrape_source
from app.tasks.processing_tasks import process_articles_batch

# Scrape → Process → Send
workflow = chain(
    scrape_source.s('bbc'),
    process_articles_batch.s(),
)

result = workflow.apply_async()
"""