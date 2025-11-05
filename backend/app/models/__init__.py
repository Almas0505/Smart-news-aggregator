"""Database models."""

from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.category import Category
from app.models.source import Source
from app.models.tag import Tag, news_tags
from app.models.news import News
from app.models.entity import Entity
from app.models.bookmark import Bookmark
from app.models.comment import Comment
from app.models.user_preference import UserPreference
from app.models.reading_history import ReadingHistory

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Category",
    "Source",
    "Tag",
    "news_tags",
    "News",
    "Entity",
    "Bookmark",
    "Comment",
    "UserPreference",
    "ReadingHistory",
]
