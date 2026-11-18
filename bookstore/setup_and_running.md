# HƯỚNG DẪN CẤU HÌNH, CÀI ĐẶT & CHẠY ỨNG DỤNG
> **Dự án:** Nhà sách trực tuyến Sông Hương (`bookstore`)  
> **Hệ điều hành:** Windows (PowerShell / Command Prompt)  
> **Python:** Python 3.10+ (Đã có sẵn `.venv` tại thư mục dự án)

---

## 1. YÊU CẦU TIỀN ĐỀ (PREREQUISITES)

- Máy tính đã cài đặt Python 3.10 trở lên.
- Đã có thư mục môi trường ảo `.venv` trong `bookstore/`.
- Không cần cài đặt bất kỳ server CSDL nào vì ứng dụng sử dụng SQLite 3 (dạng file lưu trữ cục bộ).
- Không cần cài đặt Node.js hay npm vì Tailwind CSS được nạp trực tiếp qua CDN.

---

## 2. CÁC BƯỚC THIẾT LẬP CHI TIẾT (STEP-BY-STEP SETUP)

### Bước 1: Mở PowerShell và di chuyển vào thư mục dự án
```powershell
cd E:\Projects\pmnm-hocphan\bookstore
```

### Bước 2: Kích hoạt Môi trường ảo (Virtual Environment)
```powershell
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Nếu gặp lỗi Execution Policy chặn script trên PowerShell, chạy lệnh sau rồi kích hoạt lại:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
*(Khi kích hoạt thành công, đầu dòng lệnh sẽ xuất hiện tiền tố `(.venv)`)*

### Bước 3: Cài đặt các gói phụ thuộc (Dependencies)
Tạo file `requirements.txt` (nếu chưa có) với nội dung:
```text
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
flask-wtf>=1.2.0
email-validator>=2.0.0
werkzeug>=3.0.0
Pillow>=10.0.0
```
Sau đó tiến hành cài đặt:
```powershell
pip install -r requirements.txt
```

### Bước 4: Khởi tạo Database Migration & CSDL SQLite
Dự án áp dụng **Flask-Migrate (Alembic)** theo chuẩn kiến thức Chương 6:
```powershell
# 1. Nâng cấp cấu trúc CSDL theo migration hiện tại
flask --app app db upgrade

# 2. Đổ dữ liệu mẫu mô phỏng theo đúng slide bài giảng (đầu sách, danh mục, đơn hàng mẫu)
python seed.py
```
> Thư mục `migrations/` đã được khởi tạo và lưu lịch sử các bảng: `categories`, `books`, `orders`, `order_items`, `order_status_history`.

#### Khi chỉnh sửa / thêm trường mới trong `models.py`:
Mỗi khi bạn sửa model (ví dụ thêm cột mới cho `Book` hoặc `Order`):
```powershell
# Sinh script migration mới tự động phát hiện thay đổi
flask --app app db migrate -m "Mô tả thay đổi"

# Áp dụng thay đổi vào file CSDL SQLite mà KHÔNG làm mất dữ liệu cũ
flask --app app db upgrade

# Xem phiên bản migration hiện tại
flask --app app db current
```

### Bước 5: Khởi chạy Ứng dụng Flask
```powershell
python app.py
```
Hoặc dùng lệnh Flask CLI:
```powershell
$env:FLASK_APP = "app.py"
$env:FLASK_DEBUG = "1"
flask run --port 5000
```

---

## 3. CÁC ĐỊA CHỈ TRUY CẬP HỆ THỐNG

Sau khi server khởi động thành công tại `http://127.0.0.1:5000/`:

| Phân hệ | Đường dẫn (URL) | Mô tả |
| :--- | :--- | :--- |
| **Trang chủ / Danh sách sách** | `http://127.0.0.1:5000/` hoặc `/books` | Màn hình ①: Xem, tìm kiếm sách, lọc danh mục, thêm giỏ |
| **Giỏ hàng** | `http://127.0.0.1:5000/cart` | Màn hình ③: Xem giỏ hàng, cập nhật số lượng, xóa |
| **Thanh toán** | `http://127.0.0.1:5000/checkout` | Màn hình ④: Điền thông tin giao hàng & chốt đơn |
| **Dashboard Quản trị** | `http://127.0.0.1:5000/admin` | Màn hình ⑥: Tổng quan 4 KPI cards, chart, đơn mới |
| **Quản lý sách (Admin)** | `http://127.0.0.1:5000/admin/books` | Màn hình ⑦: Danh sách sách, lọc tồn kho, phân trang |
| **Thêm sách mới (Admin)** | `http://127.0.0.1:5000/admin/books/new` | Màn hình ⑧: Form thêm sách và upload ảnh bìa |
| **Quản lý danh mục (Admin)** | `http://127.0.0.1:5000/admin/categories` | Màn hình ⑨: Bảng danh mục & Form thêm mới |
| **Quản lý đơn hàng (Admin)** | `http://127.0.0.1:5000/admin/orders` | Màn hình ⑩: Tabs lọc trạng thái, tìm đơn |

---

## 4. XỬ LÝ SỰ CỐ PHỔ BIẾN (TROUBLESHOOTING)

1. **Lỗi `cannot be loaded because running scripts is disabled on this system` khi kích hoạt virtualenv:**
   - **Cách khắc phục:** Chạy lệnh `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` trong phiên PowerShell hiện tại rồi gõ lại lệnh `.venv\Scripts\Activate.ps1`.
2. **Lỗi `sqlite3.OperationalError: no such table`: CSDL chưa có bảng:**
   - **Cách khắc phục:** Chạy `python seed.py` để script tự động tạo toàn bộ cấu trúc bảng và nạp dữ liệu mẫu ban đầu.
3. **Lỗi upload ảnh bìa không hiển thị:**
   - **Cách khắc phục:** Kiểm tra thư mục `static/uploads/books/` đã được tạo hay chưa. Hệ thống tự động gọi `os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)` khi khởi động `app.py`.
4. **Lỗi `CSRF token missing or invalid` khi submit form:**
   - **Cách khắc phục:** Trong mọi form POST, đảm bảo đã đưa thẻ `{{ form.hidden_tag() }}` hoặc `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` vào bên trong `<form method="POST">`.
