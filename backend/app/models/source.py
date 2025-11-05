"""Source model."""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.core.constants import SourceType

if TYPE_CHECKING:
    from app.models.news import News


class Source(Base, TimestampMixin):
    """News source model."""
    
    __tablename__ = "sources"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[SourceType] = mapped_column(
        SQLEnum(SourceType),
        nullable=False
    )
    
    description: Mapped[str] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scrape_interval: Mapped[int] = mapped_column(
        Integer,
        default=3600,
        nullable=False,
        comment="Scrape interval in seconds"
    )
    
    # Relationships
    news: Mapped[List["News"]] = relationship(
        "News",
        back_populates="source"
    )
    
    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name={self.name})>"
