import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIClassifier:
    """
    Sử dụng Gemini AI để phân loại các điều khoản luật dựa trên định nghĩa hóa chất và hạng mục tuân thủ.
    Sử dụng SDK google-genai mới.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY không được tìm thấy. AI sẽ không hoạt động.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-3-flash-preview' # Sử dụng model 2.0 Flash mới nhất
            
        self.definitions_hoa_chat = []
        self.definitions_hang_muc = []
        self._load_definitions()

    def _load_definitions(self):
        """
        Đọc các file định nghĩa từ thư mục definitions/
        """
        try:
            # Đường dẫn tương đối dựa trên vị trí file này (src/ai_classifier.py)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            hc_path = os.path.join(base_dir, "definitions", "hoa_chat", "hoa_chat.json")
            if os.path.exists(hc_path):
                with open(hc_path, "r", encoding="utf-8") as f:
                    self.definitions_hoa_chat = json.load(f)
                    
            hm_path = os.path.join(base_dir, "definitions", "hang_muc", "hang_muc_tuan_thu.json")
            if os.path.exists(hm_path):
                with open(hm_path, "r", encoding="utf-8") as f:
                    self.definitions_hang_muc = json.load(f)
                    
            logger.info(f"Đã tải {len(self.definitions_hoa_chat)} định nghĩa hóa chất và {len(self.definitions_hang_muc)} hạng mục tuân thủ.")
        except Exception as e:
            logger.error(f"Lỗi khi tải định nghĩa: {e}")

    def _build_system_instruction(self) -> str:
        """
        Xây dựng hướng dẫn hệ thống chứa các định nghĩa
        """
        instruction = "Bạn là một chuyên gia pháp luật về hóa chất tại Việt Nam. Nhiệm vụ của bạn là phân loại các Điều/Khoản/Điểm của luật dựa trên các định nghĩa sau:\n\n"
        
        instruction += "### 1. ĐỊNH NGHĨA HẠNG MỤC TUÂN THỦ:\n"
        for item in self.definitions_hang_muc:
            instruction += f"- {item['hang_muc_tuan_thu']} ({item['id']}): {item['dinh_nghia']}. Từ khóa: {', '.join(item['detection_keywords'])}\n"
            
        instruction += "\n### 2. PHÂN NHÓM HÓA CHẤT TRỌNG TÂM:\n"
        main_groups = set()
        for item in self.definitions_hoa_chat:
            if item.get('phan_nhom_cap_1'):
                main_groups.add(item['phan_nhom_cap_1'])
        
        instruction += f"- Các nhóm: {', '.join(main_groups)}\n"
        
        instruction += "\n### Yêu cầu:\n"
        instruction += "- Trả về kết quả dưới dạng mảng JSON chứa các object. Mỗi object cho một đoạn văn bản.\n"
        instruction += "- Các trường cần có: 'id_hang_muc', 'ten_hang_muc', 'nhom_hoa_chat', 'ghi_chu_ai'.\n"
        instruction += "- Nếu không khớp định nghĩa nào, hãy để giá trị null.\n"
        
        return instruction

    def classify_batch(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Phân loại một danh sách các entries (Điều/Khoản/Điểm)
        """
        if not self.api_key or not self.client:
            return entries

        batch_size = 15 
        results = []
        system_instruction = self._build_system_instruction()
        
        for i in range(0, len(entries), batch_size):
            current_batch = entries[i:i + batch_size]
            
            user_content = "Hãy phân loại các đoạn văn bản sau đây:\n\n"
            for j, entry in enumerate(current_batch):
                text = f"--- ĐOẠN {j+1} ---\nVị trí: {entry.get('chuong', '')} - {entry.get('dieu', '')} - {entry.get('khoan', '')} {entry.get('diem', '')}\n"
                text += f"Nội dung: {entry.get('noi_dung', '')}\n\n"
                user_content += text
            
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                    )
                )
                
                # SDK mới trả về object có thuộc tính .text hoặc parsed JSON trực tiếp nếu cấu hình
                ai_data = json.loads(response.text)
                
                for j, entry in enumerate(current_batch):
                    classification = ai_data[j] if j < len(ai_data) else {}
                    entry['ai_classification'] = {
                        'id_hang_muc': classification.get('id_hang_muc'),
                        'ten_hang_muc': classification.get('ten_hang_muc'),
                        'nhom_hoa_chat': classification.get('nhom_hoa_chat'),
                        'ghi_chu_ai': classification.get('ghi_chu_ai')
                    }
                    results.append(entry)
                
                logger.info(f"Đã phân loại xong batch {i//batch_size + 1}")
                time.sleep(4) 
                
            except Exception as e:
                logger.error(f"Lỗi khi gọi Gemini AI ở batch {i//batch_size + 1}: {e}")
                for entry in current_batch:
                    entry['ai_classification'] = None
                    results.append(entry)
        
        return results
