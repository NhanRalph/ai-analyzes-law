# LEGAL DOCUMENT PARSER

Công cụ phân tích văn bản pháp luật Việt Nam và xuất ra JSON/Google Sheets

## Tính năng

- ✅ Đọc file .docx văn bản pháp luật
- ✅ Phân tích cấu trúc: Chương, Mục, Điều, Khoản, Điểm
- ✅ Lọc bỏ phần kết luật ("Luật này được Quốc hội...")
- ✅ Xuất dữ liệu ra JSON (cả dạng phẳng và nested)
- ✅ Xuất dữ liệu lên Google Sheets với format đẹp
- ✅ Support Service Account authentication

## Cài đặt

### 1. Cài đặt Python packages

```bash
pip install -r requirements.txt
```

### 2. Cấu hình Google Service Account

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Enable Google Sheets API và Google Drive API
4. Tạo Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Tải file JSON credentials
5. Đặt file credentials vào `credentials/credentials.json`
6. Chia sẻ Google Sheet với email của Service Account (với quyền Editor)

## Sử dụng

## Web App (giao diện trực quan)

### Chạy Web App

```bash
uvicorn web.app:app --reload
```

Sau khi chạy, mở trình duyệt tại: `http://127.0.0.1:8000`

### Tính năng trên Web UI

- Upload file `.docx`
- Chọn kiểu xuất: `JSON`, `Google Sheets`, hoặc cả hai
- Chọn chế độ xử lý:
  - `Tool`: tách ý thông thường (không AI)
  - `Tool + AI`: tối ưu + phân loại bằng Gemini
- Theo dõi trạng thái xử lý theo thời gian thực
- Tải JSON flat/nested hoặc mở link Google Sheets sau khi hoàn tất

### Chỉ xuất JSON

```bash
python main.py docs/luat/69_2025_QH15_603983.docx --output-json
```

### Chỉ xuất Google Sheets

```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-sheets \
  --sheets-id "YOUR_SPREADSHEET_ID"
```

### Xuất cả JSON và Google Sheets

```bash
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-json \
  --output-sheets \
  --sheets-id "YOUR_SPREADSHEET_ID"
```

### Các tùy chọn nâng cao

```bash
# Chỉ định tên worksheet
python main.py input.docx --output-sheets --sheets-id "ID" --sheet-name "Luật 69/2025"

# Chỉ định tên file JSON
python main.py input.docx --output-json --json-filename "luat_69_2025"

# Nối thêm dữ liệu (không xóa dữ liệu cũ)
python main.py input.docx --output-sheets --sheets-id "ID" --no-clear

# Chỉ định đường dẫn credentials khác
python main.py input.docx --output-sheets --sheets-id "ID" --credentials "path/to/creds.json"
```

## Cấu trúc Project

```
ai-law/
├── credentials/
│   └── credentials.json          # Google Service Account credentials
├── docs/
│   └── luat/
│       └── 69_2025_QH15_603983.docx  # File luật mẫu
├── src/
│   ├── __init__.py
│   ├── patterns.py               # Regex patterns
│   ├── document_reader.py        # Đọc .docx
│   ├── parser.py                 # State machine parser
│   ├── json_exporter.py          # Xuất JSON
│   └── sheets_exporter.py        # Xuất Google Sheets
├── output/                       # Thư mục chứa file JSON output
├── main.py                       # Script chính
├── requirements.txt              # Python dependencies
└── README.md                     # File này
```

## Cấu trúc dữ liệu output

### JSON Flat (Phẳng)

```json
{
  "metadata": {
    "export_time": "2026-02-26T10:30:00",
    "total_entries": 150,
    "format": "flat"
  },
  "data": [
    {
      "Chương": "Chương I",
      "Mục": "",
      "Điều": "Điều 1",
      "Khoản": "1",
      "Điểm": "a",
      "Nội dung": "Nội dung điểm a..."
    }
  ]
}
```

### JSON Nested (Cây)

```json
{
  "metadata": {
    "export_time": "2026-02-26T10:30:00",
    "total_chapters": 5,
    "format": "nested"
  },
  "structure": {
    "chapters": [
      {
        "name": "Chương I",
        "articles": [
          {
            "name": "Điều 1",
            "clauses": [
              {
                "name": "1",
                "points": [
                  {
                    "name": "a",
                    "content": "Nội dung..."
                  }
                ],
                "content": ""
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### Google Sheets

| Chương | Mục | Điều | Khoản | Điểm | Nội dung |
|--------|------|------|-------|------|----------|
| Chương I | | Điều 1 | | | Nội dung điều 1... |
| Chương VI | Mục 3 | Điều 43 | 1 | a | Nội dung điểm a... |

## Xử lý lỗi

### Lỗi "File không tồn tại"
- Kiểm tra đường dẫn file .docx
- Đảm bảo file có extension .docx

### Lỗi "Không thể xác thực Google Sheets"
- Kiểm tra file credentials.json có đúng định dạng
- Đảm bảo đã enable Google Sheets API
- Kiểm tra Service Account email đã được share quyền truy cập Sheet

### Lỗi "Permission denied"
- Chia sẻ Google Sheet với email Service Account
- Cấp quyền Editor (không phải Viewer)

## Giấy phép

MIT License

## Tác giả

Copilot + Human
