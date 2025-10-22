# 🚀 FORCE REDEPLOY TRÊN RENDER

## CÁCH 1: Manual Deploy (Nhanh nhất)

1. Vào **Render Dashboard** → Chọn service `ocr-uufr`
2. Click nút **"Manual Deploy"** ở góc trên bên phải
3. Chọn **"Deploy latest commit"**
4. Đợi 2-3 phút

## CÁCH 2: Trigger Deploy bằng Git (Empty Commit)

Chạy lệnh sau trong terminal local:

```bash
git commit --allow-empty -m "trigger redeploy"
git push origin main
```

## SAU ĐÓ:

Vào **Logs** tab và tìm dòng:
```
[OK] Email config loaded from environment variable (2 accounts)
```

✅ Nếu thấy → OK!
❌ Nếu không → Có lỗi với biến môi trường!

