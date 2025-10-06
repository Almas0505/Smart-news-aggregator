"""Application constants."""

from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class NewsCategory(str, Enum):
    """News categories."""
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    POLITICS = "politics"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    SCIENCE = "science"
    HEALTH = "health"
    WORLD = "world"
    LOCAL = "local"
    OTHER = "other"


class SourceType(str, Enum):
    """News source types."""
    RSS = "rss"
    API = "api"
    WEB = "web"


class SentimentType(str, Enum):
    """Sentiment types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EntityType(str, Enum):
    """Named entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    OTHER = "other"


# HTTP Status messages
HTTP_404_NOT_FOUND = "Resource not found"
HTTP_400_BAD_REQUEST = "Bad request"
HTTP_401_UNAUTHORIZED = "Not authenticated"
HTTP_403_FORBIDDEN = "Not enough permissions"
HTTP_409_CONFLICT = "Resource already exists"
HTTP_500_INTERNAL_ERROR = "Internal server error"

# Validation messages
INVALID_CREDENTIALS = "Incorrect email or password"
INACTIVE_USER = "Inactive user"
EMAIL_ALREADY_EXISTS = "Email already registered"
USERNAME_ALREADY_EXISTS = "Username already taken"

# Pagination
MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

# Cache TTL (seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour
CACHE_TTL_VERY_LONG = 86400  # 24 hours

# Rate limiting
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_PERIOD = 60  # seconds

# File upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
