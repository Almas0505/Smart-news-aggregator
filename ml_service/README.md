# 🤖 ML Service - Полная Документация

## 📋 Содержание

1. [Обзор](#обзор)
2. [Установка](#установка)
3. [Запуск](#запуск)
4. [API Endpoints](#api-endpoints)
5. [Модели ML](#модели-ml)
6. [Примеры использования](#примеры-использования)
7. [Архитектура](#архитектура)

---

## 🎯 Обзор

ML Service - микросервис для обработки текста новостей с помощью Machine Learning и AI.

### Возможности:

✅ **Text Classification** - категоризация новостей  
✅ **Named Entity Recognition** - извлечение имен, организаций, мест  
✅ **Sentiment Analysis** - определение эмоциональной окраски  
✅ **Text Summarization** - создание кратких резюме  
✅ **Text Embeddings** - векторные представления для поиска  
✅ **Semantic Search** - поиск по смыслу, а не по ключевым словам  

---

## 🚀 Установка

### 1. Требования

- Python 3.11+
- 4GB RAM минимум (8GB рекомендуется)
- (Опционально) GPU с CUDA для ускорения

### 2. Установка зависимостей

```bash
# Переходим в директорию
cd ml_service

# Создаем virtual environment
python -m venv venv

# Активируем
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Загружаем spaCy модель
python -m spacy download en_core_web_sm

# Загружаем NLTK данные
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Конфигурация

```bash
# Копируем example config
cp .env.example .env

# Редактируем настройки
nano .env
```

---

## ▶️ Запуск

### Development режим:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Production режим:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### С помощью Docker:

```bash
docker build -t ml-service .
docker run -p 8001:8001 ml-service
```

Сервис будет доступен на: `http://localhost:8001`

API документация: `http://localhost:8001/docs`

---

## 📡 API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": {
    "ner": true,
    "sentiment": true,
    "summarizer": true,
    "embeddings": true
  },
  "version": "1.0.0"
}
```

---

### Named Entity Recognition

```http
POST /api/extract-entities
```

**Request:**
```json
{
  "text": "Elon Musk announced that Tesla will open a factory in Berlin"
}
```

**Response:**
```json
{
  "entities": [
    {
      "text": "Elon Musk",
      "type": "PERSON",
      "start": 0,
      "end": 9,
      "confidence": 0.98
    },
    {
      "text": "Tesla",
      "type": "ORGANIZATION",
      "start": 27,
      "end": 32,
      "confidence": 0.95
    },
    {
      "text": "Berlin",
      "type": "LOCATION",
      "start": 61,
      "end": 67,
      "confidence": 0.92
    }
  ],
  "entity_counts": {
    "PERSON": 1,
    "ORGANIZATION": 1,
    "LOCATION": 1
  }
}
```

---

### Sentiment Analysis

```http
POST /api/analyze-sentiment
```

**Request:**
```json
{
  "text": "This is an absolutely amazing breakthrough in AI technology!"
}
```

**Response:**
```json
{
  "label": "positive",
  "score": 0.85,
  "confidence": 0.95
}
```

---

### Text Summarization

```http
POST /api/summarize
```

**Request:**
```json
{
  "text": "Long news article text here...",
  "method": "extractive",
  "num_sentences": 3,
  "max_length": 130,
  "min_length": 30
}
```

**Response:**
```json
{
  "summary": "Short summary of the article.",
  "original_length": 500,
  "summary_length": 50,
  "compression_ratio": 0.1,
  "method": "extractive"
}
```

---

### Create Embedding

```http
POST /api/create-embedding
```

**Request:**
```json
{
  "text": "AI revolution in healthcare"
}
```

**Response:**
```json
{
  "embedding": [0.234, -0.456, 0.789, ...],  // 384 numbers
  "dimension": 384
}
```

---

### Compute Similarity

```http
POST /api/compute-similarity
```

**Request:**
```json
{
  "text1": "Artificial intelligence in medicine",
  "text2": "AI transforms healthcare"
}
```

**Response:**
```json
{
  "similarity": 0.87
}
```

---

### Semantic Search

```http
POST /api/semantic-search
```

**Request:**
```json
{
  "query": "machine learning news",
  "candidates": [
    "Deep learning breakthrough",
    "Lakers win championship",
    "AI research advances"
  ],
  "top_k": 2
}
```

**Response:**
```json
{
  "query": "machine learning news",
  "results": [
    {
      "index": 2,
      "text": "AI research advances",
      "score": 0.92
    },
    {
      "index": 0,
      "text": "Deep learning breakthrough",
      "score": 0.88
    }
  ]
}
```

---

### Complete Prediction

```http
POST /api/predict-complete
```

**Request:**
```json
{
  "text": "Apple CEO Tim Cook announced new iPhone with revolutionary AI features in California."
}
```

**Response:**
```json
{
  "classification": {
    "category": "technology",
    "confidence": 0.95
  },
  "ner": {
    "entities": [...],
    "entity_counts": {...}
  },
  "sentiment": {
    "label": "positive",
    "score": 0.75,
    "confidence": 0.85
  },
  "summary": {
    "summary": "Apple announces new iPhone with AI.",
    "original_length": 15,
    "summary_length": 6,
    "compression_ratio": 0.4,
    "method": "extractive"
  }
}
```

---

## 🧠 Модели ML

### 1. Text Classification

**Реализации:**
- **TfidfClassifier** - TF-IDF + Logistic Regression
  - Скорость: ⚡⚡⚡ (миллисекунды)
  - Точность: ⭐⭐ (70-80%)
  - Использование: Прототипирование

- **BertClassifier** - BERT transformer
  - Скорость: ⚡ (секунды)
  - Точность: ⭐⭐⭐⭐⭐ (90-95%)
  - Использование: Production (если есть GPU)

**Файл:** `app/models/classifier.py`

---

### 2. Named Entity Recognition

**Библиотека:** spaCy

**Модели:**
- `en_core_web_sm` - маленькая (12MB, быстрая) ✅ default
- `en_core_web_md` - средняя (40MB, точнее)
- `en_core_web_lg` - большая (560MB, самая точная)

**Извлекаемые сущности:**
- PERSON - люди
- ORGANIZATION - организации
- LOCATION - места
- DATE - даты
- MONEY - деньги
- PRODUCT - продукты
- EVENT - события

**Файл:** `app/models/ner_model.py`

---

### 3. Sentiment Analysis

**Реализации:**

- **SimpleSentimentAnalyzer** - TextBlob
  - Скорость: ⚡⚡⚡ (мгновенно)
  - Точность: ⭐⭐ (60-70%)
  - Использование: Baseline

- **MLSentimentAnalyzer** - TF-IDF + LogReg
  - Скорость: ⚡⚡⚡ (миллисекунды)
  - Точность: ⭐⭐⭐ (75-85%)
  - Требует: Обучение на данных

- **TransformerSentimentAnalyzer** - BERT
  - Скорость: ⚡ (секунды)
  - Точность: ⭐⭐⭐⭐⭐ (90-95%)
  - Использование: Production ✅ default

**Файл:** `app/models/sentiment.py`

---

### 4. Text Summarization

**Реализации:**

- **ExtractiveSummarizer** - TextRank algorithm
  - Скорость: ⚡⚡⚡ (секунды)
  - Качество: ⭐⭐⭐ (хорошее)
  - Метод: Выбирает важные предложения
  - Использование: Production ✅ default

- **AbstractiveSummarizer** - BART/Pegasus
  - Скорость: ⚡ (5-10 секунд)
  - Качество: ⭐⭐⭐⭐⭐ (отличное)
  - Метод: Генерирует новый текст
  - Требует: GPU для хорошей скорости

- **HybridSummarizer** - Комбинация
  - Скорость: ⚡⚡ (средняя)
  - Качество: ⭐⭐⭐⭐ (очень хорошее)

**Файл:** `app/models/summarizer.py`

---

### 5. Text Embeddings

**Модель:** Sentence Transformers

**Используемая модель:**
- `all-MiniLM-L6-v2` (default)
  - Размер: 80MB
  - Скорость: быстрая
  - Размерность: 384
  - Качество: отличное

**Возможности:**
- Создание embeddings
- Вычисление similarity
- Semantic search
- Clustering
- Duplicate detection

**Файл:** `app/models/embeddings.py`

---

## 💡 Примеры использования

### Python Client

```python
import requests

BASE_URL = "http://localhost:8001"

# NER
response = requests.post(
    f"{BASE_URL}/api/extract-entities",
    json={"text": "Apple CEO Tim Cook in California"}
)
print(response.json())

# Sentiment
response = requests.post(
    f"{BASE_URL}/api/analyze-sentiment",
    json={"text": "This is amazing!"}
)
print(response.json())

# Summary
response = requests.post(
    f"{BASE_URL}/api/summarize",
    json={
        "text": "Long article...",
        "method": "extractive",
        "num_sentences": 3
    }
)
print(response.json())

# Semantic Search
response = requests.post(
    f"{BASE_URL}/api/semantic-search",
    json={
        "query": "AI news",
        "candidates": ["ML article", "Sports news", "Tech update"],
        "top_k": 2
    }
)
print(response.json())
```

### cURL

```bash
# Health check
curl http://localhost:8001/health

# NER
curl -X POST http://localhost:8001/api/extract-entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Elon Musk in Tesla factory"}'

# Sentiment
curl -X POST http://localhost:8001/api/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing breakthrough!"}'
```

---

## 🏗️ Архитектура

```
ml_service/
├── app/
│   ├── models/           # ML модели
│   │   ├── classifier.py      # Text classification
│   │   ├── ner_model.py       # Named Entity Recognition
│   │   ├── sentiment.py       # Sentiment analysis
│   │   ├── summarizer.py      # Text summarization
│   │   └── embeddings.py      # Text embeddings
│   │
│   ├── preprocessing/    # Text preprocessing
│   │   └── text_cleaner.py
│   │
│   ├── api/             # API endpoints (не используется в текущей версии)
│   ├── config.py        # Конфигурация
│   ├── schemas.py       # Pydantic schemas
│   └── main.py          # FastAPI app
│
├── saved_models/        # Сохраненные модели
├── requirements.txt     # Python зависимости
├── .env.example        # Environment variables template
└── README.md           # Эта документация
```

---

## 📊 Performance

### Benchmark (CPU - Intel i7, 16GB RAM):

| Endpoint | Avg Time | Max Time |
|----------|----------|----------|
| NER | 50ms | 100ms |
| Sentiment (Simple) | 5ms | 10ms |
| Sentiment (Transformer) | 500ms | 1s |
| Summary (Extractive) | 200ms | 500ms |
| Summary (Abstractive) | 5s | 10s |
| Embedding | 100ms | 200ms |
| Semantic Search (100 docs) | 300ms | 600ms |

### GPU Acceleration:

С GPU (NVIDIA RTX 3060):
- Transformer Sentiment: 50ms
- Abstractive Summary: 1-2s
- BERT Classification: 30ms

---

## 🔧 Configuration

Все настройки в `config.py` и `.env`.

### Ключевые параметры:

```python
# Модели
SPACY_MODEL = "en_core_web_sm"
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Performance
MAX_LENGTH = 512
BATCH_SIZE = 32
USE_GPU = False
WORKERS = 4
```

---

## 🐛 Troubleshooting

### Модель не загружается

```bash
# Убедитесь что spaCy модель установлена
python -m spacy download en_core_web_sm

# Убедитесь что NLTK данные загружены
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Out of Memory

- Уменьшите `BATCH_SIZE`
- Используйте меньшие модели (`en_core_web_sm` вместо `lg`)
- Отключите неиспользуемые модели

### Медленная работа

- Включите GPU (`USE_GPU=True`)
- Используйте extractive вместо abstractive summarization
- Увеличьте количество workers

---

## 📝 Лицензия

MIT License

---

## 👨‍💻 Автор

Smart News Aggregator Team

Создано в рамках обучения ML/AI технологиям.