# TÍNH TOÁN DATABASE SIZE CHO 5000 LICENSE KEYS

## 📊 **PHÂN TÍCH DỮ LIỆU**

### **Database Schema (SQLite)**

```sql
-- Table 1: licenses
CREATE TABLE licenses (
    id INTEGER PRIMARY KEY,           -- 8 bytes
    license_key TEXT UNIQUE,          -- ~20 bytes ("XXXX-XXXX-XXXX-XXXX")
    email TEXT,                       -- ~30 bytes average
    machine_id TEXT,                  -- 64 bytes (SHA256 hash)
    activation_date TEXT,             -- 25 bytes (ISO datetime)
    expiry_date TEXT,                 -- 25 bytes
    plan_type TEXT,                   -- 10 bytes ("lifetime")
    is_active INTEGER,                -- 4 bytes
    status TEXT,                      -- 10 bytes ("active")
    created_at TEXT,                  -- 25 bytes
    last_validated TEXT,              -- 25 bytes
    order_id TEXT                     -- 15 bytes
);

-- Table 2: orders
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,           -- 8 bytes
    order_id TEXT UNIQUE,             -- 15 bytes
    plan_type TEXT,                   -- 10 bytes
    amount INTEGER,                   -- 8 bytes
    customer_email TEXT,              -- 30 bytes
    payment_method TEXT,              -- 10 bytes ("payos")
    payment_status TEXT,              -- 10 bytes ("completed")
    transaction_id TEXT,              -- 20 bytes
    license_key TEXT,                 -- 20 bytes
    created_at TEXT,                  -- 25 bytes
    paid_at TEXT,                     -- 25 bytes
    expires_at TEXT                   -- 25 bytes
);

-- Table 3: validation_logs (nhiều nhất)
CREATE TABLE validation_logs (
    id INTEGER PRIMARY KEY,           -- 8 bytes
    license_key TEXT,                 -- 20 bytes
    machine_id TEXT,                  -- 64 bytes
    timestamp TEXT,                   -- 25 bytes
    success INTEGER,                  -- 4 bytes
    ip_address TEXT                   -- 15 bytes ("255.255.255.255")
);
```

---

## 🧮 **TÍNH TOÁN CHI TIẾT**

### **Scenario: 5,000 License Keys**

#### **1. Licenses Table**
```
Row size: ~261 bytes (bao gồm overhead)
5,000 licenses × 261 bytes = 1,305,000 bytes = ~1.25 MB
```

#### **2. Orders Table**
```
Row size: ~206 bytes
5,000 orders × 206 bytes = 1,030,000 bytes = ~1.0 MB
```

#### **3. Validation Logs** (quan trọng nhất!)

**Giả sử mỗi license validate:**
- **1 lần/ngày** (normal usage)
- **Lưu logs 1 năm**

```
Calculations:
- 5,000 licenses × 365 days = 1,825,000 validations/year
- Row size: ~136 bytes
- Total: 1,825,000 × 136 bytes = 248,200,000 bytes = ~237 MB
```

**Nếu validate nhiều hơn:**
- **5 lần/ngày** (heavy usage): ~1.16 GB/year
- **10 lần/ngày** (very heavy): ~2.32 GB/year

#### **4. SQLite Overhead & Indexes**
```
- Index for license_key: ~500 KB
- Index for email: ~500 KB  
- Index for order_id: ~500 KB
- Database overhead (fragmentation, journal): ~20%
```

---

## 📈 **TỔNG KẾT CHO 5000 LICENSES**

### **Scenario 1: Light Usage (1 validation/day, 1 year logs)**

```
Licenses table:         1.25 MB
Orders table:           1.00 MB
Validation logs:      237.00 MB (365 days)
Indexes:                1.50 MB
SQLite overhead:       48.00 MB (20%)
─────────────────────────────────
TOTAL:                ~289 MB ≈ 0.3 GB
```

**✅ Khuyến nghị: 1 GB disk** (còn dư 70% cho growth)

---

### **Scenario 2: Normal Usage (3 validations/day, 1 year logs)**

```
Licenses table:         1.25 MB
Orders table:           1.00 MB
Validation logs:      711.00 MB (3× per day)
Indexes:                1.50 MB
SQLite overhead:      142.00 MB (20%)
─────────────────────────────────
TOTAL:                ~857 MB ≈ 0.85 GB
```

**✅ Khuyến nghị: 5 GB disk** (safe buffer)

---

### **Scenario 3: Heavy Usage (10 validations/day, 1 year logs)**

```
Licenses table:         1.25 MB
Orders table:           1.00 MB
Validation logs:     2,370.00 MB (10× per day)
Indexes:                1.50 MB
SQLite overhead:      475.00 MB (20%)
─────────────────────────────────
TOTAL:               ~2.85 GB
```

**✅ Khuyến nghị: 5 GB disk** (good buffer)

---

### **Scenario 4: Very Heavy + Long-term (10 validations/day, 3 years logs)**

```
Licenses table:         1.25 MB
Orders table:           1.00 MB
Validation logs:     7,110.00 MB (3 years)
Indexes:                1.50 MB
SQLite overhead:    1,422.00 MB (20%)
─────────────────────────────────
TOTAL:               ~8.54 GB
```

**✅ Khuyến nghị: 10 GB disk**

---

## 🎯 **KHUYẾN NGHỊ CUỐI CÙNG**

### **Cho 5,000 License Keys:**

| Disk Size | Chi phí/tháng | Phù hợp với | Dự trữ |
|-----------|---------------|-------------|--------|
| **1 GB** | **$0.25** | Light usage (1 validation/day) | 70% buffer |
| **5 GB** ✅ | **$1.25** | **Normal-Heavy usage** (recommended) | **83% buffer** |
| 10 GB | $2.50 | Very heavy or long-term logs | 92% buffer |

---

## ✅ **KHUYẾN NGHỊ: 5 GB DISK**

### **Lý do:**

1. **Chi phí hợp lý:** $1.25/tháng (chỉ 30k VND)
2. **Buffer tốt:** Đủ cho heavy usage + 3-5 năm logs
3. **Không cần lo lắng:** Còn dư 83% capacity
4. **Flexible:** Có thể chạy cleanup script sau này

---

## 💰 **CHI PHÍ BREAKDOWN**

### **Total Monthly Cost:**

```
Render Starter:     $7.00/month
Persistent Disk 5GB: $1.25/month
─────────────────────────────────
TOTAL:              $8.25/month (~200k VND)
```

**vs. Nếu dùng PostgreSQL (FREE):**
```
Render Starter:     $7.00/month
PostgreSQL:         $0.00 (free tier)
─────────────────────────────────
TOTAL:              $7.00/month (~170k VND)
```

**Tiết kiệm:** $1.25/month (30k VND)

---

## 🔧 **OPTIMIZATION TIPS (SAU NÀY)**

### **1. Auto-cleanup Old Logs**

Thêm cron job để xóa logs cũ:

```python
# cleanup_old_logs.py
def cleanup_validation_logs(days_to_keep=365):
    """Xóa validation logs cũ hơn X ngày"""
    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days_to_keep)).isoformat()
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('DELETE FROM validation_logs WHERE timestamp < ?', (cutoff_date,))
    deleted = c.rowcount
    
    # Vacuum để reclaim space
    c.execute('VACUUM')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {deleted} old validation logs")
```

**Chạy mỗi tháng** → Giữ database nhỏ gọn

---

### **2. Compress Old Data**

Sau 1 năm, export logs ra JSON compressed:

```python
# Archive logs older than 1 year
def archive_old_logs():
    import gzip
    import json
    
    # Export to JSON
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat()
    c.execute('SELECT * FROM validation_logs WHERE timestamp < ?', (cutoff,))
    
    old_logs = c.fetchall()
    
    # Compress and save
    with gzip.open(f'/var/data/logs_archive_{datetime.datetime.now().year}.json.gz', 'wt') as f:
        json.dump(old_logs, f)
    
    # Delete from DB
    c.execute('DELETE FROM validation_logs WHERE timestamp < ?', (cutoff,))
    c.execute('VACUUM')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Archived {len(old_logs)} logs")
```

---

### **3. Monitoring**

Add endpoint để check database size:

```python
@app.route('/api/admin/database-stats', methods=['GET'])
@require_admin_key
def database_stats():
    """Check database size and stats"""
    import os
    
    db_size = os.path.getsize(DATABASE)
    db_size_mb = db_size / (1024 * 1024)
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM licenses')
    license_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM orders')
    order_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM validation_logs')
    log_count = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'database_size_mb': round(db_size_mb, 2),
        'database_size_gb': round(db_size_mb / 1024, 3),
        'license_count': license_count,
        'order_count': order_count,
        'validation_log_count': log_count,
        'estimated_capacity_used': f"{(db_size_mb / 5120) * 100:.1f}%"  # For 5GB disk
    })
```

---

## 📊 **COMPARISON: DISK vs POSTGRESQL**

### **Render Disk (SQLite)**

**Pros:**
- ✅ Simple setup
- ✅ No external dependencies
- ✅ Fast local access
- ✅ Single file backup

**Cons:**
- ❌ Cost $1.25/month (5GB)
- ❌ Manual scaling
- ❌ Single point of failure

---

### **PostgreSQL (Render Free)**

**Pros:**
- ✅ **FREE** (90 days, auto-renew)
- ✅ Better for concurrent writes
- ✅ More scalable
- ✅ Built-in backup/restore

**Cons:**
- ❌ Network latency (nhẹ)
- ❌ Phải migrate code (1-2 giờ)
- ❌ Phụ thuộc external service

---

## 🎯 **KẾT LUẬN**

### **Cho 5,000 licenses:**

```
╔═══════════════════════════════════════════════════╗
║  KHUYẾN NGHỊ: 5 GB DISK                          ║
║                                                   ║
║  Chi phí: $1.25/month (~30k VND)                 ║
║  Capacity: Đủ cho 3-5 năm validation logs        ║
║  Buffer: 83% dự trữ                              ║
║  Setup: 2 phút (add disk on Render)              ║
║                                                   ║
║  ✅ BEST CHOICE cho bạn!                         ║
╚═══════════════════════════════════════════════════╝
```

---

## 🚀 **HƯỚNG DẪN MUA DISK (2 PHÚT)**

### **Bước 1: Vào Render Dashboard**
```
1. Vào: https://dashboard.render.com
2. Chọn service: "OCR" (srv-d3s5gqmr433s73ci53l0)
3. Tab "Disks"
4. Click "Add Disk"
```

### **Bước 2: Configure Disk**
```
Mount Path: /var/data
Size: 5 GB
Click "Add Disk"
```

### **Bước 3: Deploy**
```
Service sẽ auto-redeploy với disk mới
Wait ~2 minutes
```

### **Bước 4: Verify**
```
Check logs:
[CONFIG] 💾 Using persistent storage: /var/data/licenses.db
```

**DONE!** 🎉

---

## 📝 **ALTERNATIVE: MIGRATE TO POSTGRESQL (FREE)**

Nếu muốn tiết kiệm $1.25/month:

### **Setup PostgreSQL (10 phút)**

1. **Create PostgreSQL database on Render (Free)**
2. **Update code:**
   - Install `psycopg2`
   - Change SQLite → PostgreSQL queries
   - Update connection string
3. **Migrate existing data** (if any)
4. **Deploy**

**Pros:** FREE forever
**Cons:** Mất 1-2 giờ để migrate code

**Code changes:** ~50 lines (tôi có thể giúp nếu bạn muốn!)

---

## 💡 **NÊN CHỌN GÌ?**

### **Chọn 5 GB Disk nếu:**
- ✅ Muốn giữ code SQLite (đơn giản)
- ✅ Không muốn migrate (mất thời gian)
- ✅ OK với $1.25/month

### **Chọn PostgreSQL nếu:**
- ✅ Muốn FREE
- ✅ Muốn scale lớn hơn sau này
- ✅ OK với việc đổi code (1-2 giờ)

---

**Theo tôi:** **5 GB Disk** = best choice cho bạn ngay bây giờ!
- Setup nhanh (2 phút)
- Chi phí rẻ ($1.25/month)
- Đủ dùng cho 5000 licenses + nhiều năm

Muốn tôi giúp setup không? 🚀

