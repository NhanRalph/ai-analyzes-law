# CHANGELOG - Legal Document Parser

## Version 2.0 - 26/02/2026

### ✨ Tính năng mới

#### 1. Thêm cấp độ "Mục" (Section)
- **Mục** là cấp độ mới nằm giữa **Chương** và **Điều**
- Pattern: `Mục + số` (Ví dụ: "Mục 1", "Mục 2", "Mục 3")
- Mục là điều mục của một bộ nội dung mới, không liên quan trực tiếp tới nội dung chính của điều khoản
- Cột "Mục" được thêm vào cả JSON và Google Sheets

**Ví dụ cấu trúc:**
```
Chương VI - AN TOÀN, AN NINH TRONG HOẠT ĐỘNG HÓA CHẤT
  ├── Mục 1 - AN TOÀN, AN NINH HÓA CHẤT
  │   ├── Điều 33
  │   └── Điều 34
  ├── Mục 2 - PHÒNG NGỪA, ỨNG PHÓ SỰ CỐ HÓA CHẤT
  │   ├── Điều 35
  │   └── Điều 36
  └── Mục 3 - BẢO VỆ MÔI TRƯỜNG VÀ AN TOÀN CHO CỘNG ĐỒNG
      ├── Điều 43
      └── Điều 44
```

#### 2. Lọc phần kết luật
- Tự động loại bỏ phần kết của văn bản luật (thường in nghiêng)
- Pattern: `Luật này được Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam...`
- Phần kết không còn được ghép vào khoản cuối cùng của luật

### 🔧 Các file đã thay đổi

#### 1. `src/patterns.py`
- Thêm `SECTION_PATTERN`: Pattern nhận diện Mục
- Thêm `LAW_CONCLUSION_PATTERN`: Pattern nhận diện phần kết luật
- Thêm hàm `is_section()`: Kiểm tra dòng có phải là Mục
- Thêm hàm `is_law_conclusion()`: Kiểm tra dòng có phải là phần kết luật

#### 2. `src/parser.py`
- Cập nhật `reset_state()`: Thêm `current_section` và `current_section_title`
- Cập nhật `_process_paragraph()`: 
  - Thêm logic xử lý Mục
  - Thêm logic lọc phần kết luật (skip khi gặp)
- Cập nhật `_add_entry()`: Thêm tham số `section`
- Cập nhật tất cả lời gọi `_add_entry()` để truyền tham số `section`
- Cập nhật `_flush_pending_content()`: Xử lý nội dung pending cho Mục

#### 3. `src/sheets_exporter.py`
- Cập nhật `headers`: `['Chương', 'Mục', 'Điều', 'Khoản', 'Điểm', 'Nội dung']`
- Cập nhật `export_data()`: Thêm cột Mục vào rows
- Cập nhật `_format_header()`: Format range từ `A1:E1` → `A1:F1`
- Cập nhật `columns_auto_resize()`: Từ `(0, 4)` → `(0, 5)`
- Cập nhật `append_data()`: Thêm cột Mục

#### 4. `main.py`
- Cập nhật `print_summary()`:
  - Thêm đếm số Mục
  - Hiển thị "Số Mục" trong tóm tắt
  - Hiển thị thông tin Mục trong entry mẫu (nếu có)

#### 5. `README.md`
- Cập nhật phần "Tính năng": Thêm phân tích cấp độ Mục
- Cập nhật phần "Tính năng": Thêm lọc bỏ phần kết luật
- Cập nhật ví dụ JSON: Thêm trường "Mục"
- Cập nhật bảng Google Sheets: Thêm cột "Mục"

#### 6. `MASTER_PROMPT.md`
- Cập nhật phần "Phân tích cấu trúc dữ liệu": Thêm mô tả về Mục
- Cập nhật Bước 2: Thêm `is_section()` và `is_law_conclusion()`
- Cập nhật Bước 3: Thêm trường `Mục` vào cấu trúc object

### 📊 Kết quả test với file mẫu

**File:** `docs/luat/69_2025_QH15_603983.docx` (Luật Hóa chất số 69/2025/QH15)

**Thống kê:**
- Tổng số entries: 291
- Số Chương: 7
- **Số Mục: 3** ✨ (MỚI)
- Số Điều: 48
- Số Khoản: 285
- Số Điểm: 126

**Các Mục đã phát hiện:**
1. Mục 1 - AN TOÀN, AN NINH HÓA CHẤT (Chương VI)
2. Mục 2 - PHÒNG NGỪA, ỨNG PHÓ SỰ CỐ HÓA CHẤT (Chương VI)
3. Mục 3 - BẢO VỆ MÔI TRƯỜNG VÀ AN TOÀN CHO CỘNG ĐỒNG (Chương VI)

**Phần kết đã lọc:**
- ✅ "Luật này được Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam khóa XV, kỳ họp thứ 9 thông qua ngày 14 tháng 6 năm 2025." không còn xuất hiện trong dữ liệu

### 🔄 Backward Compatibility

- ⚠️ **Breaking Change**: Cấu trúc JSON đã thay đổi (thêm trường "Mục")
- ⚠️ **Breaking Change**: Google Sheets có thêm cột "Mục" (từ 5 cột → 6 cột)
- Các file JSON/Sheets cũ vẫn có thể đọc được nhưng thiếu trường "Mục"

### 📝 Migration Guide

Nếu bạn đang sử dụng version cũ:

1. **JSON files**: Thêm trường `"Mục": ""` vào các entry cũ
2. **Google Sheets**: Thêm cột "Mục" giữa "Chương" và "Điều"
3. **Code integration**: Cập nhật code xử lý để handle trường "Mục" (có thể rỗng)

### 🧪 Testing

```bash
# Test với JSON
python main.py docs/luat/69_2025_QH15_603983.docx --output-json

# Test với Google Sheets
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-sheets \
  --sheets-id "YOUR_SHEET_ID" \
  --sheet-name "Luật 69/2025 - Updated"

# Test cả hai
python main.py docs/luat/69_2025_QH15_603983.docx \
  --output-json \
  --output-sheets \
  --sheets-id "YOUR_SHEET_ID"
```

### 🐛 Bug Fixes

- Fixed: Phần kết luật không còn bị ghép vào khoản cuối cùng
- Fixed: Nội dung của Mục không còn bị ghép vào Điều tiếp theo

### 📌 Notes

- Mục là optional - không phải tất cả văn bản luật đều có Mục
- Khi không có Mục, trường "Mục" sẽ là chuỗi rỗng `""`
- Parser tự động nhận diện và xử lý đúng các trường hợp có/không có Mục
