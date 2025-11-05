"""
News Clustering Model

====== ЧТО ТАКОЕ CLUSTERING? ======

Clustering (кластеризация) - автоматическая группировка похожих новостей.

Задача: Дан список новостей → сгруппировать по темам БЕЗ меток!

====== ЗАЧЕМ НУЖНО? ======

1. **Trending Topics**: Найти популярные темы дня
   - Много новостей об одном событии → кластер
   
2. **News Deduplication**: Группировка дубликатов
   - Одна новость переопубликована на разных сайтах
   
3. **Topic Discovery**: Обнаружение новых тем
   - Автоматически найти о чем пишут
   
4. **News Organization**: Организация контента
   - "Похожие новости" feature

====== КАК РАБОТАЕТ? ======

1. Преобразуем новости в embeddings (векторы)
2. Применяем clustering algorithm
3. Получаем группы похожих новостей

====== АЛГОРИТМЫ ======

1. **K-Means** - самый популярный
   - Нужно знать количество кластеров заранее
   - Быстрый
   
2. **DBSCAN** - density-based
   - Автоматически определяет количество
   - Находит выбросы (outliers)
   
3. **Hierarchical** - иерархический
   - Строит дерево кластеров
   - Можно выбрать любой уровень
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from collections import Counter, defaultdict
import logging

from app.models.embeddings import TextEmbeddingModel


logger = logging.getLogger(__name__)


# ===== K-MEANS CLUSTERING =====

class KMeansNewsClusterer:
    """K-Means кластеризация новостей.
    
    ====== K-MEANS ALGORITHM ======
    
    1. Выбираем K случайных точек как центры кластеров
    2. Назначаем каждую новость ближайшему центру
    3. Пересчитываем центры (среднее всех точек в кластере)
    4. Повторяем шаги 2-3 до сходимости
    
    Преимущества:
    + Простой и быстрый
    + Хорошо масштабируется
    + Предсказуемый результат
    
    Недостатки:
    - Нужно знать K заранее
    - Чувствителен к начальным центрам
    - Предполагает круглые кластеры
    """
    
    def __init__(self, embedding_model: TextEmbeddingModel):
        """Инициализация.
        
        Args:
            embedding_model: Модель для создания embeddings
        """
        self.embedding_model = embedding_model
        self.kmeans = None
        self.embeddings = None
        self.texts = None
    
    def fit(
        self,
        texts: List[str],
        n_clusters: int = 5,
        random_state: int = 42
    ) -> Dict[int, List[int]]:
        """Кластеризация новостей.
        
        Args:
            texts: Список новостей
            n_clusters: Количество кластеров
            random_state: Seed для воспроизводимости
        
        Returns:
            Словарь {cluster_id: [indices новостей]}
            
        Example:
            >>> clusterer = KMeansNewsClusterer(embedding_model)
            >>> texts = ["AI news", "Sports news", "ML article", "Football game"]
            >>> clusters = clusterer.fit(texts, n_clusters=2)
            >>> print(clusters)
            {0: [0, 2], 1: [1, 3]}  # Tech vs Sports
        """
        logger.info(f"Clustering {len(texts)} texts into {n_clusters} clusters...")
        
        # Сохраняем тексты
        self.texts = texts
        
        # Создаем embeddings
        logger.info("Creating embeddings...")
        self.embeddings = self.embedding_model.encode_batch(
            texts,
            show_progress=True
        )
        
        # K-Means clustering
        logger.info("Running K-Means...")
        self.kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10  # Количество инициализаций
        )
        
        labels = self.kmeans.fit_predict(self.embeddings)
        
        # Группируем по кластерам
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            clusters[int(label)].append(idx)
        
        # Оцениваем качество
        if len(set(labels)) > 1:
            silhouette = silhouette_score(self.embeddings, labels)
            logger.info(f"Silhouette score: {silhouette:.3f}")
        
        return dict(clusters)
    
    def predict(self, text: str) -> int:
        """Определить кластер для новой новости.
        
        Args:
            text: Новость
        
        Returns:
            Cluster ID
        """
        if self.kmeans is None:
            raise ValueError("Model not fitted! Call fit() first.")
        
        # Embedding нового текста
        embedding = self.embedding_model.encode(text)
        
        # Предсказание кластера
        cluster_id = self.kmeans.predict([embedding])[0]
        
        return int(cluster_id)
    
    def get_cluster_centers(self) -> np.ndarray:
        """Получить центры кластеров.
        
        Returns:
            Матрица центров
        """
        if self.kmeans is None:
            raise ValueError("Model not fitted!")
        
        return self.kmeans.cluster_centers_
    
    def get_cluster_representatives(
        self,
        clusters: Dict[int, List[int]],
        top_n: int = 3
    ) -> Dict[int, List[str]]:
        """Получить репрезентативные новости для каждого кластера.
        
        Выбирает новости ближайшие к центру кластера.
        
        Args:
            clusters: Результат fit()
            top_n: Сколько представителей
        
        Returns:
            Словарь {cluster_id: [тексты]}
        """
        if self.kmeans is None or self.texts is None:
            raise ValueError("Model not fitted!")
        
        centers = self.kmeans.cluster_centers_
        representatives = {}
        
        for cluster_id, indices in clusters.items():
            # Embeddings новостей в этом кластере
            cluster_embeddings = self.embeddings[indices]
            
            # Расстояния до центра
            center = centers[cluster_id]
            distances = np.linalg.norm(cluster_embeddings - center, axis=1)
            
            # Топ-N ближайших
            top_indices = np.argsort(distances)[:top_n]
            
            # Получаем тексты
            representatives[cluster_id] = [
                self.texts[indices[i]] for i in top_indices
            ]
        
        return representatives


# ===== DBSCAN CLUSTERING =====

class DBSCANNewsClusterer:
    """DBSCAN кластеризация - автоматическое определение кластеров.
    
    ====== DBSCAN ALGORITHM ======
    
    Density-Based Spatial Clustering of Applications with Noise
    
    Идея: Кластер = плотная область точек
    
    Параметры:
    - eps: Радиус окрестности
    - min_samples: Минимум точек для кластера
    
    Преимущества:
    + НЕ нужно знать количество кластеров
    + Находит кластеры произвольной формы
    + Находит outliers (шум)
    
    Недостатки:
    - Чувствителен к параметрам
    - Медленнее K-Means
    - Плохо работает с разной плотностью
    """
    
    def __init__(self, embedding_model: TextEmbeddingModel):
        """Инициализация."""
        self.embedding_model = embedding_model
        self.dbscan = None
        self.embeddings = None
        self.texts = None
    
    def fit(
        self,
        texts: List[str],
        eps: float = 0.5,
        min_samples: int = 3
    ) -> Dict[int, List[int]]:
        """Кластеризация с DBSCAN.
        
        Args:
            texts: Список новостей
            eps: Максимальное расстояние между точками
            min_samples: Минимум точек для кластера
        
        Returns:
            Словарь {cluster_id: [indices]}
            -1 = noise (outliers)
        """
        logger.info(f"DBSCAN clustering {len(texts)} texts...")
        
        self.texts = texts
        
        # Embeddings
        logger.info("Creating embeddings...")
        self.embeddings = self.embedding_model.encode_batch(texts, show_progress=True)
        
        # DBSCAN
        logger.info(f"Running DBSCAN (eps={eps}, min_samples={min_samples})...")
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        labels = self.dbscan.fit_predict(self.embeddings)
        
        # Группируем
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            clusters[int(label)].append(idx)
        
        # Статистика
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")
        
        return dict(clusters)
    
    def auto_tune_eps(self, texts: List[str]) -> float:
        """Автоматически подобрать параметр eps.
        
        Использует k-distance graph для определения оптимального eps.
        
        Args:
            texts: Тексты
        
        Returns:
            Рекомендуемое значение eps
        """
        from sklearn.neighbors import NearestNeighbors
        
        # Embeddings
        embeddings = self.embedding_model.encode_batch(texts)
        
        # Находим расстояния до 4-го ближайшего соседа
        neighbors = NearestNeighbors(n_neighbors=4, metric='cosine')
        neighbors.fit(embeddings)
        distances, _ = neighbors.kneighbors(embeddings)
        
        # 4-я колонка (индекс 3) содержит расстояние до 4-го соседа
        distances = np.sort(distances[:, 3], axis=0)
        
        # "Колено" графика = хороший eps
        # Простая эвристика: 90-й перцентиль
        recommended_eps = np.percentile(distances, 90)
        
        logger.info(f"Recommended eps: {recommended_eps:.3f}")
        
        return float(recommended_eps)


# ===== HIERARCHICAL CLUSTERING =====

class HierarchicalNewsClusterer:
    """Иерархическая кластеризация.
    
    Строит дерево (дендрограмму) кластеров.
    Можно "срезать" на любом уровне.
    """
    
    def __init__(self, embedding_model: TextEmbeddingModel):
        """Инициализация."""
        self.embedding_model = embedding_model
        self.model = None
        self.embeddings = None
        self.texts = None
    
    def fit(
        self,
        texts: List[str],
        n_clusters: int = 5,
        linkage: str = 'ward'
    ) -> Dict[int, List[int]]:
        """Иерархическая кластеризация.
        
        Args:
            texts: Тексты
            n_clusters: Количество кластеров
            linkage: Метод связывания ('ward', 'average', 'complete')
        
        Returns:
            Кластеры
        """
        logger.info(f"Hierarchical clustering {len(texts)} texts...")
        
        self.texts = texts
        self.embeddings = self.embedding_model.encode_batch(texts, show_progress=True)
        
        self.model = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage
        )
        
        labels = self.model.fit_predict(self.embeddings)
        
        # Группируем
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            clusters[int(label)].append(idx)
        
        return dict(clusters)


# ===== UTILITY FUNCTIONS =====

def get_cluster_keywords(
    texts: List[str],
    cluster_indices: List[int],
    top_n: int = 10
) -> List[str]:
    """Извлечь ключевые слова кластера.
    
    Args:
        texts: Все тексты
        cluster_indices: Индексы текстов в кластере
        top_n: Сколько ключевых слов
    
    Returns:
        Список ключевых слов
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    # Тексты кластера
    cluster_texts = [texts[i] for i in cluster_indices]
    
    # TF-IDF
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(cluster_texts)
    
    # Средний TF-IDF score для каждого слова
    mean_tfidf = np.array(tfidf_matrix.mean(axis=0)).flatten()
    
    # Топ слова
    feature_names = vectorizer.get_feature_names_out()
    top_indices = mean_tfidf.argsort()[-top_n:][::-1]
    
    keywords = [feature_names[i] for i in top_indices]
    
    return keywords


def suggest_optimal_k(
    embeddings: np.ndarray,
    k_range: range = range(2, 11)
) -> int:
    """Предложить оптимальное количество кластеров.
    
    Использует Elbow Method и Silhouette Score.
    
    Args:
        embeddings: Матрица embeddings
        k_range: Диапазон K для проверки
    
    Returns:
        Оптимальное K
    """
    silhouette_scores = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        silhouette_scores.append(score)
    
    # K с максимальным silhouette score
    optimal_k = k_range[np.argmax(silhouette_scores)]
    
    logger.info(f"Optimal K: {optimal_k} (silhouette: {max(silhouette_scores):.3f})")
    
    return optimal_k


# ===== USAGE EXAMPLES =====
"""
# ===== K-Means Clustering =====

from app.models.embeddings import TextEmbeddingModel
from app.models.clustering import KMeansNewsClusterer

# Модели
embedding_model = TextEmbeddingModel()
clusterer = KMeansNewsClusterer(embedding_model)

# Новости
news = [
    "AI breakthrough in healthcare",
    "Machine learning advances research",
    "Lakers win NBA championship",
    "Football team scores victory",
    "Deep learning improves diagnosis",
    "Basketball playoffs begin"
]

# Кластеризация
clusters = clusterer.fit(news, n_clusters=2)

print("Clusters:")
for cluster_id, indices in clusters.items():
    print(f"\nCluster {cluster_id}:")
    for idx in indices:
        print(f"  - {news[idx]}")

# Output:
# Cluster 0: (Tech news)
#   - AI breakthrough in healthcare
#   - Machine learning advances research
#   - Deep learning improves diagnosis
#
# Cluster 1: (Sports news)
#   - Lakers win NBA championship
#   - Football team scores victory
#   - Basketball playoffs begin


# Представители кластеров
representatives = clusterer.get_cluster_representatives(clusters, top_n=2)
print("\nCluster representatives:")
for cluster_id, texts in representatives.items():
    print(f"Cluster {cluster_id}:")
    for text in texts:
        print(f"  - {text}")


# Предсказание для новой новости
new_news = "Neural networks in medicine"
cluster_id = clusterer.predict(new_news)
print(f"\nNew news belongs to cluster: {cluster_id}")


# ===== DBSCAN Clustering =====

from app.models.clustering import DBSCANNewsClusterer

dbscan_clusterer = DBSCANNewsClusterer(embedding_model)

# Авто-подбор eps
optimal_eps = dbscan_clusterer.auto_tune_eps(news)

# Кластеризация
clusters = dbscan_clusterer.fit(news, eps=optimal_eps, min_samples=2)

print("\nDBSCAN Clusters:")
for cluster_id, indices in clusters.items():
    if cluster_id == -1:
        print("Noise (outliers):")
    else:
        print(f"Cluster {cluster_id}:")
    for idx in indices:
        print(f"  - {news[idx]}")


# ===== Ключевые слова кластера =====

from app.models.clustering import get_cluster_keywords

keywords = get_cluster_keywords(news, clusters[0], top_n=5)
print(f"\nCluster 0 keywords: {keywords}")


# ===== Оптимальное K =====

from app.models.clustering import suggest_optimal_k

embeddings = embedding_model.encode_batch(news)
optimal_k = suggest_optimal_k(embeddings, range(2, 6))
print(f"Suggested number of clusters: {optimal_k}")
"""