"""
Module chứa các pattern Regex để nhận diện cấu trúc văn bản pháp luật Việt Nam
"""

import re

class LegalPatterns:
    """
    Class chứa các pattern và hàm kiểm tra cho từng cấp độ văn bản pháp luật
    """
    
    # Pattern cho Chương (Ví dụ: "Chương I", "Chương II", "CHƯƠNG III. QUY ĐẬNH CHUNG")
    CHAPTER_PATTERN = r'^\s*CH[ƯU][ƠO]NG\s+([IVX]+)\s*[.\-]?\s*(.*?)$'
    
    # Pattern cho Mục (Ví dụ: "Mục 1.", "MỤC 2. PHÒNG NGỪA")
    SECTION_PATTERN = r'^\s*M[ỤU]C\s+(\d+)\s*\.?\s*(.*?)$'
    
    # Pattern cho Điều (Ví dụ: "Điều 1.", "Điều 25. Giải thích từ ngữ")
    ARTICLE_PATTERN = r'^\s*Đi[ềe]u\s+(\d+)\s*\.\s*(.*?)$'
    
    # Pattern cho Số hiệu văn bản (Ví dụ: "Luật số: 69/2025/QH15")
    DOC_NUMBER_PATTERN = r'\b(?:LU[ẬA]T\s*S[ỐO]|S[ỐO](?:\s*HI[ỆE]U)?)\s*:?\s*([0-9]{1,4}\s*/\s*[0-9]{2,4}\s*/\s*[A-Z0-9\-]{2,20})\b'
    
    # Pattern cho Ngày ban hành (Ví dụ: "ngày 14 tháng 6 năm 2025")
    DOC_DATE_PATTERN = r' ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})'
    
    # Pattern cho Tiêu đề văn bản (Ví dụ: "LUẬT HÓA CHẤT")
    DOC_TITLE_PATTERN = r'^\s*(LU[ẬA]T(\s+.*)?)$'
    
    # Pattern cho phần kết luật (thường in nghiêng)
    LAW_CONCLUSION_PATTERN = r'^\s*Luật\s+này\s+được\s+Quốc\s+hội'
    
    # Pattern cho Khoản (Ví dụ: "1. ", "2. ", "15. ")
    # Khoản bắt đầu bằng số và dấu chấm, không phải đầu dòng Điều
    CLAUSE_PATTERN = r'^\s*(\d+)\.\s+(.+)$'
    
    # Pattern cho Điểm (Ví dụ: "a) ", "b) ", "aa) ", "dd) ")
    POINT_PATTERN = r'^\s*([a-z]+)\)\s+(.+)$'
    
    @staticmethod
    def is_chapter(text):
        """
        Kiểm tra xem dòng text có phải là Chương không
        
        Args:
            text (str): Dòng text cần kiểm tra
            
        Returns:
            tuple: (True/False, chapter_number, chapter_title) nếu là Chương
        """
        if not text or not text.strip():
            return False, None, None
            
        match = re.match(LegalPatterns.CHAPTER_PATTERN, text.strip(), re.IGNORECASE)
        if match:
            chapter_num = match.group(1)
            chapter_title = match.group(2).strip() if match.group(2) else ""
            return True, chapter_num, chapter_title
        return False, None, None
    
    @staticmethod
    def is_section(text):
        """
        Kiểm tra xem dòng text có phải là Mục không
        
        Args:
            text (str): Dòng text cần kiểm tra
            
        Returns:
            tuple: (True/False, section_number, section_title)
        """
        if not text or not text.strip():
            return False, None, None
            
        match = re.match(LegalPatterns.SECTION_PATTERN, text.strip(), re.IGNORECASE)
        if match:
            section_num = match.group(1)
            section_title = match.group(2).strip() if match.group(2) else ""
            return True, section_num, section_title
        return False, None, None
    
    @staticmethod
    def is_law_conclusion(text):
        """
        Kiểm tra xem dòng text có phải là phần kết luật không
        (Ví dụ: "Luật này được Quốc hội...")
        
        Args:
            text (str): Dòng text cần kiểm tra
            
        Returns:
            bool: True nếu là phần kết luật
        """
        if not text or not text.strip():
            return False
            
        return bool(re.match(LegalPatterns.LAW_CONCLUSION_PATTERN, text.strip(), re.IGNORECASE))
    
    @staticmethod
    def is_article(text):
        """
        Kiểm tra xem dòng text có phải là Điều không
        
        Args:
            text (str): Dòng text cần kiểm tra
            
        Returns:
            tuple: (True/False, article_number, article_title)
        """
        if not text or not text.strip():
            return False, None, None
            
        match = re.match(LegalPatterns.ARTICLE_PATTERN, text.strip(), re.IGNORECASE)
        if match:
            article_num = match.group(1)
            article_title = match.group(2).strip() if match.group(2) else ""
            return True, article_num, article_title
        return False, None, None
    
    @staticmethod
    def is_clause(text, context_is_article=False):
        """
        Kiểm tra xem dòng text có phải là Khoản không
        
        Args:
            text (str): Dòng text cần kiểm tra
            context_is_article (bool): True nếu đang ở ngữ cảnh bên trong một Điều
            
        Returns:
            tuple: (True/False, clause_number, clause_content)
        """
        if not text or not text.strip():
            return False, None, None
        
        # Kiểm tra không phải là Điều trước
        is_art, _, _ = LegalPatterns.is_article(text)
        if is_art:
            return False, None, None
            
        match = re.match(LegalPatterns.CLAUSE_PATTERN, text.strip())
        if match and context_is_article:
            clause_num = match.group(1)
            clause_content = match.group(2).strip()
            return True, clause_num, clause_content
        return False, None, None
    
    @staticmethod
    def is_point(text):
        """
        Kiểm tra xem dòng text có phải là Điểm không
        
        Args:
            text (str): Dòng text cần kiểm tra
            
        Returns:
            tuple: (True/False, point_letter, point_content)
        """
        if not text or not text.strip():
            return False, None, None
            
        match = re.match(LegalPatterns.POINT_PATTERN, text.strip())
        if match:
            point_letter = match.group(1)
            point_content = match.group(2).strip()
            return True, point_letter, point_content
        return False, None, None
    
    @staticmethod
    def extract_doc_metadata(paragraphs, source_name=None):
        """
        Trích xuất thông tin văn bản (Số hiệu, Ngày, Tiêu đề) từ những dòng đầu tiên
        
        Args:
            paragraphs (list): Danh sách các đoạn văn bản
            
        Returns:
            dict: {van_ban: str, ngay_ban_hanh: str}
        """
        metadata = {
            'van_ban': "Chưa xác định",
            'ngay_ban_hanh': "Chưa xác định"
        }
        
        if not paragraphs:
            return metadata

        def normalize_doc_number(number_text):
            """
            Chuẩn hóa số hiệu văn bản (xóa khoảng trắng thừa quanh '/')
            Ví dụ: '69 / 25 / qh15' -> '69/25/QH15'
            """
            compact = re.sub(r'\s*/\s*', '/', number_text.strip())
            compact = re.sub(r'\s+', '', compact)
            return compact.upper()
            
        raw_number = ""
        doc_title = ""
        title_lines = []
        date_line = ""
        
        # 1. Tìm Số hiệu theo nhãn ở phần đầu văn bản
        for i, para in enumerate(paragraphs[:25]):
            p = para.strip()
            if not p: continue
            
            clean_p = re.sub(r'\s+', ' ', p)
            upper_p = clean_p.upper()
            
            # Tìm Số hiệu theo nhãn "Luật số" hoặc "Số" trước
            if not raw_number:
                num_match = re.search(LegalPatterns.DOC_NUMBER_PATTERN, upper_p, re.IGNORECASE)
                if num_match:
                    raw_number = normalize_doc_number(num_match.group(1))
                else:
                    # Fallback: tìm token giống số hiệu văn bản bất kỳ trên dòng
                    generic_candidates = re.findall(
                        r'\b\d{1,4}\s*/\s*\d{2,4}\s*/\s*[A-Z0-9\-]{2,20}\b',
                        upper_p
                    )
                    if generic_candidates:
                        raw_number = normalize_doc_number(generic_candidates[0])
            
        # 1.1 Fallback số hiệu từ tên file (ví dụ: 69_2025_QH15.docx -> 69/25/QH15)
        if not raw_number and source_name:
            source_upper = source_name.upper()
            filename_match = re.search(r'(\d{1,4})[_\-](\d{2,4})[_\-]([A-Z]{1,6}\d{1,4})', source_upper)
            if filename_match:
                number_part, year_part, agency_part = filename_match.groups()
                if len(year_part) == 4:
                    year_part = year_part[-2:]
                raw_number = f"{number_part}/{year_part}/{agency_part}"

        # 1.2 Tìm Ngày ban hành (ưu tiên dòng 'thông qua ngày ...')
        date_candidates = []
        for para in paragraphs:
            p = para.strip()
            if not p:
                continue

            clean_p = re.sub(r'\s+', ' ', p)
            date_match = re.search(r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})', clean_p, re.IGNORECASE)
            if date_match:
                day, month, year = date_match.groups()
                normalized_date = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                date_candidates.append((clean_p, normalized_date))

        for line_text, normalized_date in date_candidates:
            if re.search(r'thông\s+qua\s+ngày', line_text, re.IGNORECASE):
                metadata['ngay_ban_hanh'] = normalized_date
                date_line = line_text
                break

        if metadata['ngay_ban_hanh'] == "Chưa xác định" and date_candidates:
            metadata['ngay_ban_hanh'] = date_candidates[0][1]
            date_line = date_candidates[0][0]
        
        # 2. Tìm Tiêu đề (dòng Uppercase sau header)
        skip_headers = [
            "QUỐC HỘI", "CỘNG HÀ", "ĐỘC LẬP", "VĂN PHÒNG", "HÀ NỘI", 
            "CHỦ NGHĨA", "VIỆT NAM", "HẠNH PHÚC", "TỰ DO", "CHỦ TỊCH"
        ]
        
        # Cố gắng sửa lại skip_headers cho đúng chính tả nếu có lỗi
        skip_headers = [h.replace("CỘNG HÀ", "CỘNG HÒA") for h in skip_headers]
        
        collecting_title = False
        for i, para in enumerate(paragraphs[:25]):
            p = para.strip()
            if not p: continue
            
            p_upper = p.upper()
            
            # Bỏ qua dòng ngày và dòng số hiệu
            if date_line and (p == date_line or date_line in p): continue
            if raw_number and raw_number in p_upper: continue
            if "SỐ:" in p_upper or "LUẬT SỐ:" in p_upper: continue
            
            # Nếu là dòng viết hoa toàn bộ và không phải common header
            if p.isupper() and len(p) > 3:
                if not any(header in p_upper for header in skip_headers):
                    title_lines.append(p)
                    collecting_title = True
            elif collecting_title and len(p) > 0:
                if p_upper.startswith("CĂN CỨ"):
                    break
        
        # 3. Tổng hợp Tiêu đề
        if title_lines:
            # LUẬT HÓA CHẤT -> Luật Hóa Chất
            doc_title = " ".join(title_lines).title()
        
        # Fallback
        if not doc_title or "Luật" not in doc_title:
             for para in paragraphs[:25]:
                p_u = para.strip().upper()
                if "LUẬT" in p_u and para.strip().isupper() and not any(h in p_u for h in skip_headers):
                    doc_title = para.strip().title()
                    break
        
        # 4. Tạo chuỗi final
        parts = []
        if raw_number:
            parts.append(f"Luật số: {raw_number}")
        
        if doc_title:
            if not doc_title.startswith("Luật"):
                doc_title = "Luật " + doc_title
            parts.append(doc_title)
            
        if parts:
            # Loại bỏ phần trùng lặp nếu title rủi ro có chứa số hiệu
            final_str = " ".join(parts)
            # Nếu trong final_str có cụm "Luật Luật", ta thu gọn
            final_str = re.sub(r'Luật Luật', 'Luật', final_str)
            metadata['van_ban'] = final_str
            
        return metadata

    @staticmethod
    def ends_with_colon(text):
        """
        Kiểm tra xem text có kết thúc bằng dấu hai chấm không
        (Dấu hiệu khoản cha có điểm con)
        
        Args:
            text (str): Text cần kiểm tra
            
        Returns:
            bool: True nếu kết thúc bằng dấu hai chấm
        """
        if not text:
            return False
        return text.strip().endswith(':')
