# 💾 Persistent Storage Setup Guide

## ⚠️ Vấn đề cũ:
- Mỗi lần deploy Render → DB bị xóa sạch ❌
- Lý do: Filesystem tạm thời, SQLite file bị mất

---

## ✅ Giải pháp: Render Disk (Persistent Storage)

### **Đã cấu hình:**

#### **1. render.yaml** ✅
```yaml
disk:
  name: license-db
  mountPath: /var/data
  sizeGB: 1  # Free tier: 1GB
```

#### **2. app.py & payos_handler.py** ✅
```python
# Auto-detect persistent disk
PERSISTENT_DIR = '/var/data'
if os.path.exists(PERSISTENT_DIR) and os.access(PERSISTENT_DIR, os.W_OK):
    DATABASE = os.path.join(PERSISTENT_DIR, 'licenses.db')
    print("[CONFIG] 💾 Using persistent storage")
else:
    DATABASE = 'licenses.db'  # Fallback for local dev
```

---

## 🚀 Deploy Instructions

### **Bước 1: Commit & Push**
```bash
git add -A
git commit -m "Add persistent storage for database"
git push
```

### **Bước 2: Tạo Disk trên Render Dashboard**

1. **Truy cập:** https://dashboard.render.com
2. **Chọn service:** `ocr-license-server`
3. **Vào tab:** **"Disks"**
4. **Click:** **"Add Disk"**
5. **Điền thông tin:**
   - **Name:** `license-db`
   - **Mount Path:** `/var/data`
   - **Size:** `1 GB` (free tier)
6. **Click:** **"Add Disk"**

### **Bước 3: Redeploy Service**

Render sẽ tự động redeploy sau khi thêm disk.

---

## 📊 Kiểm tra hoạt động

### **Check Render Logs:**
```
[CONFIG] 💾 Using persistent storage: /var/data/licenses.db
[INIT-DB] 🔧 Initializing database at: /var/data/licenses.db
✓ Database initialized
```

### **Test:**
1. Tạo license key mới
2. Deploy lại app (Manual Deploy trên Render)
3. Check lại DB → **Key vẫn còn!** ✅

---

## 📝 Lưu ý quan trọng

### **⚠️ Hạn chế của Render Disk:**

1. **Không hỗ trợ Zero-downtime Deploy**
   - Khi deploy, service sẽ tắt vài giây
   - Acceptable cho license server

2. **Chỉ 1 service có thể mount**
   - Không thể share disk giữa các service
   - OK vì chỉ có 1 web service

3. **Backup:**
   - Disk không tự backup
   - Nên export DB định kỳ qua `/api/admin/export`

### **✅ Ưu điểm:**

- ✅ **Miễn phí:** 1GB free tier
- ✅ **Đơn giản:** Không cần config phức tạp
- ✅ **Nhanh:** SQLite local file
- ✅ **Persistent:** Dữ liệu giữ lại sau deploy

---

## 🔄 Alternative: PostgreSQL (nếu cần scale)

Nếu sau này cần:
- Multi-region deployment
- Zero-downtime deploys
- Backup tự động

→ Migrate sang PostgreSQL (free 90 ngày, sau đó $7/tháng)

---

## 🧪 Local Development

Khi dev local, app tự động dùng `licenses.db` trong thư mục hiện tại.

Không cần config gì thêm! ✅

---

## 📞 Support

Nếu gặp vấn đề:
1. Check Render Logs
2. Verify disk mounted: `ls -la /var/data`
3. Check permissions: `touch /var/data/test.txt`

