"""
Train News Classifier Model

This script trains a news classifier to categorize articles into 8 categories:
- Technology
- Business
- Sports
- Entertainment
- Health
- Science
- Politics
- World

Usage:
    python -m ml_service.app.training.train_classifier --data data/training_data.csv
"""

import argparse
import pickle
import json
from pathlib import Path
from typing import Tuple, List
import logging

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Category mapping
CATEGORIES = [
    "Technology",
    "Business",
    "Sports",
    "Entertainment",
    "Health",
    "Science",
    "Politics",
    "World"
]

CATEGORY_TO_ID = {cat: idx for idx, cat in enumerate(CATEGORIES)}
ID_TO_CATEGORY = {idx: cat for cat, idx in CATEGORY_TO_ID.items()}


def load_data(file_path: str) -> Tuple[List[str], List[int]]:
    """
    Load training data from CSV.
    
    Expected columns: text, category
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        (texts, labels) tuple
    """
    logger.info(f"Loading data from {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Validate columns
    required_cols = ['text', 'category']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV must have columns: {required_cols}")
    
    # Convert category names to IDs
    df['category_id'] = df['category'].map(CATEGORY_TO_ID)
    
    # Remove rows with unknown categories
    df = df.dropna(subset=['category_id'])
    df['category_id'] = df['category_id'].astype(int)
    
    logger.info(f"Loaded {len(df)} samples")
    logger.info(f"Categories: {df['category'].value_counts().to_dict()}")
    
    return df['text'].tolist(), df['category_id'].tolist()


def create_pipeline(model_type: str = 'logistic') -> Pipeline:
    """
    Create sklearn pipeline.
    
    Args:
        model_type: 'logistic', 'random_forest', or 'naive_bayes'
        
    Returns:
        Pipeline instance
    """
    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=2,
        max_df=0.8,
        stop_words='english'
    )
    
    # Classifier
    if model_type == 'logistic':
        classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'random_forest':
        classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'naive_bayes':
        classifier = MultinomialNB()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    pipeline = Pipeline([
        ('vectorizer', vectorizer),
        ('classifier', classifier)
    ])
    
    return pipeline


def train_model(
    texts: List[str],
    labels: List[int],
    model_type: str = 'logistic',
    test_size: float = 0.2
) -> Pipeline:
    """
    Train classifier model.
    
    Args:
        texts: List of article texts
        labels: List of category IDs
        model_type: Model type
        test_size: Test set size
        
    Returns:
        Trained pipeline
    """
    logger.info("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels,
        test_size=test_size,
        random_state=42,
        stratify=labels
    )
    
    logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Create pipeline
    logger.info(f"Creating {model_type} pipeline...")
    pipeline = create_pipeline(model_type)
    
    # Train
    logger.info("Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    logger.info("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Test Accuracy: {accuracy:.4f}")
    
    # Classification report
    report = classification_report(
        y_test, y_pred,
        target_names=CATEGORIES,
        digits=4
    )
    logger.info(f"\nClassification Report:\n{report}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\nConfusion Matrix:\n{cm}")
    
    # Cross-validation
    logger.info("Performing cross-validation...")
    cv_scores = cross_val_score(pipeline, texts, labels, cv=5, n_jobs=-1)
    logger.info(f"CV Scores: {cv_scores}")
    logger.info(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return pipeline


def save_model(pipeline: Pipeline, output_dir: str):
    """
    Save trained model and metadata.
    
    Args:
        pipeline: Trained pipeline
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_file = output_path / "news_classifier.pkl"
    joblib.dump(pipeline, model_file)
    logger.info(f"Model saved to {model_file}")
    
    # Save metadata
    metadata = {
        "model_type": "news_classifier",
        "categories": CATEGORIES,
        "category_mapping": CATEGORY_TO_ID,
        "num_classes": len(CATEGORIES),
        "features": pipeline.named_steps['vectorizer'].get_feature_names_out().tolist()[:100]  # First 100
    }
    
    metadata_file = output_path / "classifier_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Metadata saved to {metadata_file}")


def generate_sample_data(output_file: str, num_samples: int = 1000):
    """
    Generate sample training data for testing.
    
    Args:
        output_file: Output CSV file
        num_samples: Number of samples to generate
    """
    logger.info(f"Generating {num_samples} sample articles...")
    
    # Sample texts for each category
    sample_texts = {
        "Technology": [
            "Apple releases new iPhone with advanced AI features",
            "Google announces breakthrough in quantum computing",
            "Tesla unveils new electric vehicle model",
            "Microsoft launches cloud gaming platform",
            "Artificial intelligence transforms software development"
        ],
        "Business": [
            "Stock market reaches all-time high amid economic recovery",
            "Amazon reports record quarterly earnings",
            "Federal Reserve announces interest rate decision",
            "Major companies announce merger deal",
            "Startup raises $100 million in funding round"
        ],
        "Sports": [
            "Championship finals set for weekend showdown",
            "Star athlete signs record-breaking contract",
            "Olympic games preparation underway",
            "Local team wins championship title",
            "New world record set in marathon race"
        ],
        "Entertainment": [
            "New blockbuster film breaks box office records",
            "Popular streaming series renewed for another season",
            "Music festival announces star-studded lineup",
            "Award ceremony honors best performances",
            "Celebrity couple announces engagement"
        ],
        "Health": [
            "New study reveals benefits of Mediterranean diet",
            "Breakthrough treatment shows promise for cancer patients",
            "Mental health awareness campaign launches nationwide",
            "Vaccine development enters final testing phase",
            "Exercise linked to improved cognitive function"
        ],
        "Science": [
            "NASA discovers potentially habitable exoplanet",
            "Scientists make breakthrough in climate research",
            "New species discovered in Amazon rainforest",
            "Particle physics experiment yields surprising results",
            "Archaeological find rewrites ancient history"
        ],
        "Politics": [
            "President announces new policy initiative",
            "Congress passes bipartisan legislation",
            "Election results show tight race",
            "International summit addresses global challenges",
            "Government releases economic recovery plan"
        ],
        "World": [
            "International leaders meet for peace talks",
            "Natural disaster strikes coastal region",
            "Global pandemic response coordinated across nations",
            "Cultural heritage site designated by UNESCO",
            "Cross-border trade agreement signed"
        ]
    }
    
    # Generate samples
    data = []
    samples_per_category = num_samples // len(CATEGORIES)
    
    for category, templates in sample_texts.items():
        for _ in range(samples_per_category):
            # Randomly pick and slightly modify template
            text = np.random.choice(templates)
            data.append({
                'text': text,
                'category': category
            })
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
    
    df.to_csv(output_file, index=False)
    logger.info(f"Sample data saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Train news classifier")
    parser.add_argument(
        '--data',
        type=str,
        help='Path to training data CSV'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='saved_models',
        help='Output directory for trained model'
    )
    parser.add_argument(
        '--model-type',
        type=str,
        default='logistic',
        choices=['logistic', 'random_forest', 'naive_bayes'],
        help='Type of classifier'
    )
    parser.add_argument(
        '--generate-sample',
        action='store_true',
        help='Generate sample training data'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=1000,
        help='Number of samples to generate'
    )
    
    args = parser.parse_args()
    
    # Generate sample data if requested
    if args.generate_sample:
        sample_file = "data/sample_training_data.csv"
        generate_sample_data(sample_file, args.sample_size)
        if not args.data:
            args.data = sample_file
    
    if not args.data:
        logger.error("No training data provided. Use --data or --generate-sample")
        return
    
    # Load data
    texts, labels = load_data(args.data)
    
    # Train model
    pipeline = train_model(texts, labels, args.model_type)
    
    # Save model
    save_model(pipeline, args.output)
    
    logger.info("✅ Training complete!")


if __name__ == "__main__":
    main()
