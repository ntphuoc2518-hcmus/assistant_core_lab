# Academic Assistant MVP (`v0.7-mvp`)

Hệ thống trợ lý học vụ gồm **2 tiến trình chạy song song**, tách biệt hoàn toàn giữa giao diện người dùng và dịch vụ xử lý nghiệp vụ:
- **Backend API (`FastAPI`):** Chạy mặc định tại `http://127.0.0.1:8000` (Swagger Docs: `http://127.0.0.1:8000/docs`).
- **Frontend UI (`Streamlit`):** Chạy mặc định tại `http://localhost:8501`, giao tiếp với Backend qua HTTP/JSON.

---

## 1. Cài đặt môi trường

### Windows (PowerShell)
```powershell
# 1. Clone repository và di chuyển vào thư mục gốc dự án
git clone [https://github.com/ntphuoc2518-hcmus/assistant_core_lab.git](https://github.com/ntphuoc2518-hcmus/assistant_core_lab.git)
cd assistant_core_lab

# 2. Tạo và kích hoạt môi trường ảo
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Cài đặt thư viện phụ thuộc và gói cục bộ ở chế độ editable
pip install -r requirements.txt
pip install -e .
@'
# Academic Assistant MVP (`v0.7-mvp`)

Hệ thống trợ lý học vụ gồm **2 tiến trình chạy song song**, tách biệt hoàn toàn giữa giao diện người dùng và dịch vụ xử lý nghiệp vụ:
- **Backend API (`FastAPI`):** Chạy mặc định tại `http://127.0.0.1:8000` (Swagger Docs: `http://127.0.0.1:8000/docs`).
- **Frontend UI (`Streamlit`):** Chạy mặc định tại `http://localhost:8501`, giao tiếp với Backend qua HTTP/JSON.

---

## 1. Cài đặt môi trường

### Windows (PowerShell)
```powershell
# 1. Clone repository và di chuyển vào thư mục gốc dự án
git clone [https://github.com/ntphuoc2518-hcmus/assistant_core_lab.git](https://github.com/ntphuoc2518-hcmus/assistant_core_lab.git)
cd assistant_core_lab

# 2. Tạo và kích hoạt môi trường ảo
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Cài đặt thư viện phụ thuộc và gói cục bộ ở chế độ editable
pip install -r requirements.txt
pip install -e .
```

### macOS / Linux (Bash / Zsh)
```bash
# 1. Clone repository và di chuyển vào thư mục gốc dự án
git clone [https://github.com/ntphuoc2518-hcmus/assistant_core_lab.git](https://github.com/ntphuoc2518-hcmus/assistant_core_lab.git)
cd assistant_core_lab

# 2. Tạo và kích hoạt môi trường ảo
python3 -m venv .venv
source .venv/bin/activate

# 3. Cài đặt thư viện phụ thuộc và gói cục bộ ở chế độ editable
pip install -r requirements.txt
pip install -e .
```

---

## 2. Cấu hình biến môi trường (`.env`)

Tạo tệp `.env` từ tệp mẫu `.env.example` ở thư mục gốc (**tuyệt đối không commit tệp `.env` lên Git**):

- **Windows PowerShell:**
  ```powershell
  Copy-Item .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

Kiểm tra và điền các biến môi trường cốt lõi trong `.env`:
- `SESSION_SALT`: Chuỗi bí mật (salt) dùng để băm SHA-256 `session_id` trước khi lưu xuống SQLite nhằm bảo vệ dữ liệu định danh người dùng.
- `ASSISTANT_API_URL`: Địa chỉ endpoint của Backend API để giao diện Streamlit kết nối tới (mặc định: `http://127.0.0.1:8000`).
- `ASSISTANT_DATA_DIR`: Đường dẫn thư mục dữ liệu học vụ (`offices.csv`, tài liệu sổ tay).
- `LLM_PROVIDER` / `API_ADMIN_KEY`: Cấu hình nhà cung cấp mô hình ngôn ngữ và khóa quản trị cho các endpoint admin.

---

## 3. Khởi chạy hệ thống (2 Terminal độc lập)

Đứng tại **thư mục gốc repository** và kích hoạt sẵn `.venv` ở cả hai cửa sổ terminal:

### Terminal 1 — Khởi chạy Backend API (Cổng `8000`)
```powershell
uvicorn assistant_api.main:create_app --factory
```
Kiểm tra nhanh backend hoạt động bằng cách mở `http://127.0.0.1:8000/docs` hoặc `http://127.0.0.1:8000/health`.

### Terminal 2 — Khởi chạy Frontend UI (Cổng `8501`)
```powershell
streamlit run ui/app.py
```
Trình duyệt sẽ tự động mở giao diện tại `http://localhost:8501`.

---

## 4. Xử lý sự cố thường gặp (Troubleshooting)

### Lỗi `WinError 10013` (Cổng `8000` bị Windows chặn hoặc chiếm dụng)
- **Triệu chứng:** Khi chạy `uvicorn`, Windows báo lỗi `[Errno 10013] An attempt was made to access a socket in a way forbidden by its access permissions`.
- **Cách khắc phục (2 bước):**
  1. **Terminal 1:** Khởi chạy Backend sang cổng `8080`:
     ```powershell
     uvicorn assistant_api.main:create_app --factory --port 8080
     ```
  2. **Terminal 2:** Cập nhật `ASSISTANT_API_URL=http://127.0.0.1:8080` trong tệp `.env` (hoặc gán biến tạm trong phiên terminal hiện tại) rồi chạy lại UI:
     - *Windows PowerShell:*
       ```powershell
       $env:ASSISTANT_API_URL = "[http://127.0.0.1:8080](http://127.0.0.1:8080)"
       streamlit run ui/app.py
       ```
     - *macOS / Linux:*
       ```bash
       ASSISTANT_API_URL=[http://127.0.0.1:8080](http://127.0.0.1:8080) streamlit run ui/app.py
       ```

### PowerShell chặn chạy script kích hoạt `.venv`
- **Triệu chứng:** Lỗi `Activate.ps1 cannot be loaded because running scripts is disabled on this system`.
- **Khắc phục:** Chạy lệnh cấp quyền thực thi script cho tài khoản hiện tại rồi kích hoạt lại `.venv`:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  .\.venv\Scripts\Activate.ps1
  ```

### Lỗi `ModuleNotFoundError: No module named 'assistant_core'` hoặc `'ui'`
- **Khắc phục:** Đảm bảo bạn đã kích hoạt đúng `.venv`, đang đứng tại **thư mục gốc repository** (nơi chứa `pyproject.toml` và thư mục `ui/`) và đã chạy lệnh `pip install -e .`.

### Giao diện hiển thị cảnh báo không kết nối được Backend
- **Khắc phục:** Kiểm tra Terminal 1 xem `uvicorn` đã khởi động thành công chưa và đối chiếu cổng của `uvicorn` với giá trị `ASSISTANT_API_URL` trong `.env`.
