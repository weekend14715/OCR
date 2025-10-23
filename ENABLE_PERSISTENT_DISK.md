# ✅ PERSISTENT DISK ĐÃ MUA - HƯỚNG DẪN KÍCH HOẠT

## 🎯 **TÌNH TRẠNG HIỆN TẠI**

✅ **Đã mua disk:** 5 GB tại `/var/data`  
✅ **Code đã sẵn sàng:** Auto-detect disk (app.py line 50-56)  
⏳ **Cần làm:** Redeploy để service nhận disk mới

---

## 🚀 **CÁCH 1: AUTO REDEPLOY (ĐỢI RENDER TỰ DEPLOY)**

Render sẽ **tự động redeploy** khi bạn add disk (mất ~2-3 phút).

### **Kiểm tra:**

1. Vào Render Dashboard → Service "OCR"
2. Tab **"Events"** → Xem có deploy mới không
3. Nếu thấy "**Disk added**" → **Đang deploy** ✅

**Wait ~3 minutes** → XONG!

---

## 🚀 **CÁCH 2: MANUAL REDEPLOY (NHANH HƠN - 30 GIÂY)**

Nếu không thấy auto-deploy, trigger manually:

### **Bước 1: Vào Render Dashboard**
```
https://dashboard.render.com
→ Chọn service "OCR" (srv-d3s5gqmr433s73ci53l0)
```

### **Bước 2: Manual Deploy**
```
Click button "Manual Deploy" (góc phải trên)
→ Chọn "Deploy latest commit"
→ Click "Deploy"
```

### **Bước 3: Đợi Deploy**
```
Wait ~2-3 minutes
Xem logs trong tab "Logs"
```

---

## 🔍 **VERIFY DISK HOẠT ĐỘNG**

### **Kiểm tra trong Logs:**

Sau khi deploy xong, check logs phải thấy:

```
[CONFIG] 💾 Using persistent storage: /var/data/licenses.db
[INIT-DB] 🔧 Initializing database at: /var/data/licenses.db
✓ Database initialized
[STARTUP] ✅ Database auto-initialized
```

### **✅ THÀNH CÔNG nếu thấy:**
```
💾 Using persistent storage: /var/data/licenses.db
```

### **❌ THẤT BẠI nếu thấy:**
```
📁 Using local storage: licenses.db  ← CHƯA DÙNG DISK!
```

---

## 🧪 **TEST DISK (SAU KHI DEPLOY XONG)**

### **Test 1: Tạo License Key**

```powershell
# Tạo 1 license key test
curl -X POST https://ocr-uufr.onrender.com/api/admin/generate `
  -H "X-Admin-Key: your-admin-key" `
  -H "Content-Type: application/json" `
  -d '{"plan_type": "lifetime", "quantity": 1, "email": "test@example.com"}'
```

**Response:**
```json
{
  "success": true,
  "licenses": ["XXXX-XXXX-XXXX-XXXX"],
  "plan": "lifetime",
  "quantity": 1
}
```

### **Test 2: Trigger Deploy Lại**

```
Manual Deploy lần nữa (để test data không mất)
```

### **Test 3: Kiểm tra License Còn Tồn Tại**

```powershell
curl -H "X-Admin-Key: your-admin-key" `
  https://ocr-uufr.onrender.com/api/admin/licenses
```

**✅ THÀNH CÔNG:** Nếu license vẫn còn sau khi deploy  
**❌ THẤT BẠI:** Nếu license mất → disk chưa hoạt động

---

## 🛠️ **TROUBLESHOOTING**

### **Problem 1: Logs vẫn hiện "local storage"**

**Nguyên nhân:** Disk chưa được mount

**Fix:**
```
1. Vào tab "Disks" → Verify disk status = "Ready"
2. Check "Mount Path" = "/var/data" (chính xác)
3. Manual Deploy lại
```

---

### **Problem 2: Deploy failed**

**Nguyên nhân:** Disk permission issue

**Fix:**
```
Code đã có fallback, sẽ dùng ephemeral storage tạm
→ Contact Render Support để check disk mount
```

---

### **Problem 3: Database empty sau deploy**

**Nguyên nhân:** 
- Lần đầu mount disk → database mới (rỗng)
- Nếu có data cũ → cần migrate

**Fix:**
```
Đây là lần đầu dùng disk → database rỗng là ĐÚNG!
Từ giờ, data sẽ được lưu persistent
```

---

## 📊 **CHECK DATABASE SIZE**

Sau khi dùng được vài ngày, check database size:

### **API Endpoint (cần thêm):**

Add vào `app.py`:

```python
@app.route('/api/admin/disk-stats', methods=['GET'])
@require_admin_key
def disk_stats():
    """Check disk usage"""
    import os
    
    try:
        db_size = os.path.getsize(DATABASE)
        db_size_mb = db_size / (1024 * 1024)
        
        # Get disk info (Linux only)
        import shutil
        if DATABASE.startswith('/var/data'):
            total, used, free = shutil.disk_usage('/var/data')
            disk_info = {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'usage_percent': round((used / total) * 100, 1)
            }
        else:
            disk_info = None
        
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
            'database_path': DATABASE,
            'database_size_mb': round(db_size_mb, 2),
            'database_size_gb': round(db_size_mb / 1024, 3),
            'license_count': license_count,
            'order_count': order_count,
            'validation_log_count': log_count,
            'disk_info': disk_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### **Test:**
```powershell
curl -H "X-Admin-Key: your-admin-key" `
  https://ocr-uufr.onrender.com/api/admin/disk-stats
```

**Response:**
```json
{
  "database_path": "/var/data/licenses.db",
  "database_size_mb": 0.05,
  "database_size_gb": 0.0,
  "license_count": 10,
  "order_count": 10,
  "validation_log_count": 150,
  "disk_info": {
    "total_gb": 5.0,
    "used_gb": 0.1,
    "free_gb": 4.9,
    "usage_percent": 2.0
  }
}
```

---

## ✅ **CHECKLIST HOÀN THÀNH**

```
☑️ 1. Đã mua disk 5GB tại mount path /var/data
☑️ 2. Đợi auto-redeploy hoặc manual deploy
☑️ 3. Check logs thấy "Using persistent storage: /var/data/licenses.db"
☑️ 4. Test tạo license key
☑️ 5. Redeploy lại → license vẫn còn (không mất)
☑️ 6. (Optional) Add API endpoint check disk stats
```

---

## 🎉 **XONG RỒI!**

**Từ giờ:**
- ✅ License keys được lưu trong `/var/data/licenses.db`
- ✅ Deploy bao nhiêu lần cũng KHÔNG MẤT DATA
- ✅ Database persistent, an toàn
- ✅ Capacity: 5 GB (đủ cho 5000+ licenses)

**Chi phí:**
```
Render Starter:     $7.00/month
Disk 5GB:          $1.25/month
─────────────────────────────────
TOTAL:             $8.25/month (~200k VND)
```

---

## 📝 **NEXT STEPS (TÙY CHỌN)**

### **1. Add Monitoring Endpoint**

Add API endpoint để check disk stats (code ở trên)

### **2. Setup Backup**

Backup database định kỳ:
```python
# backup_db.py
import shutil
import datetime

backup_name = f"licenses_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy('/var/data/licenses.db', f'/var/data/backups/{backup_name}')
```

### **3. Cleanup Old Logs**

Sau 1 năm, setup auto-cleanup:
```python
# cleanup.py
def cleanup_old_logs(days=365):
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    conn = sqlite3.connect('/var/data/licenses.db')
    c = conn.cursor()
    c.execute('DELETE FROM validation_logs WHERE timestamp < ?', (cutoff,))
    c.execute('VACUUM')
    conn.commit()
    conn.close()
```

---

**YÊU CẦU NGAY:** Chỉ cần **đợi deploy xong** hoặc **manual deploy** → XONG! 🚀

