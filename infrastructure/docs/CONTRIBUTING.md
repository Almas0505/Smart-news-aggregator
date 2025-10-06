# 🤝 Contributing Guide

## Welcome to Smart News Aggregator!

Thank you for your interest in contributing to Smart News Aggregator. This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, sexual orientation, disability, ethnicity, religion, or nationality.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, trolling, or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct deemed inappropriate

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL (or use Docker)
- Redis (or use Docker)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/smart-news-aggregator.git
cd smart-news-aggregator
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/original/smart-news-aggregator.git
```

### Setup Development Environment

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

#### ML Service
```bash
cd ml_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### Frontend
```bash
cd frontend
npm install
```

#### Start Services
```bash
# Use Docker Compose for dependencies
docker-compose up -d postgres redis rabbitmq elasticsearch

# Or start all services
make up
```

---

## 💻 Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### 2. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add news filtering by sentiment"
```

Commit message format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat: add sentiment analysis to news articles

- Integrate TextBlob for sentiment analysis
- Add sentiment field to News model
- Update API to return sentiment scores

Closes #123
```

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template
5. Request review

---

## 📝 Coding Standards

### Python (Backend & ML Service)

#### Style Guide
- Follow PEP 8
- Use Black for formatting
- Use flake8 for linting
- Use mypy for type checking

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/
```

#### Code Structure
```python
"""
Module docstring describing purpose.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class NewsService:
    """Service for news operations."""
    
    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db
    
    def get_news(
        self, 
        limit: int = 20, 
        category_id: Optional[str] = None
    ) -> List[News]:
        """
        Retrieve news articles.
        
        Args:
            limit: Maximum number of articles to return
            category_id: Filter by category ID
            
        Returns:
            List of news articles
            
        Raises:
            ValueError: If limit is invalid
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        query = self.db.query(News)
        
        if category_id:
            query = query.filter(News.category_id == category_id)
        
        return query.limit(limit).all()
```

#### Naming Conventions
- Classes: `PascalCase` (e.g., `NewsService`)
- Functions: `snake_case` (e.g., `get_news_by_id`)
- Variables: `snake_case` (e.g., `news_count`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_PAGE_SIZE`)

### TypeScript/JavaScript (Frontend)

#### Style Guide
- Use ESLint for linting
- Use Prettier for formatting
- Follow Airbnb style guide

```bash
# Lint
npm run lint

# Format
npm run format
```

#### Code Structure
```typescript
/**
 * NewsCard component for displaying news articles
 */
interface NewsCardProps {
  news: News;
  onBookmark?: (id: string) => void;
}

export const NewsCard: React.FC<NewsCardProps> = ({ 
  news, 
  onBookmark 
}) => {
  const handleBookmark = () => {
    onBookmark?.(news.id);
  };

  return (
    <div className="news-card">
      <h2>{news.title}</h2>
      <p>{news.summary}</p>
      <button onClick={handleBookmark}>Bookmark</button>
    </div>
  );
};
```

#### Naming Conventions
- Components: `PascalCase` (e.g., `NewsCard`)
- Functions: `camelCase` (e.g., `fetchNews`)
- Variables: `camelCase` (e.g., `newsCount`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_news_service.py

# Run integration tests
pytest tests/integration/
```

### Writing Tests

```python
import pytest
from app.services.news_service import NewsService


class TestNewsService:
    """Tests for NewsService."""
    
    def test_get_news_returns_list(self, db_session):
        """Test that get_news returns a list."""
        service = NewsService(db_session)
        result = service.get_news(limit=10)
        
        assert isinstance(result, list)
        assert len(result) <= 10
    
    def test_get_news_with_invalid_limit_raises_error(self, db_session):
        """Test that negative limit raises ValueError."""
        service = NewsService(db_session)
        
        with pytest.raises(ValueError):
            service.get_news(limit=-1)
```

### Frontend Tests

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Test Coverage

Aim for:
- Unit tests: 80%+ coverage
- Integration tests: Key user flows
- E2E tests: Critical paths

---

## 📨 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes

## Screenshots (if applicable)

## Related Issues
Closes #123
```

### Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

### After Merge

- Delete your branch
- Update your local main:
```bash
git checkout main
git pull upstream main
```

---

## 🐛 Issue Guidelines

### Before Creating an Issue

1. Search existing issues
2. Check documentation
3. Try latest version

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Docker version: [e.g. 20.10.21]
- Browser: [e.g. Chrome 120]

**Additional context**
Any other context about the problem.
```

### Feature Requests

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots.
```

---

## 📚 Documentation

### Code Documentation

- Add docstrings to all functions/classes
- Use type hints in Python
- Add JSDoc comments in TypeScript
- Keep README updated

### API Documentation

- Document new endpoints
- Include request/response examples
- Update OpenAPI/Swagger specs

### User Documentation

- Update user guides
- Add tutorials for new features
- Include screenshots/videos

---

## 🎯 Good First Issues

Looking for a place to start? Check issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in our community

---

## 📞 Getting Help

- GitHub Discussions: Ask questions
- Discord: Join our community (link)
- Email: dev@smartnews.com

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Thank You!

Thank you for contributing to Smart News Aggregator! Your efforts help make this project better for everyone.

---

**Happy Coding!** 🚀
