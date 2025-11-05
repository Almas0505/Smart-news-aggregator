"""Tag model."""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.news import News


# Association table for many-to-many relationship between News and Tag
news_tags = Table(
    "news_tags",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("news.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base, TimestampMixin):
    """Tag model for categorizing news."""
    
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Relationships
    news: Mapped[List["News"]] = relationship(
        "News",
        secondary=news_tags,
        back_populates="tags"
    )
    
    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"
