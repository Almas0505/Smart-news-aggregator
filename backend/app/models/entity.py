"""Entity model for Named Entity Recognition."""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.core.constants import EntityType

if TYPE_CHECKING:
    from app.models.news import News


class Entity(Base, TimestampMixin):
    """Named entity extracted from news."""
    
    __tablename__ = "entities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    entity_type: Mapped[EntityType] = mapped_column(
        SQLEnum(EntityType),
        nullable=False,
        index=True
    )
    
    entity_text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    news: Mapped["News"] = relationship(
        "News",
        back_populates="entities"
    )
    
    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, type={self.entity_type}, text={self.entity_text})>"
