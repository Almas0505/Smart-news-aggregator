# ML Model Training

Scripts for training and managing ML models.

## 📋 Available Models

### 1. News Classifier
Categorizes news articles into 8 categories:
- Technology
- Business
- Sports  
- Entertainment
- Health
- Science
- Politics
- World

### 2. Recommendation Engine
Collaborative filtering for personalized news recommendations.

## 🚀 Quick Start

### Prerequisites

```bash
cd ml_service
pip install pandas numpy scikit-learn joblib
```

### Train News Classifier

```bash
# Generate sample data and train
python -m app.training.train_classifier --generate-sample --model-type logistic

# Train with custom data
python -m app.training.train_classifier \
    --data data/training_data.csv \
    --model-type logistic \
    --output saved_models
```

**Data Format (CSV):**
```csv
text,category
"Apple releases new iPhone...",Technology
"Stock market reaches high...",Business
"Team wins championship...",Sports
```

### Train Recommender

```bash
# Generate sample data and train
python -m app.training.train_recommender --generate-sample

# Train with custom data
python -m app.training.train_recommender \
    --data data/user_interactions.csv \
    --output saved_models
```

**Data Format (CSV):**
```csv
user_id,item_id,rating
1,42,5
1,105,4
2,42,3
```

## 📊 Model Performance

### News Classifier (Logistic Regression)

- **Accuracy:** ~85-90% (depends on training data)
- **Features:** 10,000 TF-IDF features
- **N-grams:** Unigrams + Bigrams
- **Training time:** ~30 seconds on 1000 samples

### Recommender

- **Method:** Collaborative Filtering (User-based)
- **Similarity:** Cosine similarity
- **Cold start:** Handled by item-based fallback

## 📁 Directory Structure

```
ml_service/
├── app/
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train_classifier.py       # News classifier training
│   │   └── train_recommender.py      # Recommender training
│   └── models/                        # Model implementations
├── saved_models/                      # Trained models (.pkl)
│   ├── news_classifier.pkl
│   ├── classifier_metadata.json
│   └── recommender.pkl
└── data/                              # Training data
    ├── sample_training_data.csv
    └── sample_interactions.csv
```

## 🔧 Advanced Usage

### Model Types

Classifier supports multiple algorithms:

```bash
# Logistic Regression (fast, good performance)
python -m app.training.train_classifier --model-type logistic

# Random Forest (slower, better for complex patterns)
python -m app.training.train_classifier --model-type random_forest

# Naive Bayes (very fast, baseline)
python -m app.training.train_classifier --model-type naive_bayes
```

### Hyperparameter Tuning

Edit the training scripts to adjust:

**Classifier:**
- `max_features`: Number of TF-IDF features
- `ngram_range`: (1, 1) for unigrams only, (1, 2) for unigrams + bigrams
- `min_df`: Minimum document frequency
- `max_df`: Maximum document frequency

**Recommender:**
- Similarity threshold
- Number of neighbors
- Weighting scheme

### Cross-Validation

The classifier automatically performs 5-fold cross-validation and reports scores.

## 📈 Monitoring

### Model Metrics

After training, check:
- `classifier_metadata.json` - Model configuration
- Console output - Performance metrics

### Evaluation

```python
from app.models.classifier import TfidfClassifier

classifier = TfidfClassifier()
classifier.load("saved_models/news_classifier.pkl")

text = "Apple announces new iPhone with AI features"
prediction = classifier.predict(text)
print(prediction)  # {'category': 'Technology', 'confidence': 0.95, ...}
```

## 🔄 Retraining

### When to Retrain

- New categories added
- Performance degradation
- Significant data drift
- Regular schedule (monthly recommended)

### Incremental Training

For large datasets:

```python
# Train in batches
for batch in data_batches:
    texts, labels = batch
    pipeline.partial_fit(texts, labels, classes=ALL_CLASSES)
```

## 🎯 Production Deployment

### 1. Train Model

```bash
python -m app.training.train_classifier \
    --data production_data.csv \
    --model-type logistic \
    --output saved_models/production
```

### 2. Validate

```bash
# Test predictions
python -c "
from app.models.classifier import TfidfClassifier
clf = TfidfClassifier()
clf.load('saved_models/production/news_classifier.pkl')
print(clf.predict('Test article text'))
"
```

### 3. Deploy

```bash
# Copy to production directory
cp saved_models/production/news_classifier.pkl /app/saved_models/

# Restart ML service
docker restart ml_service
```

## 📚 References

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [TF-IDF Explained](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Collaborative Filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)

## 🐛 Troubleshooting

### Out of Memory

Reduce `max_features` or process in batches.

### Poor Performance

- Collect more training data
- Try different model types
- Adjust hyperparameters
- Check data quality

### Slow Training

- Use `n_jobs=-1` for parallel processing
- Reduce `max_features`
- Use simpler model (Naive Bayes)

---

**Version:** 1.0.0
**Last Updated:** November 2025
