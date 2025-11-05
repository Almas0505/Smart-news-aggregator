"""User preference model."""

from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


class UserPreference(Base, TimestampMixin):
    """User preferences for news categories."""
    
    __tablename__ = "user_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_user_category_preference"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
        comment="Interest weight (0.0 to 1.0)"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="preferences"
    )
    
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="user_preferences"
    )
    
    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, category_id={self.category_id}, weight={self.weight})>"
