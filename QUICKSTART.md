# Quick Start Guide

## Cài đặt nhanh

1. **Clone repository hoặc tải source code**

2. **Tạo và kích hoạt virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # hoặc
   venv\Scripts\activate  # Windows
   ```

3. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình môi trường:**
   - **Google Sheets:** Tải credentials JSON từ Google Cloud Console và đặt vào `credentials/credentials.json`.
   - **Gemini AI:** 
     - Tạo file `.env` từ `.env.example`.
     - Thêm `GEMINI_API_KEY=your_key_here` vào file `.env`. (Lấy key tại [Google AI Studio](https://aistudio.google.com/))

## Ví dụ sử dụng

### 0. Chạy giao diện Web App
```bash
uvicorn web.app:app --reload
```

Mở: `http://127.0.0.1:8000`

Trên giao diện web bạn có thể:
- Đăng ký / đăng nhập bằng Firebase Auth (email/password)
- Chọn file `.docx`
- Chọn xuất `JSON` hoặc `Google Sheets`
- Chọn mode `Tool` hoặc `Tool + AI`

Biến môi trường tối thiểu cho Firebase Web/Auth:

```bash
FIREBASE_API_KEY=...
FIREBASE_AUTH_DOMAIN=...
FIREBASE_PROJECT_ID=...
FIREBASE_STORAGE_BUCKET=...
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=...
FIREBASE_SERVICE_ACCOUNT_PATH=credentials/firebase-service-account.json
```

### 1. Phân tích cơ bản (Chỉ JSON)
```bash
python main.py docs/luat/69_2025_QH15_603983.docx --output-json
```

### 2. Phân tích có sử dụng AI Classifier (Khuyên dùng)
Sử dụng AI để phân loại các điều khoản theo định nghĩa Hóa chất và Hạng mục tuân thủ.
```bash
python main.py docs/luat/69_2025_QH15_603983.docx --output-json --use-ai
```

### 3. Xuất kết quả lên Google Sheets
```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-sheets \
  --sheets-id "YOUR_SHEET_ID" \
  --use-ai
```

### 4. Xuất cả hai với tên file tùy chỉnh
```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-json \
  --output-sheets \
  --sheets-id "YOUR_SHEET_ID" \
  --json-filename "luat_69_2025" \
  --use-ai
```

## Kiểm tra AI Classifier
Để kiểm tra kết nối và khả năng phân loại của AI:
```bash
python tests/test_ai_classifier.py
```

## Kết quả đầu ra
- **Dữ liệu AI:** Xuất hiện trong cột `ai_hang_muc`, `ai_nhom_hoa_chat` trên Sheets và trong trường `ai_classification` trong JSON.
- **Tham chiếu:** File JSON output bao gồm cả danh sách các định nghĩa đã dùng trong phần `metadata.definitions`.
- **Thống kê:** Hệ thống hiển thị số lượng Điều/Khoản đã được AI phân loại thành công.

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv' (hoặc 'google')"
→ Đảm bảo bạn đã cài đặt lại thư viện: `pip install -r requirements.txt` trong virtual environment.

### AI không hoạt động / Không thấy thông tin AI
→ Đảm bảo bạn đã thêm tham số `--use-ai` trong câu lệnh chạy.

### "Permission denied" khi xuất Google Sheets
→ Share Sheet với email Service Account (trong file credentials.json) và cấp quyền Editor.

### Lỗi Quota / Rate Limit AI
→ Bản Gemini Free có giới hạn lượt gọi mỗi phút. Hệ thống tự động nghỉ 4 giây giữa các đợt phát ra yêu cầu.
