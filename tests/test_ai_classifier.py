import sys
import os
from dotenv import load_dotenv

# Thêm thư mục hiện tại vào path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_classifier import AIClassifier

def test_classifier():
    print("--- KIỂM TRA KẾT NỐI VÀ LOGIC AI CLASSIFIER ---")
    
    # Khởi tạo classifier
    classifier = AIClassifier()
    
    if not classifier.api_key:
        print("⚠ Cảnh báo: Không tìm thấy GEMINI_API_KEY. AI sẽ không hoạt động thực tế.")
        print("  Vui lòng tạo file .env và thêm GEMINI_API_KEY=xxx")
        return

    # Dữ liệu test giả lập
    test_entries = [
        {
            "chuong": "Chương I",
            "dieu": "Điều 2",
            "khoan": "12",
            "diem": "",
            "noi_dung": "Cơ sở hóa chất là địa điểm diễn ra một hoặc nhiều hoạt động sản xuất hóa chất, kinh doanh hóa chất, tồn trữ hóa chất, sử dụng hóa chất, xử lý chất thải hóa chất."
        },
        {
            "chuong": "Chương II",
            "dieu": "Điều 9",
            "khoan": "3",
            "diem": "c",
            "noi_dung": "Tổ chức được phép sản xuất, nhập khẩu, sử dụng, vận chuyển, tồn trữ hóa chất cấm theo mục đích quy định tại Luật Đầu tư, Luật Quản lý ngoại thương và luật khác có liên quan; được phép xuất khẩu hóa chất cấm trong trường hợp quy định tại điểm a khoản 5 Điều 12 của Luật này."
        }
    ]
    
    print(f"\nĐang phân loại {len(test_entries)} mẫu thử...")
    results = classifier.classify_batch(test_entries)
    
    for i, entry in enumerate(results):
        print(f"\n[Mẫu {i+1}] {entry['dieu']} - {entry['khoan']}{entry['diem']}")
        print(f"Nội dung: {entry['noi_dung'][:50]}...")
        
        ai = entry.get('ai_classification')
        if ai:
            print(f"AI -> Hạng mục: {ai.get('ten_hang_muc')} ({ai.get('id_hang_muc')})")
            print(f"AI -> Nhóm hóa chất: {ai.get('nhom_hoa_chat')}")
            print(f"AI -> Ghi chú: {ai.get('ghi_chu_ai')}")
        else:
            print("AI -> (Không có kết quả phân loại)")

if __name__ == "__main__":
    test_classifier()
