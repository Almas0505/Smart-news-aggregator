# 🔐 Security Guide - Smart News Aggregator

## Overview

This document outlines security best practices and guidelines for deploying and maintaining the Smart News Aggregator platform.

---

## 🚨 Critical Security Checklist

### Before Production Deployment

- [ ] **Change ALL default passwords**
- [ ] **Generate secure SECRET_KEY**
- [ ] **Enable HTTPS/SSL certificates**
- [ ] **Configure firewall rules**
- [ ] **Set up backup strategy**
- [ ] **Enable security monitoring**
- [ ] **Review CORS settings**
- [ ] **Configure rate limiting**
- [ ] **Set up log aggregation**

---

## 🔑 Password Security

### 1. Generate Secure Passwords

Use the provided script to generate secure passwords:

```bash
cd scripts
python generate_secrets.py
```

Or manually:

```bash
# Generate SECRET_KEY (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate strong password
openssl rand -base64 24
```

### 2. Password Requirements

All user passwords MUST:
- Be at least 8 characters long
- Contain uppercase letters (A-Z)
- Contain lowercase letters (a-z)
- Contain digits (0-9)
- Contain special characters (!@#$%^&*)
- NOT be common passwords (password, 12345678, etc.)

### 3. Password Storage

- Passwords are hashed using bcrypt with salt
- Never store plain-text passwords
- Use password rotation for admin accounts
- Implement password history (prevent reuse)

---

## 🔐 Environment Variables

### Never Commit Secrets!

```bash
# Add to .gitignore
.env
.env.local
.env.*.local
*.env
```

### Required Environment Variables

#### Backend (.env)

```bash
# Database
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# Security
SECRET_KEY=<generated-secret-key-min-32-chars>

# Admin
FIRST_SUPERUSER_PASSWORD=<strong-password>
```

#### Production Values

```bash
# NEVER use these in production:
❌ SECRET_KEY=changethis
❌ POSTGRES_PASSWORD=postgres
❌ FIRST_SUPERUSER_PASSWORD=admin

# Use these instead:
✅ SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
✅ POSTGRES_PASSWORD=$(openssl rand -base64 24)
✅ FIRST_SUPERUSER_PASSWORD=$(openssl rand -base64 16)
```

---

## 🛡️ API Security

### 1. Rate Limiting

Protect against DDoS attacks:

```python
# Applied automatically to all endpoints
# Configure in .env:
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

### 2. Authentication

- JWT tokens with expiration
- Access tokens: 30 minutes
- Refresh tokens: 7 days
- Token rotation on refresh

### 3. Authorization

- Role-Based Access Control (RBAC)
- Endpoint permissions
- Resource ownership validation

### 4. Input Validation

- All inputs validated with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (output escaping)
- CSRF protection (for web forms)

---

## 🌐 CORS Configuration

### Development

```python
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### Production

```python
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]
```

**⚠️ Never use `*` (allow all) in production!**

---

## 🔒 HTTPS/SSL

### Required for Production

1. Obtain SSL certificate (Let's Encrypt recommended)
2. Configure Nginx for HTTPS
3. Redirect HTTP to HTTPS
4. Enable HSTS headers

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## 🗄️ Database Security

### 1. Connection Security

```python
# Use SSL for database connections in production
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

### 2. Access Control

- Separate database users for services
- Minimum required privileges
- No root/superuser access for apps

### 3. Backup Security

- Encrypt backups
- Secure backup storage
- Regular backup testing
- Retention policy

---

## 📊 Monitoring & Logging

### 1. Security Events to Log

- Failed login attempts
- Password changes
- Permission changes
- API rate limit hits
- Suspicious activity

### 2. Log Management

```python
# Structured logging with JSON format
LOG_FORMAT=json
LOG_LEVEL=INFO  # Use INFO in production, not DEBUG

# Never log:
❌ Passwords
❌ API keys
❌ JWT tokens
❌ Personal data (PII)
```

### 3. Monitoring Tools

- **Sentry**: Error tracking
- **Prometheus**: Metrics
- **Grafana**: Dashboards
- **ELK Stack**: Log aggregation

---

## 🚀 Deployment Security

### Docker Security

```dockerfile
# Use non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Use specific image versions (not :latest)
FROM python:3.11-slim

# Scan for vulnerabilities
docker scan smart-news-backend:latest
```

### Environment Separation

```bash
# Different environments
development  → .env.development
staging      → .env.staging
production   → .env.production
```

### Secrets Management

Consider using:
- **HashiCorp Vault**
- **AWS Secrets Manager**
- **Azure Key Vault**
- **Docker Secrets**

---

## 🔍 Security Testing

### 1. Automated Scanning

```bash
# Dependency vulnerabilities
safety check -r requirements.txt

# Code security issues
bandit -r app/

# Docker image scanning
trivy image smart-news-backend:latest
```

### 2. Penetration Testing

Regular testing for:
- SQL injection
- XSS vulnerabilities
- Authentication bypass
- Authorization flaws
- API abuse

---

## 📝 Security Incident Response

### Incident Handling

1. **Detect**: Monitor logs and alerts
2. **Contain**: Isolate affected systems
3. **Investigate**: Analyze logs and impact
4. **Remediate**: Apply fixes
5. **Document**: Record incident details
6. **Review**: Post-mortem analysis

### Emergency Contacts

- Security team: security@smartnews.com
- DevOps team: devops@smartnews.com
- On-call: +1-XXX-XXX-XXXX

---

## 🔄 Regular Security Tasks

### Daily
- [ ] Review security alerts
- [ ] Check failed login attempts

### Weekly
- [ ] Update dependencies
- [ ] Review access logs
- [ ] Backup verification

### Monthly
- [ ] Security patch updates
- [ ] Certificate expiration check
- [ ] Access review
- [ ] Password rotation (admin)

### Quarterly
- [ ] Security audit
- [ ] Penetration testing
- [ ] Policy review
- [ ] Training updates

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security](https://docs.docker.com/engine/security/)

---

## 📞 Reporting Security Issues

If you discover a security vulnerability, please email:
**security@smartnews.com**

**DO NOT** create public GitHub issues for security vulnerabilities.

---

**Last Updated**: October 2025  
**Review Schedule**: Quarterly
