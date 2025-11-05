"""
Named Entity Recognition (NER) Model

====== ЧТО ТАКОЕ NER? ======

NER (Named Entity Recognition) - извлечение именованных сущностей из текста.

Задача: Найти и классифицировать важные объекты в тексте:
- PERSON - люди (Elon Musk, Joe Biden)
- ORGANIZATION - организации (Tesla, Google, UN)
- LOCATION - места (New York, Europe, Mars)
- DATE - даты (January 1st, 2024)
- MONEY - деньги ($1 million, €500)
- PRODUCT - продукты (iPhone, Windows)

====== ЗАЧЕМ ЭТО НУЖНО? ======

1. Для поиска: "Найди новости про Tesla"
2. Для аналитики: "Сколько раз упоминается Biden?"
3. Для связей: "Кто упоминается вместе с Apple?"
4. Для базы знаний: Строим граф связей между сущностями

====== ПРИМЕР ======

Input:
"Elon Musk announced that Tesla will open a new factory in Berlin next year"

Output:
[
    {"text": "Elon Musk", "type": "PERSON", "start": 0, "end": 9},
    {"text": "Tesla", "type": "ORGANIZATION", "start": 27, "end": 32},
    {"text": "Berlin", "type": "LOCATION", "start": 61, "end": 67},
    {"text": "next year", "type": "DATE", "start": 68, "end": 77}
]

====== КАК РАБОТАЕТ? ======

Используем spaCy - современная NLP библиотека от Explosion AI.

spaCy уже содержит pretrained модели, которые умеют:
1. Токенизация (разбивка на слова)
2. POS-tagging (части речи)
3. Dependency parsing (грамматические связи)
4. NER (извлечение сущностей)

Мы используем готовую модель, но можем и дообучить на своих данных!
"""

import spacy
from spacy.tokens import Doc
from typing import List, Dict, Optional, Tuple
from collections import Counter
import logging

from app.config import settings


logger = logging.getLogger(__name__)


# ===== ОСНОВНОЙ КЛАСС NER =====

class NERModel:
    """Named Entity Recognition модель на основе spaCy.
    
    spaCy предоставляет несколько pretrained моделей:
    - en_core_web_sm (small) - 12 MB, быстрая, базовая точность
    - en_core_web_md (medium) - 40 MB, средняя скорость, хорошая точность
    - en_core_web_lg (large) - 560 MB, медленная, отличная точность
    - en_core_web_trf (transformer) - BERT-based, самая точная, самая медленная
    
    Мы используем 'sm' по умолчанию для баланса скорости и точности.
    """
    
    def __init__(self, model_name: str = settings.SPACY_MODEL):
        """Инициализация NER модели.
        
        Args:
            model_name: Название spaCy модели
        """
        self.model_name = model_name
        
        try:
            # Загружаем spaCy модель
            logger.info(f"Loading spaCy model: {model_name}")
            self.nlp = spacy.load(model_name)
            logger.info(f"✅ spaCy model loaded successfully")
            
        except OSError:
            # Модель не установлена
            logger.error(f"❌ spaCy model '{model_name}' not found!")
            logger.info("Install it with: python -m spacy download {model_name}")
            raise
        
        # Типы сущностей, которые нас интересуют
        self.entity_types = settings.ENTITY_TYPES
        
        logger.info(f"Entity types: {self.entity_types}")
    
    def extract_entities(
        self,
        text: str,
        min_confidence: float = 0.0
    ) -> List[Dict[str, any]]:
        """Извлечь сущности из текста.
        
        ====== ПРОЦЕСС ======
        
        1. spaCy обрабатывает текст (токенизация, POS-tagging, и т.д.)
        2. NER component находит сущности
        3. Фильтруем по типам и уверенности
        4. Возвращаем структурированный результат
        
        Args:
            text: Исходный текст
            min_confidence: Минимальная уверенность (0.0-1.0)
                           spaCy не всегда дает confidence, поэтому по умолчанию 0.0
        
        Returns:
            Список сущностей
            
        Example:
            >>> ner = NERModel()
            >>> text = "Apple CEO Tim Cook announced new iPhone in California"
            >>> entities = ner.extract_entities(text)
            >>> print(entities)
            [
                {
                    "text": "Apple",
                    "type": "ORGANIZATION",
                    "start": 0,
                    "end": 5,
                    "confidence": 0.95
                },
                {
                    "text": "Tim Cook",
                    "type": "PERSON",
                    "start": 10,
                    "end": 18,
                    "confidence": 0.98
                },
                ...
            ]
        """
        if not text or not isinstance(text, str):
            return []
        
        # Обрабатываем текст через spaCy pipeline
        doc = self.nlp(text)
        
        entities = []
        
        # Итерируемся по найденным сущностям
        for ent in doc.ents:
            # Фильтруем по типам
            if ent.label_ in self.entity_types:
                entity = {
                    "text": ent.text,           # Текст сущности
                    "type": ent.label_,         # Тип (PERSON, ORG, и т.д.)
                    "start": ent.start_char,    # Начальная позиция в тексте
                    "end": ent.end_char,        # Конечная позиция
                }
                
                # spaCy >= 3.0 может предоставлять confidence через ent._.score
                # Но не все модели поддерживают это
                confidence = getattr(ent._, 'score', None)
                if confidence is not None:
                    entity["confidence"] = confidence
                    
                    # Фильтруем по уверенности
                    if confidence < min_confidence:
                        continue
                else:
                    # Если confidence недоступен, считаем 1.0
                    entity["confidence"] = 1.0
                
                entities.append(entity)
        
        return entities
    
    def extract_entities_batch(
        self,
        texts: List[str],
        min_confidence: float = 0.0,
        batch_size: int = 32
    ) -> List[List[Dict[str, any]]]:
        """Извлечь сущности из множества текстов (БЫСТРЕЕ!).
        
        spaCy может обрабатывать тексты батчами, что значительно быстрее
        чем по одному, особенно для больших объемов.
        
        Args:
            texts: Список текстов
            min_confidence: Минимальная уверенность
            batch_size: Размер батча для обработки
        
        Returns:
            Список списков сущностей (для каждого текста)
        """
        results = []
        
        # nlp.pipe() обрабатывает тексты батчами - НАМНОГО быстрее!
        # Это ключевая оптимизация для production
        for doc in self.nlp.pipe(texts, batch_size=batch_size):
            entities = []
            
            for ent in doc.ents:
                if ent.label_ in self.entity_types:
                    entity = {
                        "text": ent.text,
                        "type": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                    
                    confidence = getattr(ent._, 'score', None)
                    entity["confidence"] = confidence if confidence is not None else 1.0
                    
                    if entity["confidence"] >= min_confidence:
                        entities.append(entity)
            
            results.append(entities)
        
        return results
    
    def get_entity_types_count(self, text: str) -> Dict[str, int]:
        """Получить статистику по типам сущностей.
        
        Полезно для анализа: сколько людей, организаций, и т.д. упоминается.
        
        Args:
            text: Текст
        
        Returns:
            Словарь {тип: количество}
            
        Example:
            >>> text = "Elon Musk and Jeff Bezos met in New York"
            >>> stats = ner.get_entity_types_count(text)
            >>> print(stats)
            {"PERSON": 2, "LOCATION": 1}
        """
        entities = self.extract_entities(text)
        
        # Подсчитываем количество каждого типа
        type_counts = Counter(ent["type"] for ent in entities)
        
        return dict(type_counts)
    
    def get_unique_entities(
        self,
        text: str,
        entity_type: Optional[str] = None
    ) -> List[str]:
        """Получить список уникальных сущностей.
        
        Иногда одна сущность упоминается несколько раз.
        Эта функция вернет только уникальные.
        
        Args:
            text: Текст
            entity_type: Фильтр по типу (опционально)
        
        Returns:
            Список уникальных сущностей
            
        Example:
            >>> text = "Apple released iPhone. Apple stock rose."
            >>> entities = ner.get_unique_entities(text, "ORGANIZATION")
            >>> print(entities)
            ["Apple"]  # Хотя упоминается дважды
        """
        entities = self.extract_entities(text)
        
        # Фильтруем по типу если указан
        if entity_type:
            entities = [ent for ent in entities if ent["type"] == entity_type]
        
        # Получаем уникальные текстовые значения
        unique_texts = list(set(ent["text"] for ent in entities))
        
        return sorted(unique_texts)
    
    def extract_relationships(self, text: str) -> List[Dict[str, any]]:
        """Извлечь отношения между сущностями.
        
        Это более продвинутая функция, которая ищет связи между сущностями
        через dependency parsing.
        
        Пример: "Elon Musk founded Tesla"
        Отношение: (Elon Musk, founded, Tesla)
        
        Args:
            text: Текст
        
        Returns:
            Список отношений
            
        Example:
            >>> text = "Tim Cook leads Apple"
            >>> relations = ner.extract_relationships(text)
            >>> print(relations)
            [
                {
                    "subject": "Tim Cook",
                    "subject_type": "PERSON",
                    "relation": "leads",
                    "object": "Apple",
                    "object_type": "ORGANIZATION"
                }
            ]
        """
        doc = self.nlp(text)
        relationships = []
        
        # Создаем маппинг токенов к сущностям
        token_to_entity = {}
        for ent in doc.ents:
            for token in ent:
                token_to_entity[token.i] = {
                    "text": ent.text,
                    "type": ent.label_
                }
        
        # Ищем связи через dependency tree
        for token in doc:
            # Ищем глаголы, которые связывают сущности
            if token.pos_ == "VERB":
                subject = None
                obj = None
                
                # Ищем subject и object
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        if child.i in token_to_entity:
                            subject = token_to_entity[child.i]
                    
                    if child.dep_ in ("dobj", "pobj", "attr"):
                        if child.i in token_to_entity:
                            obj = token_to_entity[child.i]
                
                # Если нашли и subject и object, записываем отношение
                if subject and obj:
                    relationships.append({
                        "subject": subject["text"],
                        "subject_type": subject["type"],
                        "relation": token.lemma_,  # Базовая форма глагола
                        "object": obj["text"],
                        "object_type": obj["type"]
                    })
        
        return relationships
    
    def highlight_entities_html(self, text: str) -> str:
        """Создать HTML с подсвеченными сущностями.
        
        Полезно для visualization и debugging.
        
        Args:
            text: Текст
        
        Returns:
            HTML строка
            
        Example:
            >>> text = "Apple released iPhone"
            >>> html = ner.highlight_entities_html(text)
            >>> # <mark class="ORG">Apple</mark> released <mark class="PRODUCT">iPhone</mark>
        """
        # spaCy имеет встроенный visualizer
        from spacy import displacy
        
        doc = self.nlp(text)
        
        # Генерируем HTML
        html = displacy.render(doc, style="ent", jupyter=False)
        
        return html


# ===== UTILITY FUNCTIONS =====

def deduplicate_entities(entities: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Удалить дубликаты сущностей.
    
    Иногда одна сущность упоминается несколько раз.
    Оставляем только первое упоминание.
    
    Args:
        entities: Список сущностей
    
    Returns:
        Список уникальных сущностей
    """
    seen = set()
    unique_entities = []
    
    for entity in entities:
        # Создаем ключ: (текст, тип)
        key = (entity["text"].lower(), entity["type"])
        
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities


def merge_overlapping_entities(entities: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Объединить пересекающиеся сущности.
    
    Иногда NER находит перекрывающиеся сущности:
    - "New York" (LOCATION)
    - "York" (LOCATION)
    
    Оставляем только более длинную.
    
    Args:
        entities: Список сущностей
    
    Returns:
        Список без пересечений
    """
    if not entities:
        return []
    
    # Сортируем по позиции начала
    sorted_entities = sorted(entities, key=lambda x: x["start"])
    
    merged = [sorted_entities[0]]
    
    for entity in sorted_entities[1:]:
        last = merged[-1]
        
        # Проверяем пересечение
        if entity["start"] < last["end"]:
            # Пересекаются - выбираем более длинную
            if (entity["end"] - entity["start"]) > (last["end"] - last["start"]):
                merged[-1] = entity
        else:
            # Не пересекаются
            merged.append(entity)
    
    return merged


# ===== USAGE EXAMPLES =====
"""
Примеры использования:

# ===== Базовое использование =====

from app.models.ner_model import NERModel

# 1. Инициализация
ner = NERModel()

# 2. Извлечение сущностей
text = "Elon Musk announced that Tesla will open a factory in Berlin"
entities = ner.extract_entities(text)

for ent in entities:
    print(f"{ent['text']:15} | {ent['type']:15} | {ent['confidence']:.2f}")

# Output:
# Elon Musk      | PERSON         | 0.98
# Tesla          | ORGANIZATION   | 0.95
# Berlin         | LOCATION       | 0.92


# ===== Batch обработка =====

texts = [
    "Apple CEO Tim Cook visited China",
    "Microsoft acquired GitHub for $7.5 billion",
    "Bitcoin price reached $50,000 in February"
]

results = ner.extract_entities_batch(texts)

for i, entities in enumerate(results):
    print(f"\nText {i+1}:")
    for ent in entities:
        print(f"  - {ent['text']} ({ent['type']})")


# ===== Статистика =====

text = "Meeting between Joe Biden and Xi Jinping in Geneva on Monday"
stats = ner.get_entity_types_count(text)
print(stats)
# {'PERSON': 2, 'LOCATION': 1, 'DATE': 1}


# ===== Уникальные сущности =====

text = "Apple released iPhone. Apple stock rose. iPhone sales increased."
unique_orgs = ner.get_unique_entities(text, "ORGANIZATION")
print(unique_orgs)  # ['Apple']

unique_products = ner.get_unique_entities(text, "PRODUCT")
print(unique_products)  # ['iPhone']


# ===== Отношения =====

text = "Tim Cook leads Apple. Elon Musk founded Tesla."
relations = ner.extract_relationships(text)

for rel in relations:
    print(f"{rel['subject']} --[{rel['relation']}]--> {rel['object']}")
# Tim Cook --[lead]--> Apple
# Elon Musk --[found]--> Tesla


# ===== HTML визуализация =====

text = "Apple announced new iPhone at WWDC in California"
html = ner.highlight_entities_html(text)
# Можно сохранить в файл или отправить в frontend
with open("entities.html", "w") as f:
    f.write(html)
"""