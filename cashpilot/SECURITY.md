# Security Guidelines

## Overview

CashPilot handles sensitive financial data and must maintain the highest security standards. This document outlines security practices for developers and contributors.

---

## 🔒 Confidential Files

### NEVER Commit These Files:

1. **Environment Variables**
   - `.env`
   - `.env.local`
   - `.env.production`
   - Any file containing API keys or credentials

2. **Database Credentials**
   - `database.ini`
   - `db_config.json`
   - Connection strings with passwords

3. **API Keys & Secrets**
   - `secrets.json`
   - `api_keys.txt`
   - Any file with `_secret` or `_key` in the name

4. **SSL/TLS Certificates**
   - `*.pem`
   - `*.key`
   - `*.crt`
   - Private keys of any kind

5. **User Data**
   - Uploaded receipts
   - Financial records
   - Transaction history
   - Any files containing PII (Personally Identifiable Information)

---

## ✅ Safe Practices

### 1. Environment Variables

**DO:**
```bash
# Use .env for local development
DATABASE_URL=postgresql://user:pass@host:5432/db

# Access in code
import os
db_url = os.environ.get("DATABASE_URL")
```

**DON'T:**
```python
# Never hardcode credentials
db_url = "postgresql://user:mypassword@host:5432/db"  # ❌ WRONG
```

### 2. Configuration Files

**DO:**
- Use `.env.example` as a template (no real values)
- Document required environment variables
- Use different credentials for dev/staging/prod

**DON'T:**
- Commit `.env` files
- Share credentials in chat/email
- Use production credentials in development

### 3. API Keys

**DO:**
- Store in environment variables
- Rotate keys regularly (every 90 days)
- Use separate keys for each environment
- Revoke unused keys immediately

**DON'T:**
- Hardcode in source code
- Share in public repositories
- Use the same key across environments

### 4. Database Security

**DO:**
- Use SSL/TLS for connections (`sslmode=require`)
- Use strong passwords (16+ characters)
- Limit database user permissions
- Enable connection pooling with limits

**DON'T:**
- Use default passwords
- Allow public database access
- Store passwords in code
- Use root/admin accounts for applications

---

## 🛡️ Data Protection

### Sensitive Data Types

1. **Financial Data**
   - Bank account numbers
   - Transaction amounts
   - Balance information
   - Payment details

2. **Personal Information (PII)**
   - Names
   - Email addresses
   - Phone numbers
   - Physical addresses

3. **Business Data**
   - Vendor information
   - Contract terms
   - Pricing details
   - Financial projections

### Handling Guidelines

**Storage:**
- Encrypt at rest (database encryption)
- Encrypt in transit (HTTPS/TLS)
- Use secure cloud storage (Supabase with encryption)

**Access:**
- Implement role-based access control (RBAC)
- Log all access to sensitive data
- Require authentication for all endpoints

**Retention:**
- Delete data when no longer needed
- Follow data retention policies
- Provide user data export/deletion

---

## 🔐 Authentication & Authorization

### API Security

**DO:**
- Use HTTPS for all API calls
- Implement rate limiting
- Validate all inputs
- Use CORS restrictions

**DON'T:**
- Expose internal endpoints publicly
- Trust client-side validation alone
- Return detailed error messages to clients

### Session Management

**DO:**
- Use secure session tokens
- Implement session timeouts
- Invalidate sessions on logout
- Use httpOnly cookies

**DON'T:**
- Store tokens in localStorage (XSS risk)
- Use predictable session IDs
- Allow concurrent sessions without limits

---

## 🚨 Incident Response

### If Credentials Are Exposed:

1. **Immediate Actions:**
   - Revoke the exposed credentials immediately
   - Generate new credentials
   - Update all systems using the old credentials
   - Check logs for unauthorized access

2. **Investigation:**
   - Determine what was exposed
   - Identify when the exposure occurred
   - Check for any unauthorized access
   - Document the incident

3. **Prevention:**
   - Review how the exposure happened
   - Update security practices
   - Train team members
   - Implement additional safeguards

### Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email security concerns to: [security@cashpilot.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## 📋 Security Checklist

### Before Committing Code:

- [ ] No `.env` files included
- [ ] No hardcoded credentials
- [ ] No API keys in code
- [ ] No sensitive data in comments
- [ ] No database passwords
- [ ] No private keys or certificates
- [ ] No user data or PII
- [ ] `.gitignore` is up to date

### Before Deploying:

- [ ] Environment variables configured
- [ ] SSL/TLS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Error messages sanitized
- [ ] Logging configured (no sensitive data)
- [ ] Backup strategy in place

### Regular Maintenance:

- [ ] Rotate API keys (every 90 days)
- [ ] Update dependencies (monthly)
- [ ] Review access logs (weekly)
- [ ] Test backup restoration (quarterly)
- [ ] Security audit (annually)

---

## 🔧 Tools & Resources

### Security Scanning

```bash
# Check for secrets in git history
git secrets --scan

# Scan dependencies for vulnerabilities
npm audit
pip-audit

# Check for exposed credentials
truffleHog --regex --entropy=False .
```

### Environment Variable Management

```bash
# Verify .env is not tracked
git ls-files | grep .env

# Check .gitignore
git check-ignore -v .env
```

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/security)
- [Next.js Security Headers](https://nextjs.org/docs/advanced-features/security-headers)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

## 📞 Contact

For security concerns or questions:
- Email: security@cashpilot.com
- Security Team: [Your Team Contact]

---

**Remember: Security is everyone's responsibility!** 🔒

Last Updated: March 25, 2026
