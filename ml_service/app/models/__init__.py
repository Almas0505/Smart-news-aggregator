"""
ML Models Module

Этот модуль содержит все ML/AI модели для обработки текста новостей.
"""

from app.models.classifier import TfidfClassifier, BertClassifier
from app.models.ner_model import NERModel
from app.models.sentiment import (
    SimpleSentimentAnalyzer,
    MLSentimentAnalyzer,
    TransformerSentimentAnalyzer,
    EnsembleSentimentAnalyzer
)
from app.models.summarizer import (
    ExtractiveSummarizer,
    AbstractiveSummarizer,
    HybridSummarizer
)
from app.models.embeddings import TextEmbeddingModel, SimpleVectorDB


__all__ = [
    # Classification
    "TfidfClassifier",
    "BertClassifier",
    
    # NER
    "NERModel",
    
    # Sentiment
    "SimpleSentimentAnalyzer",
    "MLSentimentAnalyzer",
    "TransformerSentimentAnalyzer",
    "EnsembleSentimentAnalyzer",
    
    # Summarization
    "ExtractiveSummarizer",
    "AbstractiveSummarizer",
    "HybridSummarizer",
    
    # Embeddings
    "TextEmbeddingModel",
    "SimpleVectorDB",
]