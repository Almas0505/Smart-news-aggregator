"""User model."""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.core.constants import UserRole

if TYPE_CHECKING:
    from app.models.bookmark import Bookmark
    from app.models.comment import Comment
    from app.models.user_preference import UserPreference
    from app.models.reading_history import ReadingHistory


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False
    )
    
    # Relationships
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    preferences: Mapped[List["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    reading_history: Mapped[List["ReadingHistory"]] = relationship(
        "ReadingHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
