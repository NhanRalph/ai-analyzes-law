"""
Module Parser với State Machine để phân tích cấu trúc văn bản pháp luật
"""

from .patterns import LegalPatterns

class LegalDocumentParser:
    """
    Parser sử dụng State Machine để phân tích văn bản pháp luật
    """
    
    def __init__(self):
        """
        Khởi tạo Parser với state ban đầu
        """
        self.patterns = LegalPatterns()
        self.reset_state()
        self.data = []
        self.nested_structure = []
    
    def reset_state(self):
        """
        Reset state của parser về trạng thái ban đầu
        """
        self.metadata = {
            'van_ban': 'Chưa xác định',
            'ngay_ban_hanh': 'Chưa xác định'
        }
        self.current_chapter = ""
        self.current_chapter_title = ""
        self.current_section = ""
        self.current_section_title = ""
        self.current_article = ""
        self.current_article_title = ""
        self.current_clause = ""
        self.current_clause_content = ""
        self.clause_has_colon = False
        self.pending_content = []
    
    def parse(self, paragraphs, source_name=None):
        """
        Parse danh sách paragraphs thành cấu trúc dữ liệu
        
        Args:
            paragraphs (list): Danh sách các đoạn văn bản
            
        Returns:
            list: Danh sách các entry (dict) với cấu trúc phẳng
        """
        self.data = []
        self.nested_structure = []
        self.reset_state()
        
        # Trích xuất metadata
        self.metadata = self.patterns.extract_doc_metadata(paragraphs, source_name=source_name)
        
        for i, para in enumerate(paragraphs):
            self._process_paragraph(para, i)
        
        # Xử lý nội dung còn pending (nếu có)
        self._flush_pending_content()
        
        return self.data
    
    def _process_paragraph(self, para, index):
        """
        Xử lý một paragraph
        
        Args:
            para (str): Paragraph cần xử lý
            index (int): Chỉ số của paragraph
        """
        # Kiểm tra phần kết luật (bỏ qua)
        if self.patterns.is_law_conclusion(para):
            return
        
        # Kiểm tra Chương
        is_chap, chap_num, chap_title = self.patterns.is_chapter(para)
        if is_chap:
            self._flush_pending_content()
            self.current_chapter = f"Chương {chap_num}"
            # Nếu tiêu đề đã có trên cùng dòng thì lưu, không thì dòng tiếp theo sẽ là tiêu đề
            self.current_chapter_title = chap_title
            self.current_section = ""
            self.current_section_title = ""
            self.current_article = ""
            self.current_article_title = ""
            self.current_clause = ""
            self.current_clause_content = ""
            return
        
        # Kiểm tra Mục
        is_sect, sect_num, sect_title = self.patterns.is_section(para)
        if is_sect:
            self._flush_pending_content()
            self.current_section = f"Mục {sect_num}"
            self.current_section_title = sect_title
            self.current_article = ""
            self.current_article_title = ""
            self.current_clause = ""
            self.current_clause_content = ""
            return
        
        # Kiểm tra Điều
        is_art, art_num, art_title = self.patterns.is_article(para)
        if is_art:
            self._flush_pending_content()
            self.current_article = f"Điều {art_num}"
            self.current_article_title = art_title
            self.current_clause = ""
            self.current_clause_content = ""
            self.clause_has_colon = False
            return
        
        # Nếu đang trong một Điều, kiểm tra Khoản
        if self.current_article:
            is_cl, cl_num, cl_content = self.patterns.is_clause(para, context_is_article=True)
            if is_cl:
                self._flush_pending_content()
                self.current_clause = cl_num
                self.current_clause_content = cl_content
                self.clause_has_colon = self.patterns.ends_with_colon(cl_content)
                
                # Nếu khoản không có dấu hai chấm, có thể đây là khoản độc lập
                if not self.clause_has_colon:
                    self._add_entry(
                        chapter=self.current_chapter,
                        section=self.current_section,
                        article=self.current_article,
                        clause=self.current_clause,
                        point="",
                        content=self.current_clause_content
                    )
                return
            
            # Kiểm tra Điểm
            is_pt, pt_letter, pt_content = self.patterns.is_point(para)
            if is_pt and self.current_clause and self.clause_has_colon:
                self._add_entry(
                    chapter=self.current_chapter,
                    section=self.current_section,
                    article=self.current_article,
                    clause=self.current_clause,
                    point=pt_letter,
                    content=pt_content
                )
                return
            
            # Nếu không phải cấu trúc nào, là nội dung tiếp theo
            self.pending_content.append(para)
    
    def _flush_pending_content(self):
        """
        Xử lý các nội dung đang pending (nội dung nhiều dòng)
        """
        if not self.pending_content:
            return
        
        content = " ".join(self.pending_content)
        
        # Nếu có khoản hiện tại mà không có dấu hai chấm
        if self.current_clause and not self.clause_has_colon:
            # Cập nhật entry cuối cùng
            if self.data:
                self.data[-1]['noi_dung'] += " " + content
        elif self.current_article and not self.current_clause:
            # Nội dung thuộc về Điều (không có khoản)
            self._add_entry(
                chapter=self.current_chapter,
                section=self.current_section,
                article=self.current_article,
                clause="",
                point="",
                content=content
            )
        elif self.current_section and not self.current_article:
            # Có thể là tiêu đề mục
            if not self.current_section_title:
                self.current_section_title = content
        elif self.current_chapter and not self.current_section and not self.current_article:
            # Có thể là tiêu đề chương
            if not self.current_chapter_title:
                self.current_chapter_title = content
        
        self.pending_content = []
    
    def _add_entry(self, chapter, section, article, clause, point, content):
        """
        Thêm một entry vào danh sách dữ liệu
        
        Args:
            chapter (str): Số chương
            section (str): Số mục
            article (str): Số điều
            clause (str): Số khoản
            point (str): Ký tự điểm
            content (str): Nội dung
        """
        entry = {
            'chuong': chapter,
            'muc': section,
            'tieu_de_muc': self.current_section_title,
            'dieu': article,
            'tieu_de_dieu': self.current_article_title,
            'khoan': clause,
            'diem': point,
            'noi_dung': content.strip()
        }
        self.data.append(entry)
    
    def get_data(self):
        """
        Lấy dữ liệu đã parse (dạng phẳng)
        
        Returns:
            list: Danh sách các entry
        """
        return self.data
    
    def build_nested_structure(self):
        """
        Xây dựng cấu trúc cây nested từ dữ liệu phẳng
        
        Returns:
            dict: Cấu trúc cây nested
        """
        nested = {
            'chapters': []
        }
        
        current_chapter = None
        current_article = None
        current_clause = None
        
        for entry in self.data:
            chapter_name = entry['chuong']
            article_name = entry['dieu']
            clause_name = entry['khoan']
            point_name = entry['diem']
            content = entry['noi_dung']
            
            # Xử lý Chương
            if chapter_name and (not current_chapter or current_chapter['name'] != chapter_name):
                current_chapter = {
                    'name': chapter_name,
                    'articles': []
                }
                nested['chapters'].append(current_chapter)
                current_article = None
                current_clause = None
            
            # Xử lý Điều
            if article_name and (not current_article or current_article['name'] != article_name):
                current_article = {
                    'name': article_name,
                    'clauses': [],
                    'ai_classification': entry.get('ai_classification') if not clause_name else None
                }
                if current_chapter:
                    current_chapter['articles'].append(current_article)
                current_clause = None
            
            # Xử lý Khoản
            if clause_name and (not current_clause or current_clause['name'] != clause_name):
                current_clause = {
                    'name': clause_name,
                    'points': [],
                    'content': content if not point_name else "",
                    'ai_classification': entry.get('ai_classification') if not point_name else None
                }
                if current_article:
                    current_article['clauses'].append(current_clause)
            
            # Xử lý Điểm
            if point_name and current_clause:
                point = {
                    'name': point_name,
                    'content': content,
                    'ai_classification': entry.get('ai_classification')
                }
                current_clause['points'].append(point)
            elif not clause_name and not point_name and current_article:
                # Nội dung trực tiếp của Điều
                if 'content' not in current_article:
                    current_article['content'] = content
                else:
                    current_article['content'] += " " + content
                
                # Cập nhật AI classification cho Điều nếu chưa có (lấy từ entry này)
                if not current_article.get('ai_classification'):
                    current_article['ai_classification'] = entry.get('ai_classification')
        
        return nested
