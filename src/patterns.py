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
