"""Category model."""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.news import News
    from app.models.user_preference import UserPreference


class Category(Base, TimestampMixin):
    """News category model."""
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    news: Mapped[List["News"]] = relationship(
        "News",
        back_populates="category"
    )
    
    user_preferences: Mapped[List["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="category"
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"
