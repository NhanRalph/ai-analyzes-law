#!/usr/bin/env python3
"""
LEGAL DOCUMENT PARSER - Main Script
Công cụ phân tích văn bản pháp luật Việt Nam và xuất ra JSON/Google Sheets
"""

import os
import sys
import argparse
from src.document_reader import DocumentReader
from src.parser import LegalDocumentParser
from src.json_exporter import JSONExporter
from src.sheets_exporter import SheetsExporter
from src.ai_classifier import AIClassifier

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Phân tích văn bản pháp luật và xuất ra JSON/Google Sheets'
    )
    
    parser.add_argument(
        'input_file',
        help='Đường dẫn tới file .docx đầu vào'
    )
    
    parser.add_argument(
        '--output-json',
        action='store_true',
        help='Xuất ra file JSON'
    )
    
    parser.add_argument(
        '--output-sheets',
        action='store_true',
        help='Xuất lên Google Sheets'
    )
    
    parser.add_argument(
        '--sheets-id',
        help='ID của Google Spreadsheet'
    )
    
    parser.add_argument(
        '--credentials',
        default='credentials/credentials.json',
        help='Đường dẫn tới file credentials.json (mặc định: credentials/credentials.json)'
    )
    
    parser.add_argument(
        '--sheet-name',
        help='Tên worksheet trong Google Sheets (tùy chọn)'
    )
    
    parser.add_argument(
        '--json-filename',
        help='Tên file JSON output (tùy chọn)'
    )
    
    parser.add_argument(
        '--no-clear',
        action='store_true',
        help='Không xóa dữ liệu cũ trong Google Sheets (nối thêm)'
    )
    
    parser.add_argument(
        '--use-ai',
        action='store_true',
        help='Sử dụng Gemini AI để phân loại Điều/Khoản/Điểm'
    )
    
    parser.add_argument(
        '--gemini-api-key',
        help='Gemini API Key (nếu không có trong .env)'
    )
    
    return parser.parse_args()

def print_banner():
    """
    In banner của chương trình
    """
    print("=" * 70)
    print("  LEGAL DOCUMENT PARSER - Công cụ phân tích văn bản pháp luật")
    print("=" * 70)
    print()

def print_summary(data):
    """
    In tóm tắt dữ liệu đã parse
    """
    if not data:
        print("⚠ Không có dữ liệu")
        return
    
    print("\n" + "=" * 70)
    print("  TÓM TẮT DỮ LIỆU")
    print("=" * 70)
    
    # Đếm số lượng từng loại
    chapters = set()
    sections = set()
    articles = set()
    clauses = 0
    points = 0
    
    for entry in data:
        if entry.get('chuong'):
            chapters.add(entry['chuong'])
        if entry.get('muc'):
            sections.add(entry['muc'])
        if entry.get('dieu'):
            articles.add(entry['dieu'])
        if entry.get('khoan'):
            clauses += 1
        if entry.get('diem'):
            points += 1
    
    print(f"  Tổng số dòng dữ liệu: {len(data)}")
    print(f"  Số Chương: {len(chapters)}")
    print(f"  Số Mục: {len(sections)}")
    print(f"  Số Điều: {len(articles)}")
    print(f"  Số Khoản: {clauses}")
    print(f"  Số Điểm: {points}")
    
    # Thống kê AI
    ai_classified = sum(1 for entry in data if entry.get('ai_classification'))
    if ai_classified > 0:
        print(f"  Số dòng được AI phân loại: {ai_classified}")
    print()
    
    # Hiển thị một vài entry mẫu
    print("  Một vài entry mẫu:")
    print("  " + "-" * 66)
    for i, entry in enumerate(data[:3]):
        muc_info = f" ({entry.get('muc', '')})" if entry.get('muc') else ""
        print(f"  [{i+1}] {entry.get('dieu', '')} - {entry.get('khoan', '')} {entry.get('diem', '')}{muc_info}")
        content = entry.get('noi_dung', '')
        if len(content) > 60:
            content = content[:60] + "..."
        print(f"      {content}")
        print()

def main():
    """
    Hàm main
    """
    print_banner()
    
    # Parse arguments
    args = parse_arguments()
    
    # Kiểm tra file đầu vào
    if not os.path.exists(args.input_file):
        print(f"✗ File không tồn tại: {args.input_file}")
        sys.exit(1)
    
    print(f"📄 Đọc file: {args.input_file}")
    print()
    
    # Bước 1: Đọc file .docx
    print("[1/4] Đọc và tiền xử lý file .docx...")
    reader = DocumentReader(args.input_file)
    paragraphs = reader.read()
    
    if not paragraphs:
        print("✗ Không thể đọc file hoặc file rỗng")
        sys.exit(1)
    
    print(f"✓ Đã đọc {len(paragraphs)} đoạn văn bản")
    print()
    
    # Bước 2: Parse dữ liệu
    print("[2/4] Phân tích cấu trúc văn bản...")
    parser = LegalDocumentParser()
    data = parser.parse(paragraphs)
    
    if not data:
        print("✗ Không parse được dữ liệu")
        sys.exit(1)
    
    print(f"✓ Đã parse {len(data)} entry")
    
    # Bước 2.5: Phân loại bằng AI (nếu được yêu cầu)
    if args.use_ai:
        print("\n[2.5/4] Phân loại bằng Gemini AI (vui lòng đợi)...")
        ai_classifier = AIClassifier(api_key=args.gemini_api_key)
        data = ai_classifier.classify_batch(data)
        print("✓ Đã hoàn thành phân loại bằng AI")
    
    # In tóm tắt
    print_summary(data)
    
    # Bước 3: Xuất JSON (nếu được yêu cầu)
    if args.output_json:
        print("[3/4] Xuất dữ liệu ra JSON...")
        json_exporter = JSONExporter()
        
        # Xây dựng cấu trúc nested
        nested_data = parser.build_nested_structure()
        
        # Lấy định nghĩa từ AI Classifier nếu có dùng AI
        definitions = None
        if args.use_ai:
            definitions = {
                'hoa_chat': ai_classifier.definitions_hoa_chat,
                'hang_muc': ai_classifier.definitions_hang_muc
            }
        
        # Xuất cả hai dạng
        if args.json_filename:
            base_name = args.json_filename.replace('.json', '')
            json_exporter.export_both(data, nested_data, base_name, definitions=definitions)
        else:
            json_exporter.export_both(data, nested_data, definitions=definitions)
        print()
    
    # Bước 4: Xuất Google Sheets (nếu được yêu cầu)
    if args.output_sheets:
        if not args.sheets_id:
            print("✗ Cần cung cấp --sheets-id để xuất lên Google Sheets")
            sys.exit(1)
        
        print("[4/4] Xuất dữ liệu lên Google Sheets...")
        
        # Kiểm tra credentials
        has_env_credentials = bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') or os.getenv('GG_SERVICE_ACCOUNT_JSON'))
        if not os.path.exists(args.credentials) and not has_env_credentials:
            print(f"✗ File credentials không tồn tại: {args.credentials}")
            print("  Gợi ý: đặt GOOGLE_SERVICE_ACCOUNT_JSON trong .env để không cần file credentials")
            sys.exit(1)
        
        sheets_exporter = SheetsExporter(args.credentials, args.sheets_id)
        
        clear_existing = not args.no_clear
        success = sheets_exporter.export_data(
            data,
            clear_existing=clear_existing,
            sheet_name=args.sheet_name,
            van_ban=parser.metadata.get('van_ban'),
            ngay_ban_hanh=parser.metadata.get('ngay_ban_hanh')
        )
        
        if not success:
            print("✗ Xuất Google Sheets thất bại")
            sys.exit(1)
        print()
    
    # Hoàn thành
    print("=" * 70)
    print("  ✓ HOÀN THÀNH!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Đã hủy bởi người dùng")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
