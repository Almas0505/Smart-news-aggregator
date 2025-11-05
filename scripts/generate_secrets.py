#!/usr/bin/env python3
"""
Generate secure passwords and secrets for Smart News Aggregator.
Usage: python generate_secrets.py
"""

import secrets
import string


def generate_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Ensure password has at least one of each type
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]
    # Fill the rest
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    # Shuffle
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


def generate_secret_key(length=32):
    """Generate a secure secret key for JWT."""
    return secrets.token_urlsafe(length)


def main():
    print("=" * 60)
    print("🔐 SMART NEWS AGGREGATOR - Secure Secrets Generator")
    print("=" * 60)
    print()
    
    print("📋 Copy these values to your .env file:\n")
    
    print("# Database")
    print(f"POSTGRES_PASSWORD={generate_password(24)}")
    print()
    
    print("# Redis")
    print(f"REDIS_PASSWORD={generate_password(24)}")
    print()
    
    print("# Security - JWT")
    print(f"SECRET_KEY={generate_secret_key(32)}")
    print()
    
    print("# Admin User")
    print(f"FIRST_SUPERUSER_PASSWORD={generate_password(16)}")
    print()
    
    print("# RabbitMQ")
    print(f"RABBITMQ_PASSWORD={generate_password(20)}")
    print()
    
    print("# Grafana")
    print(f"GRAFANA_ADMIN_PASSWORD={generate_password(16)}")
    print()
    
    print("=" * 60)
    print("⚠️  IMPORTANT:")
    print("1. Save these passwords securely (e.g., in a password manager)")
    print("2. Never commit .env files to git")
    print("3. Use different passwords for each environment")
    print("=" * 60)


if __name__ == "__main__":
    main()
