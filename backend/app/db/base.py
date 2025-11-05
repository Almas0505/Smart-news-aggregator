"""Import all models for Alembic."""

from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.source import Source
from app.models.tag import Tag
from app.models.news import News
from app.models.entity import Entity
from app.models.bookmark import Bookmark
from app.models.comment import Comment
from app.models.user_preference import UserPreference
from app.models.reading_history import ReadingHistory

# This allows Alembic to discover all models
__all__ = [
    "Base",
    "User",
    "Category",
    "Source",
    "Tag",
    "News",
    "Entity",
    "Bookmark",
    "Comment",
    "UserPreference",
    "ReadingHistory",
]
