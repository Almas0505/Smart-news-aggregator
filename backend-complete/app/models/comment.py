"""Comment model."""

from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.news import News


class Comment(Base, TimestampMixin):
    """User comment on news articles."""
    
    __tablename__ = "comments"
    
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
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comments"
    )
    
    news: Mapped["News"] = relationship(
        "News",
        back_populates="comments"
    )
    
    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"
