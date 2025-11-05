"""
Train Recommendation Model

Collaborative filtering model for personalized news recommendations.

Usage:
    python -m ml_service.app.training.train_recommender --data data/user_interactions.csv
"""

import argparse
import logging
from pathlib import Path
import json
import joblib

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborativeFilteringRecommender:
    """
    Simple collaborative filtering recommender.
    
    Uses user-item interaction matrix and cosine similarity.
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity = None
        self.item_similarity = None
        self.user_index = {}
        self.item_index = {}
    
    def fit(self, interactions_df: pd.DataFrame):
        """
        Train recommender on interaction data.
        
        Args:
            interactions_df: DataFrame with columns [user_id, item_id, rating]
        """
        logger.info("Building user-item matrix...")
        
        # Create user-item matrix
        self.user_item_matrix = interactions_df.pivot_table(
            index='user_id',
            columns='item_id',
            values='rating',
            fill_value=0
        )
        
        # Create indices
        self.user_index = {uid: idx for idx, uid in enumerate(self.user_item_matrix.index)}
        self.item_index = {iid: idx for idx, iid in enumerate(self.user_item_matrix.columns)}
        
        logger.info(f"Matrix shape: {self.user_item_matrix.shape}")
        
        # Compute similarities
        logger.info("Computing user similarity...")
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        
        logger.info("Computing item similarity...")
        self.item_similarity = cosine_similarity(self.user_item_matrix.T)
        
        logger.info("Training complete!")
    
    def recommend_for_user(self, user_id: int, n: int = 10) -> list:
        """
        Get top N recommendations for user.
        
        Args:
            user_id: User ID
            n: Number of recommendations
            
        Returns:
            List of (item_id, score) tuples
        """
        if user_id not in self.user_index:
            return []
        
        user_idx = self.user_index[user_id]
        
        # Get similar users
        user_similarities = self.user_similarity[user_idx]
        
        # Weighted sum of similar users' ratings
        scores = np.dot(user_similarities, self.user_item_matrix.values)
        
        # Normalize by sum of similarities
        scores = scores / (np.sum(np.abs(user_similarities)) + 1e-10)
        
        # Remove items user has already interacted with
        user_items = self.user_item_matrix.iloc[user_idx] > 0
        scores[user_items] = -np.inf
        
        # Get top N
        top_indices = np.argsort(scores)[::-1][:n]
        
        recommendations = [
            (self.user_item_matrix.columns[idx], scores[idx])
            for idx in top_indices
        ]
        
        return recommendations
    
    def similar_items(self, item_id: int, n: int = 10) -> list:
        """
        Get similar items.
        
        Args:
            item_id: Item ID
            n: Number of similar items
            
        Returns:
            List of (item_id, similarity) tuples
        """
        if item_id not in self.item_index:
            return []
        
        item_idx = self.item_index[item_id]
        similarities = self.item_similarity[item_idx]
        
        # Exclude self
        similarities[item_idx] = -np.inf
        
        top_indices = np.argsort(similarities)[::-1][:n]
        
        similar = [
            (self.user_item_matrix.columns[idx], similarities[idx])
            for idx in top_indices
        ]
        
        return similar


def load_interaction_data(file_path: str) -> pd.DataFrame:
    """Load user-item interaction data."""
    logger.info(f"Loading interactions from {file_path}")
    df = pd.read_csv(file_path)
    
    required_cols = ['user_id', 'item_id', 'rating']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV must have columns: {required_cols}")
    
    logger.info(f"Loaded {len(df)} interactions")
    logger.info(f"Users: {df['user_id'].nunique()}, Items: {df['item_id'].nunique()}")
    
    return df


def generate_sample_interactions(output_file: str, num_interactions: int = 10000):
    """Generate sample interaction data."""
    logger.info(f"Generating {num_interactions} interactions...")
    
    np.random.seed(42)
    
    num_users = 100
    num_items = 500
    
    # Generate interactions
    data = []
    for _ in range(num_interactions):
        user_id = np.random.randint(1, num_users + 1)
        item_id = np.random.randint(1, num_items + 1)
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.1, 0.2, 0.3, 0.3])
        
        data.append({
            'user_id': user_id,
            'item_id': item_id,
            'rating': rating
        })
    
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['user_id', 'item_id'])
    
    df.to_csv(output_file, index=False)
    logger.info(f"Sample data saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Train recommendation model")
    parser.add_argument('--data', type=str, help='Path to interaction data CSV')
    parser.add_argument('--output', type=str, default='saved_models', help='Output directory')
    parser.add_argument('--generate-sample', action='store_true', help='Generate sample data')
    
    args = parser.parse_args()
    
    if args.generate_sample:
        sample_file = "data/sample_interactions.csv"
        generate_sample_interactions(sample_file)
        if not args.data:
            args.data = sample_file
    
    if not args.data:
        logger.error("No data provided. Use --data or --generate-sample")
        return
    
    # Load data
    interactions = load_interaction_data(args.data)
    
    # Train model
    logger.info("Training recommender...")
    recommender = CollaborativeFilteringRecommender()
    recommender.fit(interactions)
    
    # Save model
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_file = output_path / "recommender.pkl"
    joblib.dump(recommender, model_file)
    logger.info(f"Model saved to {model_file}")
    
    logger.info("✅ Training complete!")


if __name__ == "__main__":
    main()
