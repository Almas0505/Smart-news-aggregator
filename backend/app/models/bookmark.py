"""Bookmark model."""

from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.news import News


class Bookmark(Base, TimestampMixin):
    """User bookmark for news articles."""
    
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_user_news_bookmark"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="bookmarks"
    )
    
    news: Mapped["News"] = relationship(
        "News",
        back_populates="bookmarks"
    )
    
    def __repr__(self) -> str:
        return f"<Bookmark(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"
