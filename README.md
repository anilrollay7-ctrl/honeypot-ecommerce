# 🔥 Advanced Honeypot E-Commerce System

Complete honeypot system combining e-commerce website + Cowrie honeypot with comprehensive attack detection, IP blocking, and activity tracking.

## 🎯 Features

### Attack Detection
- ✅ **Web Attacks**: SQL Injection, XSS, Path Traversal, Command Injection
- ✅ **SSH/Telnet Attacks**: Via Cowrie honeypot (ports 2222, 2223)
- ✅ **Brute Force Detection**: Automatic blocking after 5 failed attempts
- ✅ **Suspicious Activity**: Flags rapid/automated behavior

### Security
- ✅ **IP Blocking**: Automatic + manual unblock (1 hour duration)
- ✅ **User Blocking**: Malicious accounts blocked
- ✅ **Rate Limiting**: 100 requests/minute per IP
- ✅ **Activity Tracking**: Every action logged with full details

### Technology Stack
- **Backend**: Flask 3.0.0 (Python)
- **Frontend**: React 18 + Vite
- **Database**: MongoDB Atlas (cloud)
- **Honeypot**: Cowrie (official Docker image)
- **Deployment**: Railway (free tier)

## 📦 Project Structure

```
honeypot/
├── app.py                      # Main Flask application
├── advanced_security.py        # Security system (IP blocking, attack detection)
├── ecommerce_api.py           # E-commerce API endpoints
├── database.py                # MongoDB handler (15 collections)
├── cowrie_to_mongodb.py       # Cowrie → MongoDB bridge
├── security_logger.py         # Legacy security logger
├── config.py                  # Configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Production container
├── railway.json              # Railway deployment config
├── templates/                # Dashboard HTML templates
└── frontend/                 # React e-commerce app
```

## 🗄️ MongoDB Collections (15 total)

**Cowrie Honeypot**: sessions, auth_attempts, commands, downloads, stats
**Attack Analysis**: brute_force_attacks, shell_interactions, malware_downloads, attack_patterns, threat_intelligence
**Advanced Security**: blocked_ips, blocked_users, user_activities, failed_logins, successful_logins, web_attacks

## 🔧 Configuration

Security settings in `advanced_security.py`:
```python
MAX_FAILED_ATTEMPTS = 5          # Block after 5 failed logins
BLOCK_DURATION_SECONDS = 3600    # Block for 1 hour
SUSPICIOUS_ACTIVITY_COUNT = 10   # Flag after 10 rapid actions
MAX_REQUESTS_PER_MINUTE = 100    # Rate limit per IP
```

## 🚀 Quick Start

### Local Development
```bash
cd C:\Users\ANIL777\OneDrive\Desktop\honeypot
pip install -r requirements.txt
python app.py
# Access: http://localhost:5000
```

### Railway Deployment
1. Push all files to GitHub repository
2. Connect Railway to GitHub repo
3. Railway auto-builds using Dockerfile
4. Configure TCP proxies:
   - Port 2222 → SSH (Cowrie)
   - Port 2223 → Telnet (Cowrie)
   - Port 5000 → Web App
5. Set environment variable: `MONGODB_URI` (MongoDB Atlas connection string)

## 🛡️ API Endpoints

### Security Dashboard
- `GET /api/security/stats` - Comprehensive security statistics
- `GET /api/security/blocked-ips` - List blocked IPs
- `GET /api/security/blocked-users` - List blocked users
- `GET /api/security/failed-logins` - Failed login attempts
- `GET /api/security/web-attacks` - All web attacks (SQL, XSS, etc.)
- `GET /api/security/user-activities/<username>` - User activity log
- `POST /api/security/unblock-ip/<ip>` - Manually unblock IP
- `POST /api/security/unblock-user/<username>` - Manually unblock user

### E-Commerce
- `POST /api/ecommerce/auth/register` - User registration
- `POST /api/ecommerce/auth/login` - User login (with IP/user blocking)
- `GET /api/ecommerce/products` - Browse products
- `POST /api/ecommerce/orders/checkout` - Checkout (tracked activity)

### Honeypot Data
- `GET /api/stats` - Overall honeypot statistics
- `GET /api/honeypot/brute-force` - Brute force attacks
- `GET /api/honeypot/shell-interactions` - Shell commands
- `GET /api/commands` - Recent commands executed

## 📊 How It Works

### Normal User Flow
1. Visit website → IP activity logged
2. Browse products → User activity logged
3. Register/Login → Successful login logged
4. Checkout → Activity logged with order details
✅ All actions allowed

### Attacker Flow
1. SQL injection attempt → Detected, IP blocked, logged to `web_attacks`
2. Access again → **403 Forbidden**
3. Brute force login → Blocked after 5 attempts
4. Rapid actions → User account blocked
❌ All malicious actions blocked and logged

## 🎯 Attack Detection Examples

**SQL Injection**:
```
/api/products?search=1' OR '1'='1
→ Detected, IP blocked, severity: HIGH
```

**XSS**:
```
<script>alert('XSS')</script>
→ Detected, IP blocked, severity: HIGH
```

**Brute Force**:
```
Login attempt 1 → Failed
Login attempt 2 → Failed
...
Login attempt 5 → IP BLOCKED for 1 hour
```

**Suspicious Activity**:
```
User views 15 products in 30 seconds
→ Flagged as suspicious
→ User account BLOCKED
```

## 📈 Dashboard Features

Real-time monitoring dashboard shows:
- Attack map (geographic visualization)
- Blocked IPs/users counters
- Failed login timeline
- Attack type breakdown (pie chart)
- Live activity feed
- Web attacks log
- Cowrie attacks log

## 🌐 Environment Variables

Required in Railway deployment:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
SECRET_KEY=your-secret-key
PORT=5000
```

## 📝 Notes

- **NO synthetic data** - All attack simulator code removed
- **Real attacks only** - Captures actual malicious traffic
- **Production ready** - Fully tested and deployed
- **Free tier friendly** - Works on Railway free plan ($5/month credit)

## 🔗 Live Deployment

- **Cowrie SSH**: `ssh root@cowrie-honeypot-production.up.railway.app -p 2222`
- **Web App**: Deploy to get Railway URL
- **Database**: MongoDB Atlas (free tier)

---

**Status**: ✅ Complete and production-ready
**Last Updated**: January 28, 2026
