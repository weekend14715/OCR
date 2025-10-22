# 🏗️ Architecture - License System

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIETNAMESE OCR TOOL                          │
│                    LICENSE SYSTEM                               │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│                  │         │                  │         │                  │
│  OCR Desktop App │◄───────►│  License Server  │◄───────►│    Database      │
│  (Client)        │  HTTPS  │  (Flask API)     │         │   (SQLite)       │
│                  │         │                  │         │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
        │                             │
        │                             │
        ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│  License Client  │         │   Admin Panel    │
│  Module          │         │   (Web UI)       │
│                  │         │                  │
└──────────────────┘         └──────────────────┘
```

---

## 🔄 Data Flow

### 1️⃣ License Activation Flow

```
┌────────┐                 ┌────────┐                 ┌────────┐
│  User  │                 │  App   │                 │ Server │
└───┬────┘                 └───┬────┘                 └───┬────┘
    │                          │                          │
    │  Enter License Key       │                          │
    ├─────────────────────────►│                          │
    │                          │                          │
    │                          │  POST /api/validate      │
    │                          │  {license_key, machine}  │
    │                          ├─────────────────────────►│
    │                          │                          │
    │                          │                          │  Check DB
    │                          │                          ├─────────┐
    │                          │                          │         │
    │                          │                          │◄────────┘
    │                          │                          │
    │                          │  ◄─ Valid: true         │
    │                          │     Activated!           │
    │                          │◄─────────────────────────┤
    │                          │                          │
    │                          │  Save license.dat        │
    │                          ├─────────┐                │
    │                          │         │                │
    │                          │◄────────┘                │
    │                          │                          │
    │  ✅ Activation Success   │                          │
    │◄─────────────────────────┤                          │
    │                          │                          │
```

### 2️⃣ Daily Validation Flow

```
┌────────┐                 ┌────────┐                 ┌────────┐
│  App   │                 │ Server │                 │   DB   │
└───┬────┘                 └───┬────┘                 └───┬────┘
    │                          │                          │
    │  Read license.dat        │                          │
    ├─────────┐                │                          │
    │         │                │                          │
    │◄────────┘                │                          │
    │                          │                          │
    │  POST /api/validate      │                          │
    ├─────────────────────────►│                          │
    │                          │                          │
    │                          │  Query license           │
    │                          ├─────────────────────────►│
    │                          │                          │
    │                          │  ◄─ License data        │
    │                          │◄─────────────────────────┤
    │                          │                          │
    │                          │  Check:                  │
    │                          │  - Machine ID match?     │
    │                          │  - Is active?            │
    │                          │  - Not expired?          │
    │                          ├─────────┐                │
    │                          │         │                │
    │                          │◄────────┘                │
    │                          │                          │
    │  ◄─ Valid: true/false    │                          │
    │◄─────────────────────────┤                          │
    │                          │                          │
    │  Allow/Deny OCR          │                          │
    ├─────────┐                │                          │
    │         │                │                          │
    │◄────────┘                │                          │
    │                          │                          │
```

### 3️⃣ Admin Generate License Flow

```
┌────────┐                 ┌────────┐                 ┌────────┐
│ Admin  │                 │ Server │                 │   DB   │
└───┬────┘                 └───┬────┘                 └───┬────┘
    │                          │                          │
    │  POST /admin/generate    │                          │
    │  Header: X-Admin-Key     │                          │
    │  Body: {plan, qty}       │                          │
    ├─────────────────────────►│                          │
    │                          │                          │
    │                          │  Verify API Key          │
    │                          ├─────────┐                │
    │                          │         │                │
    │                          │◄────────┘                │
    │                          │                          │
    │                          │  Generate Keys           │
    │                          │  (XXXX-XXXX-XXXX-XXXX)   │
    │                          ├─────────┐                │
    │                          │         │                │
    │                          │◄────────┘                │
    │                          │                          │
    │                          │  INSERT INTO licenses    │
    │                          ├─────────────────────────►│
    │                          │                          │
    │                          │  ◄─ Success             │
    │                          │◄─────────────────────────┤
    │                          │                          │
    │  ◄─ {licenses: [...]}    │                          │
    │◄─────────────────────────┤                          │
    │                          │                          │
    │  Copy & Send to Customer │                          │
    ├─────────┐                │                          │
    │         │                │                          │
    │◄────────┘                │                          │
    │                          │                          │
```

---

## 🗄️ Database Schema

```
┌──────────────────────────────────────────────────────┐
│                   licenses                           │
├──────────────────────────────────────────────────────┤
│ id                INTEGER PRIMARY KEY               │
│ license_key       TEXT UNIQUE (XXXX-XXXX-XXXX-XXXX) │
│ email             TEXT (customer email)             │
│ machine_id        TEXT (hashed hardware ID)         │
│ activation_date   TEXT (ISO datetime)               │
│ expiry_date       TEXT (ISO datetime or NULL)       │
│ plan_type         TEXT (lifetime/yearly/monthly)    │
│ is_active         INTEGER (0 or 1)                  │
│ created_at        TEXT (ISO datetime)               │
│ last_validated    TEXT (ISO datetime)               │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│               validation_logs                        │
├──────────────────────────────────────────────────────┤
│ id                INTEGER PRIMARY KEY               │
│ license_key       TEXT                              │
│ machine_id        TEXT (hashed)                     │
│ timestamp         TEXT (ISO datetime)               │
│ success           INTEGER (0 or 1)                  │
│ ip_address        TEXT                              │
└──────────────────────────────────────────────────────┘
```

---

## 🔐 Security Model

### Machine ID Generation

```python
Machine ID = SHA256(
    hostname + 
    MAC_address + 
    processor_info
)[:32]
```

### License Key Format

```
Format: XXXX-XXXX-XXXX-XXXX
- 16 characters (hex)
- Randomly generated
- Unique in database
```

### API Authentication

```
Admin Endpoints:
  Header: X-Admin-Key: <secret-key>
  
Public Endpoints:
  No auth required (validate endpoint)
```

---

## 📦 Components

### 1. License Server (`license_server/app.py`)

**Technology:** Flask + SQLite

**Endpoints:**
- `GET /` - Landing page
- `GET /admin` - Admin panel
- `POST /api/validate` - Validate license
- `POST /api/admin/generate` - Generate licenses
- `GET /api/admin/licenses` - List all licenses
- `POST /api/admin/deactivate` - Deactivate license
- `GET /api/admin/stats` - Statistics

### 2. License Client (`license_client.py`)

**Functions:**
- `get_machine_id()` - Get hardware fingerprint
- `validate_license()` - Validate with server
- `activate_license()` - First-time activation
- `check_license_status()` - Check current status
- `save_license_key()` - Save to local storage
- `load_license_key()` - Load from local storage

### 3. OCR App (`ocr_tool_licensed.py`)

**Integration:**
- Check license on startup
- Block OCR if invalid
- Show activation dialog
- Tray menu for license management

---

## 🌐 Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────────────────┐
│                   Internet Users                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS (Port 443)
                     │
          ┌──────────▼──────────┐
          │   Nginx/Apache      │
          │   Reverse Proxy     │
          │   SSL Termination   │
          └──────────┬──────────┘
                     │
                     │ HTTP (Port 5000)
                     │
          ┌──────────▼──────────┐
          │   Gunicorn          │
          │   WSGI Server       │
          │   4 workers         │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   Flask App         │
          │   License Server    │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   SQLite Database   │
          │   licenses.db       │
          └─────────────────────┘
```

---

## 🔄 State Machine - License States

```
    [Created]
        │
        │ Customer activates
        │
        ▼
    [Activated] ──────┐
        │             │
        │ Daily use   │ Admin deactivates
        │             │
        ▼             ▼
    [Active]      [Inactive]
        │
        │ Time passes
        │
        ▼
    [Expired] ─────► [Inactive]
```

### State Transitions:

1. **Created** → **Activated**: User enters key first time
2. **Activated** → **Active**: Validation successful
3. **Active** → **Active**: Daily validation OK
4. **Active** → **Expired**: expiry_date passed
5. **Active** → **Inactive**: Admin deactivates
6. **Expired** → **Inactive**: Cannot reactivate

---

## 📈 Scalability Considerations

### Current Design (SQLite)
- ✅ Good for: 1-10K users
- ✅ Simple setup
- ✅ No extra dependencies
- ❌ Limited concurrency

### Future Scaling (PostgreSQL/MySQL)
- ✅ Good for: 10K+ users
- ✅ Better concurrency
- ✅ Replication support
- ✅ Cloud-ready

### Migration Path:

```python
# Change in app.py:

# From:
DATABASE = 'licenses.db'
conn = sqlite3.connect(DATABASE)

# To:
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="licenses",
    user="admin",
    password="secret"
)
```

---

## 🎯 Best Practices

### 1. Security
- ✅ Never commit ADMIN_API_KEY to git
- ✅ Use environment variables in production
- ✅ Enable HTTPS in production
- ✅ Backup database regularly

### 2. Performance
- ✅ Cache validation results (5-10 min)
- ✅ Use connection pooling
- ✅ Index license_key column
- ✅ Cleanup old logs periodically

### 3. User Experience
- ✅ Clear error messages
- ✅ Offline grace period (7 days)
- ✅ Easy license transfer
- ✅ Email notifications

---

## 📊 Monitoring & Analytics

### Key Metrics to Track:

1. **License Metrics:**
   - Total licenses sold
   - Activation rate
   - Active users
   - Churn rate

2. **Technical Metrics:**
   - API response time
   - Failed validations
   - Database size
   - Server uptime

3. **Business Metrics:**
   - Revenue by plan
   - Customer LTV
   - Support tickets
   - Refund rate

---

## 🔮 Future Enhancements

1. **Features:**
   - Multi-machine licenses (family plan)
   - Subscription auto-renewal
   - Usage analytics
   - API rate limiting

2. **Security:**
   - JWT tokens
   - OAuth integration
   - 2FA for admin
   - Encrypted database

3. **Infrastructure:**
   - Redis caching
   - Load balancing
   - CDN for static files
   - Automated backups

---

**Last Updated:** 2025-01-21
**Version:** 1.0.0

