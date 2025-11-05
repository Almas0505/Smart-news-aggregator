"""User service for business logic."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.constants import HTTP_404_NOT_FOUND, EMAIL_ALREADY_EXISTS


class UserService:
    """Service for user operations."""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """Create new user.
        
        Args:
            db: Database session
            user_in: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email exists
        existing_user = await UserService.get_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=EMAIL_ALREADY_EXISTS
            )
        
        # Create user
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=user_in.is_active,
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update(
        db: AsyncSession,
        user: User,
        user_in: UserUpdate
    ) -> User:
        """Update user.
        
        Args:
            db: Database session
            user: User to update
            user_in: Update data
            
        Returns:
            Updated user
        """
        update_data = user_in.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
        
        # Update fields
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User if authenticated, None otherwise
        """
        user = await UserService.get_by_email(db, email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Delete user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if deleted, False otherwise
        """
        user = await UserService.get_by_id(db, user_id)
        
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        
        return True
