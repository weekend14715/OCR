# 🚀 HƯỚNG DẪN MANUAL DEPLOY (30 GIÂY)

## Bước 1: Vào Render Dashboard
```
https://dashboard.render.com
→ Chọn service "OCR" 
```

## Bước 2: Click "Manual Deploy"
```
Góc phải trên → Button "Manual Deploy"
→ Chọn "Deploy latest commit"
→ Click "Deploy"
```

## Bước 3: Đợi Deploy (2-3 phút)
```
Tab "Logs" → Xem logs deploy
```

## Bước 4: Check Logs - PHẢI THẤY:
```
✅ [CONFIG] 💾 Using persistent storage: /var/data/licenses.db
✅ [INIT-DB] 🔧 Initializing database at: /var/data/licenses.db
✅ ✓ Database initialized
```

## ❌ NẾU THẤY (CHƯA DÙNG DISK):
```
❌ [CONFIG] 📁 Using local storage: licenses.db
```

**Fix:** Verify disk mount path = `/var/data` và redeploy lại

---

## ✅ XONG! DATA GIỜ KHÔNG MẤT KHI DEPLOY!

