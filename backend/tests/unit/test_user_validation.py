"""Test user models and schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class TestUserPasswordValidation:
    """Test password validation in user schemas."""
    
    def test_valid_strong_password(self):
        """Test that a strong password passes validation."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongP@ssw0rd",
            "full_name": "Test User"
        }
        user = UserCreate(**user_data)
        assert user.password == "StrongP@ssw0rd"
    
    def test_password_too_short(self):
        """Test that short passwords are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "Short1!",
            "full_name": "Test User"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "at least 8 characters" in str(exc_info.value)
    
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "lowercase123!",
            "full_name": "Test User"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "uppercase letter" in str(exc_info.value)
    
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "UPPERCASE123!",
            "full_name": "Test User"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "lowercase letter" in str(exc_info.value)
    
    def test_password_no_digit(self):
        """Test that passwords without digits are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "NoDigits!@#",
            "full_name": "Test User"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "digit" in str(exc_info.value)
    
    def test_password_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "NoSpecial123",
            "full_name": "Test User"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "special character" in str(exc_info.value)
    
    def test_common_password_rejected(self):
        """Test that common passwords are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "too common" in str(exc_info.value).lower()


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test that passwords are hashed correctly."""
        password = "TestP@ssw0rd"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")
    
    def test_password_verification(self):
        """Test that password verification works."""
        password = "TestP@ssw0rd"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that same password generates different hashes (salt)."""
        password = "TestP@ssw0rd"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestUserUpdate:
    """Test user update schema validation."""
    
    def test_update_with_valid_password(self):
        """Test updating user with valid password."""
        update_data = {
            "password": "NewStrongP@ss1"
        }
        user_update = UserUpdate(**update_data)
        assert user_update.password == "NewStrongP@ss1"
    
    def test_update_without_password(self):
        """Test updating user without changing password."""
        update_data = {
            "full_name": "Updated Name"
        }
        user_update = UserUpdate(**update_data)
        assert user_update.password is None
        assert user_update.full_name == "Updated Name"
    
    def test_update_with_weak_password(self):
        """Test that weak passwords are rejected on update."""
        update_data = {
            "password": "weak"
        }
        with pytest.raises(ValidationError):
            UserUpdate(**update_data)
