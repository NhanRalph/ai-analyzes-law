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

4. **Cấu hình Google Service Account:**
   - Tạo Service Account tại [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Sheets API và Google Drive API
   - Tải file credentials JSON và đặt vào `credentials/credentials.json`
   - Share Google Sheet với email Service Account (quyền Editor)

## Ví dụ sử dụng

### 1. Xuất chỉ JSON
```bash
python main.py docs/luat/69_2025_QH15_603983.docx --output-json
```

### 2. Xuất chỉ Google Sheets
```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-sheets \
  --sheets-id "1PsJvspGzl0HPIu_AY2eT4HnQZOie84CpGGiwAH4NriU"
```

### 3. Xuất cả hai với tên file tùy chỉnh
```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-json \
  --output-sheets \
  --sheets-id "YOUR_SHEET_ID" \
  --json-filename "luat_69_2025"
```

### 4. Xuất với tên worksheet cụ thể
```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-sheets \
  --sheets-id "YOUR_SHEET_ID" \
  --sheet-name "Luật Hóa Chất 2025"
```

## Kết quả mẫu từ file test

File test: `docs/luat/69_2025_QH15_603983.docx`

**Thống kê:**
- ✅ Tổng số entries: 291
- ✅ Số Chương: 7
- ✅ Số Điều: 48
- ✅ Số Khoản: 285
- ✅ Số Điểm: 126

**Output files:**
- JSON Flat: `output/luat_69_2025_flat.json`
- JSON Nested: `output/luat_69_2025_nested.json`
- Google Sheets: Link được hiển thị sau khi export

## Troubleshooting

### "externally-managed-environment"
→ Sử dụng virtual environment (xem bước 2)

### "FileNotFoundError: credentials.json"
→ Đảm bảo file credentials.json nằm ở đúng vị trí

### "Permission denied" khi xuất Google Sheets
→ Share Sheet với email Service Account và cấp quyền Editor

### Parser không nhận diện đúng cấu trúc
→ Kiểm tra định dạng file .docx có đúng chuẩn không (Chương, Điều, Khoản, Điểm)
