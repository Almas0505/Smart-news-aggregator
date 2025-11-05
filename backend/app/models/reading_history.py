"""Reading history model."""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.news import News


class ReadingHistory(Base, TimestampMixin):
    """User reading history."""
    
    __tablename__ = "reading_history"
    
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
    
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    read_duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Reading duration in seconds"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reading_history"
    )
    
    news: Mapped["News"] = relationship(
        "News",
        back_populates="reading_history"
    )
    
    def __repr__(self) -> str:
        return f"<ReadingHistory(user_id={self.user_id}, news_id={self.news_id})>"
