"""
Text Classification Model

Этот модуль реализует классификацию текста новостей по категориям.

====== ЧТО ТАКОЕ КЛАССИФИКАЦИЯ? ======

Задача: Дан текст новости → определить категорию (Technology, Sports, и т.д.)

Пример:
Input:  "Apple releases new iPhone with AI features"
Output: "Technology" (confidence: 95%)

====== КАК ЭТО РАБОТАЕТ? ======

1. TRAINING (Обучение):
   - Берем размеченные данные: [текст, категория]
   - "Apple releases iPhone" → Technology
   - "Lakers win championship" → Sports
   
   - Модель учится: какие слова → какая категория
   - "iPhone", "AI", "tech" → Technology
   - "win", "championship", "Lakers" → Sports

2. PREDICTION (Предсказание):
   - Новый текст → модель → категория + уверенность
   
====== ДВА ПОДХОДА ======

Подход 1: TF-IDF + Logistic Regression (простой, быстрый)
Подход 2: BERT transformer (точный, медленный)

Мы реализуем ОБА!
"""

import os
import joblib
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

from app.config import settings
from app.preprocessing.text_cleaner import preprocess_for_tfidf, preprocess_for_bert


# ===== КЛАСС 1: TF-IDF CLASSIFIER (Простой) =====

class TfidfClassifier:
    """Классификатор на основе TF-IDF + Logistic Regression.
    
    ====== ЧТО ТАКОЕ TF-IDF? ======
    
    TF-IDF = Term Frequency - Inverse Document Frequency
    
    Идея: Важность слова = как часто встречается В ЭТОМ документе /
                           как часто встречается ВО ВСЕХ документах
    
    Пример:
    - Слово "the" встречается везде → низкая важность (0.1)
    - Слово "iPhone" встречается редко → высокая важность (0.9)
    
    TF-IDF преобразует текст в числовой вектор:
    "Apple releases iPhone" → [0.0, 0.3, 0.0, 0.9, 0.2, ...]
                               каждое число = важность слова
    
    ====== ЧТО ТАКОЕ LOGISTIC REGRESSION? ======
    
    Простой ML алгоритм для классификации.
    Учится: вектор чисел → категория
    
    [0.0, 0.3, 0.0, 0.9, ...] → "Technology"
    
    Преимущества:
    + Быстрый (миллисекунды)
    + Простой в понимании
    + Мало требует данных
    
    Недостатки:
    - Не понимает контекст ("Apple pie" vs "Apple iPhone")
    - Игнорирует порядок слов
    """
    
    def __init__(self):
        """Инициализация классификатора."""
        
        # TfidfVectorizer - преобразует текст в числа
        self.vectorizer = TfidfVectorizer(
            max_features=5000,    # Используем топ-5000 самых важных слов
            ngram_range=(1, 2),   # Учитываем 1-граммы и 2-граммы
            # 1-грамма: "iPhone"
            # 2-грамма: "new iPhone", "releases iPhone"
            min_df=2,             # Слово должно встречаться минимум в 2 документах
            max_df=0.8            # Игнорируем слова, которые есть в >80% документов
        )
        
        # LogisticRegression - классификатор
        self.model = LogisticRegression(
            max_iter=1000,        # Максимум итераций обучения
            random_state=42,      # Для воспроизводимости результатов
            multi_class='multinomial',  # Для нескольких классов
            solver='lbfgs'        # Алгоритм оптимизации
        )
        
        # Маппинг: индекс → категория
        self.label_to_category = {}
        self.category_to_label = {}
    
    def train(
        self,
        texts: List[str],
        labels: List[str],
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """Обучить модель.
        
        ====== ПРОЦЕСС ОБУЧЕНИЯ ======
        
        1. Разделяем данные на train/test (80%/20%)
        2. Preprocessing текстов
        3. TF-IDF преобразование (текст → числа)
        4. Обучение Logistic Regression
        5. Оценка на тестовой выборке
        
        Args:
            texts: Список текстов новостей
            labels: Список категорий (той же длины)
            test_size: Процент данных для тестирования
            
        Returns:
            Метрики: accuracy, precision, recall, f1
            
        Example:
            texts = [
                "Apple releases new iPhone",
                "Lakers win championship"
            ]
            labels = ["technology", "sports"]
            
            classifier.train(texts, labels)
        """
        print(f"📚 Обучаем модель на {len(texts)} примерах...")
        
        # Шаг 1: Preprocessing
        print("🧹 Preprocessing текстов...")
        cleaned_texts = [preprocess_for_tfidf(text) for text in texts]
        
        # Шаг 2: Создаем маппинг категорий
        unique_labels = sorted(set(labels))
        self.label_to_category = {i: label for i, label in enumerate(unique_labels)}
        self.category_to_label = {label: i for i, label in enumerate(unique_labels)}
        
        # Конвертируем категории в числа
        numeric_labels = [self.category_to_label[label] for label in labels]
        
        # Шаг 3: Разделяем на train/test
        X_train, X_test, y_train, y_test = train_test_split(
            cleaned_texts,
            numeric_labels,
            test_size=test_size,
            random_state=42,
            stratify=numeric_labels  # Сохраняем пропорции классов
        )
        
        print(f"📊 Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Шаг 4: TF-IDF vectorization
        print("🔢 TF-IDF vectorization...")
        # Обучаем vectorizer на train данных
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        # Применяем к test данным (БЕЗ переобучения!)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        print(f"✅ Создано {X_train_tfidf.shape[1]} features")
        
        # Шаг 5: Обучение модели
        print("🎓 Обучаем Logistic Regression...")
        self.model.fit(X_train_tfidf, y_train)
        
        # Шаг 6: Оценка
        print("📈 Оценка на test set...")
        y_pred = self.model.predict(X_test_tfidf)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"✅ Accuracy: {accuracy:.2%}")
        
        # Детальный отчет
        report = classification_report(
            y_test,
            y_pred,
            target_names=[self.label_to_category[i] for i in range(len(unique_labels))],
            output_dict=True
        )
        
        return {
            'accuracy': accuracy,
            'report': report
        }
    
    def predict(self, text: str) -> Tuple[str, float]:
        """Предсказать категорию для текста.
        
        ====== ПРОЦЕСС ПРЕДСКАЗАНИЯ ======
        
        1. Preprocessing текста
        2. TF-IDF преобразование
        3. Предсказание модели
        4. Получение вероятностей
        
        Args:
            text: Текст новости
            
        Returns:
            (категория, уверенность)
            
        Example:
            >>> text = "Apple releases new iPhone"
            >>> category, confidence = classifier.predict(text)
            >>> print(f"{category}: {confidence:.2%}")
            "Technology: 95%"
        """
        # Шаг 1: Preprocessing
        cleaned_text = preprocess_for_tfidf(text)
        
        # Шаг 2: TF-IDF
        text_tfidf = self.vectorizer.transform([cleaned_text])
        
        # Шаг 3: Предсказание
        prediction = self.model.predict(text_tfidf)[0]
        
        # Шаг 4: Вероятности (уверенность)
        probabilities = self.model.predict_proba(text_tfidf)[0]
        confidence = probabilities[prediction]
        
        # Шаг 5: Конвертируем индекс в категорию
        category = self.label_to_category[prediction]
        
        return category, confidence
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """Предсказать категории для множества текстов.
        
        Быстрее, чем вызывать predict() для каждого текста.
        
        Args:
            texts: Список текстов
            
        Returns:
            Список (категория, уверенность)
        """
        # Preprocessing всех текстов
        cleaned_texts = [preprocess_for_tfidf(text) for text in texts]
        
        # TF-IDF
        texts_tfidf = self.vectorizer.transform(cleaned_texts)
        
        # Предсказания
        predictions = self.model.predict(texts_tfidf)
        probabilities = self.model.predict_proba(texts_tfidf)
        
        # Формируем результаты
        results = []
        for pred, probs in zip(predictions, probabilities):
            category = self.label_to_category[pred]
            confidence = probs[pred]
            results.append((category, confidence))
        
        return results
    
    def save(self, path: str):
        """Сохранить модель на диск.
        
        Args:
            path: Путь для сохранения
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Сохраняем всё вместе
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'label_to_category': self.label_to_category,
            'category_to_label': self.category_to_label
        }
        
        joblib.dump(model_data, path)
        print(f"✅ Модель сохранена: {path}")
    
    def load(self, path: str):
        """Загрузить модель с диска.
        
        Args:
            path: Путь к модели
        """
        model_data = joblib.load(path)
        
        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.label_to_category = model_data['label_to_category']
        self.category_to_label = model_data['category_to_label']
        
        print(f"✅ Модель загружена: {path}")


# ===== КЛАСС 2: BERT CLASSIFIER (Продвинутый) =====

class BertClassifier:
    """Классификатор на основе BERT transformer.
    
    ====== ЧТО ТАКОЕ BERT? ======
    
    BERT = Bidirectional Encoder Representations from Transformers
    
    Революционная модель от Google (2018).
    
    Отличия от TF-IDF:
    1. Понимает КОНТЕКСТ
       - "Apple pie" vs "Apple iPhone" - разные значения!
       - TF-IDF: одинаковые векторы
       - BERT: разные векторы
    
    2. Понимает ПОРЯДОК СЛОВ
       - "Dog bites man" vs "Man bites dog" - разный смысл!
       - TF-IDF: одинаковые векторы
       - BERT: разные векторы
    
    3. PRETRAINED (предобученная)
       - Обучена на миллиардах текстов
       - Уже понимает английский язык
       - Мы только "fine-tune" (дообучаем) на наших данных
    
    Преимущества:
    + Очень точная (90-95%+ accuracy)
    + Понимает контекст
    + Требует меньше данных (transfer learning)
    
    Недостатки:
    - Медленная (секунды вместо миллисекунд)
    - Требует больше памяти
    - Сложнее в понимании
    """
    
    def __init__(self, model_name: str = settings.CLASSIFICATION_MODEL):
        """Инициализация BERT классификатора.
        
        Args:
            model_name: Имя pretrained модели
                       "distilbert-base-uncased" - быстрая
                       "bert-base-uncased" - стандартная
                       "roberta-base" - улучшенная
        """
        self.model_name = model_name
        self.tokenizer = None  # Загружается при обучении
        self.model = None
        self.label_to_category = {}
        self.category_to_label = {}
        
        # Device (CPU или GPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🖥️  Using device: {self.device}")
    
    # TODO: Реализация train, predict для BERT
    # Это будет в следующем файле, т.к. BERT более сложный


# ===== USAGE EXAMPLES =====
"""
Примеры использования:

# ===== TF-IDF Classifier =====

# 1. Создание и обучение
classifier = TfidfClassifier()

texts = [
    "Apple releases new iPhone with AI features",
    "Tesla announces electric car breakthrough",
    "Lakers win NBA championship",
    "New COVID vaccine shows promising results"
]

labels = [
    "technology",
    "technology",
    "sports",
    "health"
]

metrics = classifier.train(texts, labels)
print(f"Accuracy: {metrics['accuracy']:.2%}")

# 2. Предсказание
text = "Google launches new AI product"
category, confidence = classifier.predict(text)
print(f"Category: {category} ({confidence:.2%})")

# 3. Batch предсказание
texts = [
    "Bitcoin price rises",
    "Olympics begin in Paris"
]
results = classifier.predict_batch(texts)
for text, (cat, conf) in zip(texts, results):
    print(f"{text[:30]}: {cat} ({conf:.2%})")

# 4. Сохранение/загрузка
classifier.save("./models/classifier.joblib")
classifier.load("./models/classifier.joblib")


# ===== BERT Classifier (пока не реализован) =====
# bert_classifier = BertClassifier()
# bert_classifier.train(texts, labels)
# category, confidence = bert_classifier.predict(text)
"""