"""
Text Summarization Model

====== ЧТО ТАКОЕ SUMMARIZATION? ======

Суммаризация - создание короткого резюме длинного текста.

Задача: Длинный текст (500 слов) → Короткое резюме (50 слов)

====== ЗАЧЕМ НУЖНО? ======

1. Превью новостей: показать суть без чтения всего
2. Экономия времени: быстро понять о чем статья
3. Мобильные устройства: короткий текст лучше читается
4. SEO: meta descriptions для поисковиков

====== ДВА ПОДХОДА ======

1. EXTRACTIVE (извлекающая):
   - Выбирает самые важные ПРЕДЛОЖЕНИЯ из текста
   - Просто копирует их без изменений
   - Быстро, но менее читабельно
   
   Пример:
   Original: "The cat sat. It was black. The dog ran. It was fast."
   Summary: "The cat sat. The dog ran."

2. ABSTRACTIVE (абстрактная):
   - ГЕНЕРИРУЕТ новый текст
   - Перефразирует своими словами
   - Медленно, но читабельно
   
   Пример:
   Original: "The cat sat. It was black. The dog ran. It was fast."
   Summary: "A black cat and fast dog were active."

Мы реализуем ОБА подхода!
"""

import numpy as np
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import networkx as nx

from app.config import settings
from app.preprocessing.text_cleaner import preprocess_text, remove_html_tags


# Загрузка NLTK данных
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


# ===== EXTRACTIVE SUMMARIZATION =====

class ExtractiveSummarizer:
    """Extractive суммаризация - выбирает важные предложения.
    
    ====== АЛГОРИТМ: TextRank ======
    
    TextRank - адаптация алгоритма PageRank для текстов.
    
    Как работает PageRank:
    - Веб-страницы = узлы графа
    - Ссылки = ребра графа
    - Важность страницы = сколько на нее ссылок
    
    Как работает TextRank:
    - Предложения = узлы графа
    - Похожесть предложений = ребра графа
    - Важность предложения = насколько оно связано с другими
    
    Процесс:
    1. Разбиваем текст на предложения
    2. Векторизуем каждое предложение (TF-IDF)
    3. Считаем similarity между всеми парами предложений
    4. Строим граф: узлы = предложения, ребра = similarity
    5. Применяем PageRank → получаем важность каждого предложения
    6. Выбираем топ-N самых важных предложений
    
    Преимущества:
    + Быстро (секунды)
    + Не требует обучения
    + Сохраняет оригинальные фразы
    + Понятно и объяснимо
    
    Недостатки:
    - Может быть нечитабельно (просто набор предложений)
    - Не перефразирует
    - Может повторяться информация
    """
    
    def __init__(self):
        """Инициализация."""
        self.vectorizer = TfidfVectorizer()
    
    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Вычислить похожесть двух предложений.
        
        Используем cosine similarity между TF-IDF векторами.
        
        Args:
            sent1, sent2: Предложения
        
        Returns:
            Similarity score (0.0 до 1.0)
        """
        # Векторизуем оба предложения
        try:
            vectors = self.vectorizer.fit_transform([sent1, sent2])
            
            # Cosine similarity
            similarity = (vectors * vectors.T).toarray()[0, 1]
            
            return similarity
        except:
            return 0.0
    
    def summarize(
        self,
        text: str,
        num_sentences: int = 3,
        min_sentence_length: int = 10
    ) -> str:
        """Создать extractive summary.
        
        Args:
            text: Исходный текст
            num_sentences: Сколько предложений в резюме
            min_sentence_length: Минимальная длина предложения (в словах)
        
        Returns:
            Summary
            
        Example:
            >>> summarizer = ExtractiveSummarizer()
            >>> text = "Long article text here... (many sentences)"
            >>> summary = summarizer.summarize(text, num_sentences=3)
            >>> print(summary)
        """
        if not text:
            return ""
        
        # Очистка HTML
        text = remove_html_tags(text)
        
        # Шаг 1: Разбиваем на предложения
        sentences = sent_tokenize(text)
        
        # Фильтруем короткие предложения
        sentences = [
            sent for sent in sentences
            if len(sent.split()) >= min_sentence_length
        ]
        
        if len(sentences) <= num_sentences:
            # Текст уже короткий, возвращаем как есть
            return ' '.join(sentences)
        
        # Шаг 2: Preprocessing предложений (легкий)
        cleaned_sentences = [
            preprocess_text(
                sent,
                remove_html=False,  # уже сделано
                remove_stops=False,  # нужны для читабельности
                lemmatize=False
            )
            for sent in sentences
        ]
        
        # Шаг 3: Векторизация через TF-IDF
        try:
            sentence_vectors = self.vectorizer.fit_transform(cleaned_sentences)
        except:
            # Если векторизация не удалась, возвращаем первые N предложений
            return ' '.join(sentences[:num_sentences])
        
        # Шаг 4: Матрица similarity
        # similarity_matrix[i][j] = похожесть предложения i и j
        similarity_matrix = (sentence_vectors * sentence_vectors.T).toarray()
        
        # Шаг 5: Строим граф
        nx_graph = nx.from_numpy_array(similarity_matrix)
        
        # Шаг 6: PageRank для нахождения важных предложений
        scores = nx.pagerank(nx_graph)
        
        # Шаг 7: Ранжируем предложения по важности
        ranked_sentences = sorted(
            ((scores[i], i, sent) for i, sent in enumerate(sentences)),
            reverse=True
        )
        
        # Шаг 8: Выбираем топ-N предложений
        top_sentences = ranked_sentences[:num_sentences]
        
        # Шаг 9: Сортируем по оригинальному порядку (для читабельности)
        top_sentences = sorted(top_sentences, key=lambda x: x[1])
        
        # Формируем summary
        summary = ' '.join([sent for _, _, sent in top_sentences])
        
        return summary
    
    def get_sentence_scores(self, text: str) -> List[Dict[str, any]]:
        """Получить важность каждого предложения.
        
        Полезно для анализа и debugging.
        
        Args:
            text: Текст
        
        Returns:
            Список {sentence, score, rank}
        """
        sentences = sent_tokenize(remove_html_tags(text))
        cleaned = [preprocess_text(s, remove_stops=False) for s in sentences]
        
        try:
            vectors = self.vectorizer.fit_transform(cleaned)
            similarity_matrix = (vectors * vectors.T).toarray()
            graph = nx.from_numpy_array(similarity_matrix)
            scores = nx.pagerank(graph)
            
            results = []
            for i, (sent, score) in enumerate(zip(sentences, scores.values())):
                results.append({
                    "sentence": sent,
                    "score": score,
                    "rank": i + 1
                })
            
            # Сортируем по важности
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
        except:
            return []


# ===== ABSTRACTIVE SUMMARIZATION =====

class AbstractiveSummarizer:
    """Abstractive суммаризация - генерирует новый текст.
    
    ====== МОДЕЛИ ======
    
    Используем SOTA transformer модели:
    
    1. BART (Facebook):
       - facebook/bart-large-cnn
       - Обучена на новостях CNN/DailyMail
       - Отличная для news summarization
    
    2. Pegasus (Google):
       - google/pegasus-xsum
       - Специально для extreme summarization
       - Очень короткие summaries
    
    3. T5 (Google):
       - t5-base, t5-large
       - Универсальная модель
    
    По умолчанию используем BART - лучший выбор для новостей.
    
    ====== КАК РАБОТАЕТ? ======
    
    1. Encoder читает весь текст
    2. Создает internal representation (понимание текста)
    3. Decoder генерирует summary слово за словом
    4. Каждое слово генерируется с учетом контекста
    
    Это seq2seq модель (sequence to sequence):
    Input sequence (long text) → Output sequence (short summary)
    
    Преимущества:
    + Создает читабельный текст
    + Может перефразировать
    + Понимает смысл
    
    Недостатки:
    - Медленно (5-10 секунд на текст)
    - Требует GPU для хорошей скорости
    - Может "галлюцинировать" (генерировать факты)
    """
    
    def __init__(
        self,
        model_name: str = settings.SUMMARIZATION_MODEL
    ):
        """Инициализация.
        
        Args:
            model_name: Hugging Face модель
        """
        self.model_name = model_name
        
        print(f"📦 Loading summarization model: {model_name}")
        
        # Pipeline для суммаризации
        self.pipeline = pipeline(
            "summarization",
            model=model_name,
            device=-1  # CPU (-1) или GPU (0)
        )
        
        # Tokenizer для подсчета токенов
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        print(f"✅ Model loaded successfully")
    
    def summarize(
        self,
        text: str,
        max_length: int = 130,
        min_length: int = 30,
        do_sample: bool = False
    ) -> str:
        """Создать abstractive summary.
        
        Args:
            text: Исходный текст
            max_length: Макс длина summary (в токенах)
            min_length: Мин длина summary (в токенах)
            do_sample: Использовать sampling (более creative, но менее stable)
        
        Returns:
            Summary
            
        Example:
            >>> summarizer = AbstractiveSummarizer()
            >>> text = "Long news article..."
            >>> summary = summarizer.summarize(text, max_length=50)
            >>> print(summary)
            "Short generated summary of the article."
        """
        if not text:
            return ""
        
        # Очистка
        text = remove_html_tags(text)
        
        # BART/Pegasus имеют лимит ~1024 токена
        # Если текст длиннее, обрезаем
        tokens = self.tokenizer.encode(text, truncation=True, max_length=1024)
        text = self.tokenizer.decode(tokens, skip_special_tokens=True)
        
        # Генерация summary
        try:
            result = self.pipeline(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=do_sample,
                truncation=True
            )
            
            summary = result[0]['summary_text']
            
            return summary
            
        except Exception as e:
            print(f"❌ Summarization failed: {e}")
            # Fallback: возвращаем первые N предложений
            sentences = sent_tokenize(text)
            return ' '.join(sentences[:2])
    
    def summarize_batch(
        self,
        texts: List[str],
        max_length: int = 130,
        min_length: int = 30,
        batch_size: int = 4
    ) -> List[str]:
        """Batch суммаризация (быстрее для многих текстов).
        
        Args:
            texts: Список текстов
            max_length: Макс длина
            min_length: Мин длина
            batch_size: Размер батча
        
        Returns:
            Список summaries
        """
        # Preprocessing
        cleaned_texts = [remove_html_tags(text) for text in texts]
        
        # Truncate
        truncated_texts = []
        for text in cleaned_texts:
            tokens = self.tokenizer.encode(text, truncation=True, max_length=1024)
            truncated_texts.append(
                self.tokenizer.decode(tokens, skip_special_tokens=True)
            )
        
        # Batch generation
        try:
            results = self.pipeline(
                truncated_texts,
                max_length=max_length,
                min_length=min_length,
                batch_size=batch_size,
                truncation=True
            )
            
            summaries = [r['summary_text'] for r in results]
            return summaries
            
        except Exception as e:
            print(f"❌ Batch summarization failed: {e}")
            # Fallback
            return [' '.join(sent_tokenize(t)[:2]) for t in truncated_texts]


# ===== HYBRID SUMMARIZER =====

class HybridSummarizer:
    """Гибридный суммаризатор - комбинирует extractive и abstractive.
    
    Стратегия:
    1. Extractive: выбираем важные предложения (быстро)
    2. Abstractive: перефразируем их (качественно)
    
    Преимущества:
    + Быстрее чем pure abstractive
    + Качественнее чем pure extractive
    + Лучший баланс
    """
    
    def __init__(self):
        """Инициализация."""
        self.extractive = ExtractiveSummarizer()
        self.abstractive = AbstractiveSummarizer()
    
    def summarize(
        self,
        text: str,
        num_sentences_extract: int = 5,
        max_length_abstract: int = 100
    ) -> str:
        """Гибридная суммаризация.
        
        Args:
            text: Исходный текст
            num_sentences_extract: Сколько предложений извлечь
            max_length_abstract: Макс длина финального summary
        
        Returns:
            Summary
        """
        # Шаг 1: Extractive (выбираем важные части)
        extracted = self.extractive.summarize(text, num_sentences=num_sentences_extract)
        
        # Шаг 2: Abstractive (перефразируем)
        final_summary = self.abstractive.summarize(
            extracted,
            max_length=max_length_abstract
        )
        
        return final_summary


# ===== UTILITY FUNCTIONS =====

def calculate_compression_ratio(original: str, summary: str) -> float:
    """Вычислить степень сжатия.
    
    Args:
        original: Оригинальный текст
        summary: Summary
    
    Returns:
        Compression ratio (0.0 to 1.0)
        
    Example:
        >>> ratio = calculate_compression_ratio("100 words", "20 words")
        >>> print(ratio)
        0.2  # Summary is 20% of original
    """
    orig_words = len(original.split())
    summ_words = len(summary.split())
    
    if orig_words == 0:
        return 0.0
    
    return summ_words / orig_words


def get_summary_stats(original: str, summary: str) -> Dict[str, any]:
    """Статистика summary.
    
    Args:
        original: Оригинальный текст
        summary: Summary
    
    Returns:
        Статистика
    """
    return {
        "original_length": len(original),
        "original_words": len(original.split()),
        "original_sentences": len(sent_tokenize(original)),
        "summary_length": len(summary),
        "summary_words": len(summary.split()),
        "summary_sentences": len(sent_tokenize(summary)),
        "compression_ratio": calculate_compression_ratio(original, summary)
    }


# ===== USAGE EXAMPLES =====
"""
# ===== 1. Extractive Summarization =====

extractive = ExtractiveSummarizer()

text = '''
Long news article about AI breakthrough.
Multiple sentences with different information.
Some sentences are more important than others.
The key findings are in certain sentences.
Other sentences provide background context.
'''

# Создаем summary из 2 предложений
summary = extractive.summarize(text, num_sentences=2)
print(summary)

# Смотрим важность всех предложений
scores = extractive.get_sentence_scores(text)
for item in scores[:3]:  # топ-3
    print(f"Score {item['score']:.3f}: {item['sentence'][:50]}...")


# ===== 2. Abstractive Summarization =====

abstractive = AbstractiveSummarizer()

text = '''
Apple Inc. announced today the release of the new iPhone 15 
with revolutionary AI features. The device features an advanced 
neural engine capable of real-time language translation and 
enhanced photography. CEO Tim Cook stated that this represents 
a major leap forward in mobile technology.
'''

# Генерируем summary
summary = abstractive.summarize(text, max_length=50)
print(summary)
# Output (generated): "Apple releases iPhone 15 with AI features, 
#                     neural engine for translation and photography."


# Batch summarization
texts = [
    "Long article 1...",
    "Long article 2...",
    "Long article 3..."
]
summaries = abstractive.summarize_batch(texts)
for text, summ in zip(texts, summaries):
    print(f"Original: {text[:50]}...")
    print(f"Summary:  {summ}\n")


# ===== 3. Hybrid Summarization =====

hybrid = HybridSummarizer()

text = "Very long news article with many details..."
summary = hybrid.summarize(text)
print(summary)


# ===== 4. Статистика =====

original = "Long article text..."
summary = "Short summary..."

stats = get_summary_stats(original, summary)
print(f"Compression: {stats['compression_ratio']:.1%}")
print(f"Original: {stats['original_words']} words → Summary: {stats['summary_words']} words")


# ===== Выбор подхода =====

# Для СКОРОСТИ (миллисекунды):
summarizer = ExtractiveSummarizer()

# Для КАЧЕСТВА (секунды):
summarizer = AbstractiveSummarizer()

# Для БАЛАНСА:
summarizer = HybridSummarizer()
"""