"""Test security utilities."""

import pytest
from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash
)


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        user_id = "123"
        token = create_access_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user_id = "123"
        token = create_refresh_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
    
    def test_verify_valid_access_token(self):
        """Test verifying a valid access token."""
        user_id = "123"
        token = create_access_token(subject=user_id)
        
        verified_subject = verify_token(token, token_type="access")
        assert verified_subject == user_id
    
    def test_verify_valid_refresh_token(self):
        """Test verifying a valid refresh token."""
        user_id = "123"
        token = create_refresh_token(subject=user_id)
        
        verified_subject = verify_token(token, token_type="refresh")
        assert verified_subject == user_id
    
    def test_verify_wrong_token_type(self):
        """Test that wrong token type returns None."""
        user_id = "123"
        access_token = create_access_token(subject=user_id)
        
        # Try to verify access token as refresh token
        verified_subject = verify_token(access_token, token_type="refresh")
        assert verified_subject is None
    
    def test_verify_invalid_token(self):
        """Test that invalid token returns None."""
        invalid_token = "invalid.token.here"
        
        verified_subject = verify_token(invalid_token, token_type="access")
        assert verified_subject is None
    
    def test_verify_expired_token(self):
        """Test that expired token returns None."""
        user_id = "123"
        # Create token with very short expiration
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        verified_subject = verify_token(token, token_type="access")
        assert verified_subject is None
    
    def test_tokens_are_different(self):
        """Test that access and refresh tokens are different."""
        user_id = "123"
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        assert access_token != refresh_token


class TestPasswordSecurity:
    """Test password security functions."""
    
    def test_password_hashing_consistency(self):
        """Test that password hashing is consistent."""
        password = "TestPassword123!"
        
        # Hash the same password multiple times
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_wrong_password_verification(self):
        """Test that wrong password fails verification."""
        correct_password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        
        hashed = get_password_hash(correct_password)
        
        assert verify_password(correct_password, hashed) is True
        assert verify_password(wrong_password, hashed) is False
    
    def test_empty_password_hashing(self):
        """Test hashing empty password."""
        empty_password = ""
        hashed = get_password_hash(empty_password)
        
        assert hashed != empty_password
        assert verify_password(empty_password, hashed)
    
    def test_special_characters_in_password(self):
        """Test passwords with special characters."""
        special_password = "P@$$w0rd!#%&*()_+-=[]{}|;:',.<>?/~`"
        hashed = get_password_hash(special_password)
        
        assert verify_password(special_password, hashed)
        assert not verify_password("different", hashed)
