"""
Text Embeddings Model

====== ЧТО ТАКОЕ EMBEDDINGS? ======

Embeddings (векторные представления) - преобразование текста в числовой вектор.

Текст → Вектор чисел → Можем сравнивать математически

====== ЗАЧЕМ НУЖНЫ? ======

1. SEMANTIC SEARCH (семантический поиск):
   Запрос: "AI breakthrough"
   Находит: "Artificial intelligence advancement" (хотя слова разные!)
   
2. SIMILARITY (похожесть):
   Находим похожие новости для рекомендаций
   
3. CLUSTERING (кластеризация):
   Группируем новости по темам
   
4. DEDUPLICATION (дедупликация):
   Находим дубликаты новостей (переопубликованные)

====== КАК РАБОТАЕТ? ======

Старый подход (TF-IDF):
"apple" → [0, 0, 1, 0, 0, ...]  # one-hot encoding
"orange" → [0, 1, 0, 0, 0, ...]  # совершенно разные векторы

Проблема: "apple" и "orange" - оба фрукты, но векторы не похожи!

Новый подход (Embeddings):
"apple" → [0.2, -0.5, 0.8, ...]   # dense vector
"orange" → [0.3, -0.4, 0.7, ...]  # похожий вектор!
"car" → [-0.8, 0.3, -0.2, ...]    # совсем другой вектор

Модель ПОНИМАЕТ смысл и создает похожие векторы для похожих по смыслу слов!

====== EXAMPLE ======

text1 = "AI revolution in healthcare"
text2 = "Artificial intelligence transforms medicine"
text3 = "Bitcoin price rises"

embedding1 = [0.2, -0.5, 0.8, 0.3, ...]  # 384 числа
embedding2 = [0.3, -0.4, 0.7, 0.4, ...]  # похож на embedding1!
embedding3 = [-0.8, 0.3, -0.2, -0.5, ...] # совсем другой

similarity(embedding1, embedding2) = 0.95  # очень похожи!
similarity(embedding1, embedding3) = 0.12  # не похожи
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import joblib

from app.config import settings
from app.preprocessing.text_cleaner import preprocess_for_bert


# ===== ОСНОВНОЙ КЛАСС =====

class TextEmbeddingModel:
    """Модель для создания embeddings текста.
    
    ====== SENTENCE-TRANSFORMERS ======
    
    Используем библиотеку sentence-transformers - специализированные
    BERT модели для создания embeddings.
    
    Популярные модели:
    
    1. all-MiniLM-L6-v2 (наш default):
       - Размер: 80 MB
       - Скорость: быстрая
       - Размерность: 384
       - Качество: хорошее
       - Лучший выбор для production!
    
    2. all-mpnet-base-v2:
       - Размер: 420 MB
       - Скорость: медленная
       - Размерность: 768
       - Качество: отличное
       - Для максимальной точности
    
    3. multi-qa-MiniLM-L6-cos-v1:
       - Специально для Q&A и search
       - Размерность: 384
       - Хороша для вопросов
    
    ====== КАК РАБОТАЮТ? ======
    
    1. BERT кодирует текст
    2. Pooling (обычно mean) создает единый вектор из всех токенов
    3. Normalization для cosine similarity
    
    Модели уже обучены на миллиардах пар текстов!
    Не требуют дополнительного обучения.
    """
    
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        """Инициализация модели embeddings.
        
        Args:
            model_name: Название sentence-transformers модели
        """
        self.model_name = model_name
        
        print(f"📦 Loading embedding model: {model_name}")
        
        # Загружаем модель
        self.model = SentenceTransformer(model_name)
        
        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Размерность векторов
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        print(f"✅ Model loaded (dim={self.embedding_dim}, device={self.device})")
    
    def encode(
        self,
        text: str,
        normalize: bool = True,
        convert_to_numpy: bool = True
    ) -> np.ndarray:
        """Создать embedding для текста.
        
        Args:
            text: Текст
            normalize: Нормализовать вектор (для cosine similarity)
            convert_to_numpy: Конвертировать в numpy array
        
        Returns:
            Вектор embeddings (размерность: embedding_dim)
            
        Example:
            >>> model = TextEmbeddingModel()
            >>> text = "AI revolution in healthcare"
            >>> embedding = model.encode(text)
            >>> print(embedding.shape)
            (384,)
            >>> print(embedding[:5])
            [ 0.234, -0.456,  0.789, -0.123,  0.567]
        """
        if not text:
            # Пустой текст → нулевой вектор
            return np.zeros(self.embedding_dim)
        
        # Минимальный preprocessing
        cleaned_text = preprocess_for_bert(text)
        
        # Encoding
        embedding = self.model.encode(
            cleaned_text,
            normalize_embeddings=normalize,
            convert_to_numpy=convert_to_numpy,
            show_progress_bar=False
        )
        
        return embedding
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """Создать embeddings для множества текстов (БЫСТРЕЕ!).
        
        Args:
            texts: Список текстов
            batch_size: Размер батча
            show_progress: Показать progress bar
        
        Returns:
            Матрица embeddings (размерность: len(texts) × embedding_dim)
            
        Example:
            >>> texts = ["AI news", "Sports article", "Tech update"]
            >>> embeddings = model.encode_batch(texts)
            >>> print(embeddings.shape)
            (3, 384)
        """
        # Preprocessing
        cleaned_texts = [preprocess_for_bert(text) for text in texts]
        
        # Batch encoding - НАМНОГО быстрее чем по одному!
        embeddings = self.model.encode(
            cleaned_texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def compute_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Вычислить similarity между двумя текстами.
        
        Использует cosine similarity:
        - 1.0 = идентичные
        - 0.0 = не связаны
        - -1.0 = противоположные (редко в тексте)
        
        Args:
            text1, text2: Тексты для сравнения
        
        Returns:
            Similarity score (0.0 to 1.0)
            
        Example:
            >>> sim = model.compute_similarity(
            ...     "AI revolution",
            ...     "Artificial intelligence breakthrough"
            ... )
            >>> print(f"{sim:.2f}")
            0.87  # очень похожи!
        """
        # Создаем embeddings
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # Или используем встроенную функцию
        # similarity = util.cos_sim(emb1, emb2).item()
        
        return float(similarity)
    
    def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[Tuple[int, str, float]]:
        """Найти самые похожие тексты из списка кандидатов.
        
        Это основа SEMANTIC SEARCH!
        
        Args:
            query: Поисковый запрос
            candidates: Список текстов для поиска
            top_k: Сколько результатов вернуть
        
        Returns:
            Список (index, text, similarity_score)
            
        Example:
            >>> query = "AI in medicine"
            >>> candidates = [
            ...     "Machine learning transforms healthcare",
            ...     "Bitcoin price rises",
            ...     "Artificial intelligence cures diseases"
            ... ]
            >>> results = model.find_most_similar(query, candidates, top_k=2)
            >>> for idx, text, score in results:
            ...     print(f"{score:.2f}: {text}")
            0.89: Machine learning transforms healthcare
            0.92: Artificial intelligence cures diseases
        """
        # Encode query
        query_emb = self.encode(query)
        
        # Encode всех кандидатов (batch!)
        candidate_embs = self.encode_batch(candidates)
        
        # Вычисляем similarity с query
        similarities = cosine_similarity([query_emb], candidate_embs)[0]
        
        # Сортируем по убыванию similarity
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Формируем результаты
        results = [
            (int(idx), candidates[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
    
    def cluster_texts(
        self,
        texts: List[str],
        num_clusters: int = 5
    ) -> Dict[int, List[int]]:
        """Кластеризация текстов по смыслу.
        
        Группирует похожие тексты вместе.
        Полезно для:
        - Группировки новостей по темам
        - Нахождения trending topics
        - Организации контента
        
        Args:
            texts: Список текстов
            num_clusters: Количество кластеров
        
        Returns:
            Словарь {cluster_id: [indices текстов]}
            
        Example:
            >>> texts = [
            ...     "AI breakthrough",
            ...     "Lakers win game",
            ...     "Machine learning advances",
            ...     "NBA finals result",
            ...     "Deep learning innovation"
            ... ]
            >>> clusters = model.cluster_texts(texts, num_clusters=2)
            >>> print(clusters)
            {
                0: [0, 2, 4],  # AI topics
                1: [1, 3]      # Sports topics
            }
        """
        # Создаем embeddings
        embeddings = self.encode_batch(texts)
        
        # K-Means clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        
        # Группируем по кластерам
        clusters = {}
        for idx, label in enumerate(labels):
            label = int(label)
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)
        
        return clusters
    
    def find_duplicates(
        self,
        texts: List[str],
        threshold: float = 0.9
    ) -> List[Tuple[int, int, float]]:
        """Найти дубликаты/почти дубликаты.
        
        Полезно для дедупликации новостей:
        - Одна новость опубликована на разных сайтах
        - Перефразированные версии одной новости
        
        Args:
            texts: Список текстов
            threshold: Минимальный similarity для считания дубликатом
        
        Returns:
            Список (index1, index2, similarity)
            
        Example:
            >>> texts = [
            ...     "Apple releases new iPhone",
            ...     "New iPhone announced by Apple",
            ...     "Bitcoin price rises"
            ... ]
            >>> dupes = model.find_duplicates(texts, threshold=0.85)
            >>> print(dupes)
            [(0, 1, 0.94)]  # Первые два - дубликаты!
        """
        # Embeddings
        embeddings = self.encode_batch(texts)
        
        # Вычисляем similarity matrix
        similarities = cosine_similarity(embeddings)
        
        # Находим пары с high similarity
        duplicates = []
        n = len(texts)
        
        for i in range(n):
            for j in range(i + 1, n):  # Только верхний треугольник матрицы
                sim = similarities[i, j]
                if sim >= threshold:
                    duplicates.append((i, j, float(sim)))
        
        # Сортируем по similarity (от высокого к низкому)
        duplicates.sort(key=lambda x: x[2], reverse=True)
        
        return duplicates
    
    def get_centroid(self, embeddings: np.ndarray) -> np.ndarray:
        """Получить центроид (средний вектор) набора embeddings.
        
        Полезно для создания "профиля пользователя":
        - Пользователь читал статьи X, Y, Z
        - Создаем центроид их embeddings
        - Рекомендуем статьи близкие к центроиду
        
        Args:
            embeddings: Матрица embeddings
        
        Returns:
            Центроид (среднее)
        """
        return np.mean(embeddings, axis=0)
    
    def save_embeddings(self, embeddings: np.ndarray, path: str):
        """Сохранить embeddings на диск.
        
        Args:
            embeddings: Матрица embeddings
            path: Путь для сохранения
        """
        np.save(path, embeddings)
        print(f"✅ Embeddings saved: {path}")
    
    def load_embeddings(self, path: str) -> np.ndarray:
        """Загрузить embeddings с диска.
        
        Args:
            path: Путь к файлу
        
        Returns:
            Загруженные embeddings
        """
        embeddings = np.load(path)
        print(f"✅ Embeddings loaded: {path} (shape={embeddings.shape})")
        return embeddings


# ===== UTILITY CLASS: VECTOR DATABASE (Простой) =====

class SimpleVectorDB:
    """Простая in-memory vector database.
    
    Для production используйте:
    - Qdrant
    - Weaviate
    - Pinecone
    - Milvus
    
    Но для понимания концепта - эта простая реализация.
    """
    
    def __init__(self, embedding_model: TextEmbeddingModel):
        """Инициализация.
        
        Args:
            embedding_model: Модель для создания embeddings
        """
        self.model = embedding_model
        self.embeddings = []  # Список векторов
        self.metadata = []    # Список метаданных (тексты, IDs, и т.д.)
    
    def add(self, text: str, metadata: Optional[Dict] = None):
        """Добавить текст в database.
        
        Args:
            text: Текст
            metadata: Дополнительная информация
        """
        embedding = self.model.encode(text)
        self.embeddings.append(embedding)
        
        meta = metadata or {}
        meta['text'] = text
        self.metadata.append(meta)
    
    def add_batch(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """Добавить множество текстов.
        
        Args:
            texts: Список текстов
            metadatas: Список метаданных
        """
        embeddings = self.model.encode_batch(texts)
        self.embeddings.extend(embeddings)
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        for text, meta in zip(texts, metadatas):
            meta['text'] = text
            self.metadata.append(meta)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search в database.
        
        Args:
            query: Поисковый запрос
            top_k: Сколько результатов
        
        Returns:
            Список результатов с metadata и scores
        """
        if not self.embeddings:
            return []
        
        # Query embedding
        query_emb = self.model.encode(query)
        
        # Similarities
        embeddings_matrix = np.array(self.embeddings)
        similarities = cosine_similarity([query_emb], embeddings_matrix)[0]
        
        # Top-K
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            result = self.metadata[idx].copy()
            result['score'] = float(similarities[idx])
            results.append(result)
        
        return results
    
    def save(self, path: str):
        """Сохранить database."""
        data = {
            'embeddings': np.array(self.embeddings),
            'metadata': self.metadata
        }
        joblib.dump(data, path)
    
    def load(self, path: str):
        """Загрузить database."""
        data = joblib.load(path)
        self.embeddings = list(data['embeddings'])
        self.metadata = data['metadata']


# ===== USAGE EXAMPLES =====
"""
# ===== 1. Базовое использование =====

from app.models.embeddings import TextEmbeddingModel

model = TextEmbeddingModel()

# Создаем embedding
text = "AI revolution in healthcare"
embedding = model.encode(text)
print(f"Embedding dimension: {embedding.shape}")
print(f"First 5 values: {embedding[:5]}")


# ===== 2. Similarity =====

text1 = "Artificial intelligence in medicine"
text2 = "AI transforms healthcare"
text3 = "Bitcoin price rises"

sim12 = model.compute_similarity(text1, text2)
sim13 = model.compute_similarity(text1, text3)

print(f"Similarity(AI, healthcare): {sim12:.2f}")  # ~0.90
print(f"Similarity(AI, bitcoin): {sim13:.2f}")     # ~0.15


# ===== 3. Semantic Search =====

query = "machine learning news"
candidates = [
    "Deep learning breakthrough in computer vision",
    "Lakers win NBA championship",
    "Neural networks advance AI research",
    "Stock market hits all-time high",
    "Artificial intelligence revolutionizes industry"
]

results = model.find_most_similar(query, candidates, top_k=3)
print("\nSearch results:")
for idx, text, score in results:
    print(f"{score:.2f}: {text}")


# ===== 4. Clustering =====

news_articles = [
    "AI breakthrough announced",
    "Machine learning improves",
    "Lakers beat Warriors",
    "NBA playoffs begin",
    "Deep learning advances",
    "Football championship final"
]

clusters = model.cluster_texts(news_articles, num_clusters=2)
print("\nClusters:")
for cluster_id, indices in clusters.items():
    print(f"Cluster {cluster_id}:")
    for idx in indices:
        print(f"  - {news_articles[idx]}")


# ===== 5. Duplicate Detection =====

articles = [
    "Apple announces new iPhone release",
    "New iPhone unveiled by Apple",
    "Tesla stock price increases",
    "Apple's latest iPhone announcement"
]

duplicates = model.find_duplicates(articles, threshold=0.80)
print("\nDuplicates found:")
for i, j, sim in duplicates:
    print(f"{sim:.2f}:")
    print(f"  [{i}] {articles[i]}")
    print(f"  [{j}] {articles[j]}")


# ===== 6. Vector Database =====

db = SimpleVectorDB(model)

# Добавляем статьи
articles = [
    "AI transforms healthcare industry",
    "Lakers win championship game",
    "New vaccine shows promising results"
]

db.add_batch(articles)

# Semantic search
query = "artificial intelligence medical"
results = db.search(query, top_k=2)

print("\nDatabase search results:")
for result in results:
    print(f"{result['score']:.2f}: {result['text']}")


# ===== 7. User Profile Recommendations =====

# Статьи, которые прочитал пользователь
user_read = [
    "Machine learning advances",
    "AI in robotics",
    "Deep learning breakthrough"
]

# Создаем embeddings
read_embeddings = model.encode_batch(user_read)

# Центроид = "профиль интересов пользователя"
user_profile = model.get_centroid(read_embeddings)

# Новые статьи для рекомендации
new_articles = [
    "Neural networks in autonomous vehicles",  # Similar to AI/ML
    "Bitcoin reaches new high",                # Different topic
    "Computer vision applications in medicine" # Similar to AI/ML
]

# Находим релевантные
new_embeddings = model.encode_batch(new_articles)
similarities = cosine_similarity([user_profile], new_embeddings)[0]

# Сортируем по релевантности
recommendations = sorted(
    zip(new_articles, similarities),
    key=lambda x: x[1],
    reverse=True
)

print("\nRecommendations for user:")
for article, score in recommendations:
    print(f"{score:.2f}: {article}")
"""