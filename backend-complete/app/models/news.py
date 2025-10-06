"""News model."""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.core.constants import SentimentType

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.source import Source
    from app.models.tag import Tag
    from app.models.entity import Entity
    from app.models.bookmark import Bookmark
    from app.models.comment import Comment
    from app.models.reading_history import ReadingHistory


class News(Base, TimestampMixin):
    """News article model."""
    
    __tablename__ = "news"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Basic info
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # URLs
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Foreign keys
    source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # ML fields
    sentiment: Mapped[Optional[SentimentType]] = mapped_column(
        SQLEnum(SentimentType),
        nullable=True
    )
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Dates
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    
    # Stats
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bookmarks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    source: Mapped["Source"] = relationship(
        "Source",
        back_populates="news"
    )
    
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="news"
    )
    
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="news_tags",
        back_populates="news"
    )
    
    entities: Mapped[List["Entity"]] = relationship(
        "Entity",
        back_populates="news",
        cascade="all, delete-orphan"
    )
    
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark",
        back_populates="news",
        cascade="all, delete-orphan"
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="news",
        cascade="all, delete-orphan"
    )
    
    reading_history: Mapped[List["ReadingHistory"]] = relationship(
        "ReadingHistory",
        back_populates="news",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<News(id={self.id}, title={self.title[:50]})>"
