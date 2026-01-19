# Deploy SudachiPy API lên Render - Hướng dẫn Chi Tiết

## Bước 1: Chuẩn bị GitHub Repository

### 1.1. Tạo GitHub Repository mới

1. Vào https://github.com/new
2. Đặt tên: `sudachipy-api` (hoặc tên bạn muốn)
3. Chọn **Public** hoặc **Private**
4. **KHÔNG** chọn "Add a README file"
5. Click **Create repository**

### 1.2. Push code lên GitHub

Mở PowerShell tại thư mục `sudachipy-api`:

```powershell
cd d:\CODE\git\2pjp\sudachipy-api

# Khởi tạo git (nếu chưa có)
git init

# Add tất cả files
git add .

# Commit
git commit -m "Initial commit: SudachiPy FastAPI service"

# Thêm remote (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/sudachipy-api.git

# Push lên GitHub
git branch -M main
git push -u origin main
```

**Lưu ý**: Nếu git yêu cầu đăng nhập, dùng Personal Access Token thay vì password.

---

## Bước 2: Deploy lên Render

### 2.1. Đăng nhập Render

1. Vào https://render.com
2. Đăng nhập bằng GitHub account (khuyến nghị) hoặc email

### 2.2. Tạo Web Service

1. Click nút **"New +"** ở góc trên bên phải
2. Chọn **"Web Service"**

### 2.3. Connect Repository

1. Trong danh sách repo, tìm `sudachipy-api`
   - Nếu không thấy, click **"Connect account"** để kết nối thêm repos
2. Click **"Connect"** bên cạnh repository `sudachipy-api`

### 2.4. Cấu hình Web Service

Điền thông tin như sau:

**General:**

- **Name**: `sudachipy-api` (hoặc tên bạn muốn, phải unique trên Render)
- **Region**: Chọn `Singapore` (gần VN nhất) hoặc `Oregon` (free tier)
- **Branch**: `main`
- **Root Directory**: Để trống (vì code ở root của repo)
- **Environment**: Chọn **`Docker`** (QUAN TRỌNG!)
- **Docker Build Context Path**: Để trống
- **Docker Command**: Để trống (sẽ dùng CMD trong Dockerfile)

**Instance Type:**

- Chọn **`Free`** (để test, sau này có thể upgrade)

**Advanced:**

- **Auto-Deploy**: Chọn **`Yes`** (tự động deploy khi push code mới)

### 2.5. Deploy

1. Click **"Create Web Service"**
2. Render sẽ bắt đầu build và deploy
3. Đợi khoảng 3-5 phút cho quá trình build + deploy

---

## Bước 3: Kiểm tra Deploy

### 3.1. Xem Logs

1. Trong Render Dashboard, click vào service `sudachipy-api`
2. Tab **"Logs"** sẽ hiện quá trình build và deploy
3. Đợi đến khi thấy: `Application startup complete`

### 3.2. Lấy URL

1. Trong service dashboard, phần **"Your service is live at"**
2. Copy URL, dạng: `https://sudachipy-api-xxxxx.onrender.com`

### 3.3. Test API

Mở PowerShell hoặc browser:

```powershell
# Test health check (thay URL bằng URL của bạn)
curl https://sudachipy-api-xxxxx.onrender.com/health

# Test tokenize
curl -X POST https://sudachipy-api-xxxxx.onrender.com/tokenize `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"日本語を学ぶ。\"}'
```

Nếu trả về JSON → **THÀNH CÔNG!** 🎉

---

## Bước 4: Cập nhật NestJS API

### 4.1. Sửa file `.env`

Mở file `d:\CODE\git\2pjp\2pjp-api\.env` và thêm:

```env
SUDACHIPY_API_URL=https://sudachipy-api-xxxxx.onrender.com
```

**Thay `sudachipy-api-xxxxx.onrender.com` bằng URL thực tế của bạn!**

### 4.2. Restart NestJS Server

```powershell
cd d:\CODE\git\2pjp\2pjp-api

# Stop server hiện tại (Ctrl+C)
# Rồi chạy lại
npm run start:dev
```

### 4.3. Test Integration

```bash
# Test endpoint furigana
POST http://localhost:3000/contents/test/furigana
Content-Type: application/json

{
  "text": "日本語を学ぶ。"
}
```

Response phải có `tokens` từ SudachiPy API!

---

## Troubleshooting

### ❌ Build failed trên Render

- Kiểm tra **Logs** tab
- Đảm bảo `Dockerfile` đúng
- Đảm bảo chọn **Environment = Docker**

### ❌ Service timeout / not responding

- Free tier Render sleep sau 15 phút không dùng
- Lần đầu gọi sẽ mất ~30 giây để wake up
- Sau đó sẽ nhanh hơn

### ❌ CORS error từ NestJS

- Đã cấu hình CORS trong `main.py`, không cần sửa gì

### ❌ 502 Bad Gateway

- Đợi thêm vài phút, service có thể đang starting
- Check Logs xem có lỗi gì

---

## Performance Tips

### Free Tier Limitations:

- Sleep sau 15 phút không dùng
- 750 hours/month miễn phí
- Bandwidth: 100GB/month
- Build time: tối đa 15 phút

### Để service không sleep:

1. Upgrade lên **Starter plan** ($7/month)
2. Hoặc dùng cron job ping API mỗi 10 phút

### Monitoring

1. Vào Render Dashboard
2. Tab **Metrics** để xem CPU, Memory usage
3. Tab **Logs** để debug

---

## URL Sau Khi Deploy

**SudachiPy API Docs:** `https://your-service.onrender.com/docs`

Render tự động tạo Swagger UI từ FastAPI!

---

## Lệnh Hữu Ích

```powershell
# Update code và redeploy
git add .
git commit -m "Update something"
git push

# Render sẽ tự động deploy lại (nếu bật Auto-Deploy)

# Xem logs real-time
# → Vào Render Dashboard → Logs tab

# Restart service
# → Render Dashboard → Manual Deploy → Deploy latest commit
```

---

**DONE!** Giờ bạn đã có SudachiPy API chạy trên cloud rồi! 🚀
