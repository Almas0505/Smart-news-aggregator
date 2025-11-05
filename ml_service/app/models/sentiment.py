"""
Sentiment Analysis Model

====== ЧТО ТАКОЕ SENTIMENT ANALYSIS? ======

Sentiment Analysis (Анализ тональности) - определение эмоциональной окраски текста.

Задача: Текст → Эмоция (Positive/Negative/Neutral) + Уверенность

====== ЗАЧЕМ ЭТО НУЖНО? ======

1. Фильтрация новостей: показывать позитивные/негативные отдельно
2. Мониторинг репутации: "сколько негатива о компании?"
3. Тренды: "настроения по поводу выборов изменились"
4. Рекомендации: "пользователь предпочитает позитивные новости"

====== ПРИМЕРЫ ======

Positive (0.95):
"Amazing breakthrough! Scientists cure cancer in mice."

Negative (0.92):
"Terrible disaster. Hundreds killed in earthquake."

Neutral (0.88):
"The meeting was scheduled for 3 PM on Tuesday."

====== ТРИ ПОДХОДА ======

1. Lexicon-based (TextBlob) - самый простой
   + Быстрый
   - Не очень точный
   
2. Classical ML (Logistic Regression) - средний
   + Баланс скорости и точности
   - Нужны размеченные данные
   
3. Transformers (BERT) - самый точный
   + Очень точный (понимает контекст)
   - Медленный

Мы реализуем ВСЕ ТРИ!
"""

import numpy as np
from typing import Dict, List, Tuple, Literal
from textblob import TextBlob
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

from app.config import settings
from app.preprocessing.text_cleaner import preprocess_for_bert, preprocess_for_tfidf


# ===== КОНСТАНТЫ =====

# Возможные sentiment labels
SentimentLabel = Literal["positive", "negative", "neutral"]


# ===== КЛАСС 1: ПРОСТОЙ SENTIMENT (TextBlob) =====

class SimpleSentimentAnalyzer:
    """Простой анализ тональности через TextBlob.
    
    ====== КАК РАБОТАЕТ TEXTBLOB? ======
    
    TextBlob использует готовый словарь слов с оценками:
    - "amazing" = +0.8
    - "terrible" = -0.9
    - "good" = +0.7
    - "bad" = -0.7
    
    Алгоритм:
    1. Разбивает текст на слова
    2. Находит каждое слово в словаре
    3. Считает среднюю оценку
    
    Плюсы:
    + Не требует обучения
    + Очень быстрый
    + Простой в использовании
    
    Минусы:
    - Не понимает контекст ("not good" = good?)
    - Ограниченный словарь
    - Точность ~60-70%
    """
    
    def __init__(self):
        """Инициализация (ничего загружать не надо!)."""
        pass
    
    def analyze(self, text: str) -> Dict[str, any]:
        """Анализировать тональность текста.
        
        Args:
            text: Исходный текст
        
        Returns:
            {
                "label": "positive" | "negative" | "neutral",
                "score": float,  # -1.0 (очень негативный) до +1.0 (очень позитивный)
                "confidence": float  # 0.0 до 1.0
            }
            
        Example:
            >>> analyzer = SimpleSentimentAnalyzer()
            >>> result = analyzer.analyze("This is amazing!")
            >>> print(result)
            {
                "label": "positive",
                "score": 0.75,
                "confidence": 0.75
            }
        """
        if not text:
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0
            }
        
        # TextBlob автоматически анализирует
        blob = TextBlob(text)
        
        # Polarity: -1.0 (негативный) до +1.0 (позитивный)
        polarity = blob.sentiment.polarity
        
        # Subjectivity: 0.0 (объективный) до 1.0 (субъективный)
        subjectivity = blob.sentiment.subjectivity
        
        # Определяем label на основе polarity
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        # Confidence = насколько уверены (используем abs(polarity) и subjectivity)
        confidence = min(abs(polarity) + subjectivity / 2, 1.0)
        
        return {
            "label": label,
            "score": polarity,
            "confidence": confidence,
            "subjectivity": subjectivity
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """Анализ множества текстов.
        
        Args:
            texts: Список текстов
        
        Returns:
            Список результатов
        """
        return [self.analyze(text) for text in texts]


# ===== КЛАСС 2: ML-BASED SENTIMENT =====

class MLSentimentAnalyzer:
    """ML-based sentiment analyzer (TF-IDF + Logistic Regression).
    
    ====== КАК РАБОТАЕТ? ======
    
    Похоже на Text Classifier, но для sentiment:
    
    1. TF-IDF векторизация текста
    2. Logistic Regression классифицирует: positive/negative/neutral
    
    Требует обучения на размеченных данных!
    
    Плюсы:
    + Точнее TextBlob (~75-85%)
    + Быстрый
    + Можно обучить на своих данных
    
    Минусы:
    - Требует датасет
    - Не понимает сложный контекст
    """
    
    def __init__(self):
        """Инициализация."""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2
        )
        
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            multi_class='multinomial'
        )
        
        self.label_mapping = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }
        
        self.is_trained = False
    
    def train(
        self,
        texts: List[str],
        labels: List[str]  # ["positive", "negative", "neutral"]
    ) -> Dict[str, float]:
        """Обучить модель.
        
        Args:
            texts: Тексты
            labels: Метки ("positive", "negative", "neutral")
        
        Returns:
            Метрики обучения
        """
        # Preprocessing
        cleaned_texts = [preprocess_for_tfidf(text) for text in texts]
        
        # Конвертируем labels в числа
        label_to_num = {"negative": 0, "neutral": 1, "positive": 2}
        numeric_labels = [label_to_num[label] for label in labels]
        
        # TF-IDF
        X = self.vectorizer.fit_transform(cleaned_texts)
        
        # Обучение
        self.model.fit(X, numeric_labels)
        
        self.is_trained = True
        
        # Оценка
        train_accuracy = self.model.score(X, numeric_labels)
        
        return {"accuracy": train_accuracy}
    
    def analyze(self, text: str) -> Dict[str, any]:
        """Анализ тональности.
        
        Args:
            text: Текст
        
        Returns:
            Результат анализа
        """
        if not self.is_trained:
            raise ValueError("Model not trained! Call train() first.")
        
        # Preprocessing
        cleaned_text = preprocess_for_tfidf(text)
        
        # TF-IDF
        X = self.vectorizer.transform([cleaned_text])
        
        # Prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        label = self.label_mapping[prediction]
        confidence = probabilities[prediction]
        
        # Score: -1.0 (negative) to +1.0 (positive)
        score = probabilities[2] - probabilities[0]  # positive - negative
        
        return {
            "label": label,
            "score": score,
            "confidence": confidence
        }
    
    def save(self, path: str):
        """Сохранить модель."""
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'label_mapping': self.label_mapping,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, path)
    
    def load(self, path: str):
        """Загрузить модель."""
        model_data = joblib.load(path)
        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.label_mapping = model_data['label_mapping']
        self.is_trained = model_data['is_trained']


# ===== КЛАСС 3: TRANSFORMER-BASED SENTIMENT =====

class TransformerSentimentAnalyzer:
    """SOTA sentiment analyzer на основе BERT/RoBERTa.
    
    ====== КАК РАБОТАЕТ? ======
    
    Использует pretrained transformer модели от Hugging Face:
    - distilbert-base-uncased-finetuned-sst-2-english (наш default)
    - roberta-base-openai-detector
    - cardiffnlp/twitter-roberta-base-sentiment
    
    Эти модели уже обучены на миллионах примеров!
    
    Преимущества:
    + Очень высокая точность (90-95%)
    + Понимает контекст
    + Понимает сарказм (частично)
    + Готов к использованию (no training needed!)
    
    Недостатки:
    - Медленный (1-2 секунды на текст)
    - Требует много памяти
    - Нужен GPU для хорошей скорости
    """
    
    def __init__(self, model_name: str = settings.SENTIMENT_MODEL):
        """Инициализация transformer модели.
        
        Args:
            model_name: Название Hugging Face модели
        """
        self.model_name = model_name
        
        print(f"📦 Loading transformer model: {model_name}")
        
        # Используем pipeline - простейший способ
        # Pipeline автоматически:
        # 1. Загружает tokenizer
        # 2. Загружает модель
        # 3. Настраивает preprocessing
        # 4. Настраивает postprocessing
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=-1  # -1 = CPU, 0 = GPU
        )
        
        print(f"✅ Model loaded successfully")
        
        # Маппинг: некоторые модели возвращают LABEL_0, LABEL_1
        # Нужно конвертировать в понятные метки
        self.label_mapping = {
            "NEGATIVE": "negative",
            "POSITIVE": "positive",
            "NEUTRAL": "neutral",
            "LABEL_0": "negative",
            "LABEL_1": "neutral",
            "LABEL_2": "positive"
        }
    
    def analyze(self, text: str, max_length: int = 512) -> Dict[str, any]:
        """Анализ тональности через transformer.
        
        Args:
            text: Текст
            max_length: Максимальная длина (BERT лимит = 512)
        
        Returns:
            Результат анализа
            
        Example:
            >>> analyzer = TransformerSentimentAnalyzer()
            >>> result = analyzer.analyze("This movie is absolutely amazing!")
            >>> print(result)
            {
                "label": "positive",
                "score": 0.9998,
                "confidence": 0.9998
            }
        """
        if not text:
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0
            }
        
        # Preprocessing (минимальный для BERT)
        cleaned_text = preprocess_for_bert(text)
        
        # Обрезаем если слишком длинный
        # BERT models имеют лимит 512 токенов
        if len(cleaned_text.split()) > max_length:
            cleaned_text = ' '.join(cleaned_text.split()[:max_length])
        
        # Prediction через pipeline
        result = self.pipeline(cleaned_text)[0]
        
        # Конвертируем label
        raw_label = result['label'].upper()
        label = self.label_mapping.get(raw_label, raw_label.lower())
        
        # Score от модели (уверенность)
        confidence = result['score']
        
        # Нормализуем score к -1.0 (negative) ... +1.0 (positive)
        if label == "positive":
            score = confidence
        elif label == "negative":
            score = -confidence
        else:  # neutral
            score = 0.0
        
        return {
            "label": label,
            "score": score,
            "confidence": confidence
        }
    
    def analyze_batch(
        self,
        texts: List[str],
        batch_size: int = 8
    ) -> List[Dict[str, any]]:
        """Batch анализ (НАМНОГО быстрее для множества текстов!).
        
        Args:
            texts: Список текстов
            batch_size: Размер батча
        
        Returns:
            Список результатов
        """
        # Preprocessing
        cleaned_texts = [preprocess_for_bert(text) for text in texts]
        
        # Batch prediction
        results = self.pipeline(cleaned_texts, batch_size=batch_size)
        
        # Форматируем результаты
        formatted_results = []
        for result in results:
            raw_label = result['label'].upper()
            label = self.label_mapping.get(raw_label, raw_label.lower())
            confidence = result['score']
            
            if label == "positive":
                score = confidence
            elif label == "negative":
                score = -confidence
            else:
                score = 0.0
            
            formatted_results.append({
                "label": label,
                "score": score,
                "confidence": confidence
            })
        
        return formatted_results


# ===== ENSEMBLE ANALYZER =====

class EnsembleSentimentAnalyzer:
    """Комбинированный анализатор - использует несколько моделей.
    
    Идея: Комбинируем результаты разных моделей для лучшей точности.
    
    Стратегии:
    1. Voting: большинство голосов
    2. Averaging: среднее score
    3. Weighted: взвешенное среднее (доверяем BERT больше)
    """
    
    def __init__(self, use_transformer: bool = True):
        """Инициализация ансамбля.
        
        Args:
            use_transformer: Использовать BERT (медленно, но точно)
        """
        self.simple = SimpleSentimentAnalyzer()
        self.use_transformer = use_transformer
        
        if use_transformer:
            self.transformer = TransformerSentimentAnalyzer()
    
    def analyze(self, text: str, strategy: str = "weighted") -> Dict[str, any]:
        """Анализ через ансамбль моделей.
        
        Args:
            text: Текст
            strategy: "voting", "averaging", "weighted"
        
        Returns:
            Комбинированный результат
        """
        results = []
        
        # Simple analyzer (быстрый)
        simple_result = self.simple.analyze(text)
        results.append(simple_result)
        
        # Transformer analyzer (медленный, точный)
        if self.use_transformer:
            transformer_result = self.transformer.analyze(text)
            results.append(transformer_result)
        
        # Комбинируем результаты
        if strategy == "voting":
            # Большинство голосов
            labels = [r['label'] for r in results]
            label = max(set(labels), key=labels.count)
            
        elif strategy == "averaging":
            # Среднее score
            avg_score = np.mean([r['score'] for r in results])
            label = "positive" if avg_score > 0.1 else ("negative" if avg_score < -0.1 else "neutral")
            
        elif strategy == "weighted":
            # Взвешенное (больший вес BERT)
            if self.use_transformer:
                weights = [0.3, 0.7]  # 30% simple, 70% transformer
            else:
                weights = [1.0]
            
            weighted_score = sum(r['score'] * w for r, w in zip(results, weights))
            label = "positive" if weighted_score > 0.1 else ("negative" if weighted_score < -0.1 else "neutral")
        
        # Средняя уверенность
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        return {
            "label": label,
            "score": weighted_score if strategy == "weighted" else avg_score,
            "confidence": avg_confidence,
            "individual_results": results
        }


# ===== USAGE EXAMPLES =====
"""
# ===== 1. Simple Sentiment (TextBlob) =====

simple = SimpleSentimentAnalyzer()

text = "This is an absolutely amazing product!"
result = simple.analyze(text)
print(f"{result['label']}: {result['score']:.2f} (confidence: {result['confidence']:.2f})")
# Output: positive: 0.75 (confidence: 0.75)


# ===== 2. ML Sentiment (требует обучения) =====

ml = MLSentimentAnalyzer()

# Обучение
texts = [
    "I love this!",
    "This is terrible",
    "The meeting is at 3pm"
]
labels = ["positive", "negative", "neutral"]

ml.train(texts, labels)

# Использование
result = ml.analyze("This is great!")
print(result['label'])  # positive


# ===== 3. Transformer Sentiment (SOTA) =====

transformer = TransformerSentimentAnalyzer()

text = "The movie was phenomenal! Best I've seen in years."
result = transformer.analyze(text)
print(f"{result['label']}: {result['confidence']:.2%}")
# Output: positive: 99.98%

# Batch processing
texts = [
    "Amazing product!",
    "Worst experience ever",
    "The delivery was on time"
]
results = transformer.analyze_batch(texts)
for text, res in zip(texts, results):
    print(f"{text:30} → {res['label']:10} ({res['confidence']:.2%})")


# ===== 4. Ensemble (комбинированный) =====

ensemble = EnsembleSentimentAnalyzer(use_transformer=True)

text = "Not bad at all, quite good actually!"
result = ensemble.analyze(text, strategy="weighted")
print(f"{result['label']}: {result['score']:.2f}")
print("Individual results:")
for r in result['individual_results']:
    print(f"  - {r['label']}: {r['score']:.2f}")


# ===== Выбор модели =====

# Для БЫСТРОГО прототипа:
analyzer = SimpleSentimentAnalyzer()

# Для PRODUCTION с балансом:
analyzer = TransformerSentimentAnalyzer()

# Для МАКСИМАЛЬНОЙ точности:
analyzer = EnsembleSentimentAnalyzer(use_transformer=True)
"""