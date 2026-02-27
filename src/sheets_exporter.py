"""
Module xuất dữ liệu lên Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class SheetsExporter:
    """
    Class xuất dữ liệu lên Google Sheets
    """
    
    # Định nghĩa scope cho Google Sheets API
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path, spreadsheet_id):
        """
        Khởi tạo SheetsExporter
        
        Args:
            credentials_path (str): Đường dẫn tới file credentials.json
            spreadsheet_id (str): ID của Google Spreadsheet
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
    
    def authenticate(self):
        """
        Xác thực với Google Sheets API
        
        Returns:
            bool: True nếu xác thực thành công
        """
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            self.client = gspread.authorize(creds)
            print("✓ Xác thực Google Sheets API thành công")
            return True
        except Exception as e:
            print(f"✗ Lỗi xác thực: {e}")
            return False
    
    def open_spreadsheet(self, sheet_name=None):
        """
        Mở spreadsheet và worksheet
        
        Args:
            sheet_name (str): Tên worksheet (mặc định: sheet đầu tiên)
            
        Returns:
            bool: True nếu mở thành công
        """
        try:
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            if sheet_name:
                try:
                    self.worksheet = self.spreadsheet.worksheet(sheet_name)
                except gspread.WorksheetNotFound:
                    # Tạo worksheet mới nếu không tồn tại
                    self.worksheet = self.spreadsheet.add_worksheet(
                        title=sheet_name,
                        rows=1000,
                        cols=10
                    )
            else:
                self.worksheet = self.spreadsheet.sheet1
            
            print(f"✓ Đã mở worksheet: {self.worksheet.title}")
            return True
        except Exception as e:
            print(f"✗ Lỗi mở spreadsheet: {e}")
            return False
    
    def clear_worksheet(self):
        """
        Xóa toàn bộ nội dung worksheet
        """
        try:
            self.worksheet.clear()
            print("✓ Đã xóa nội dung worksheet")
        except Exception as e:
            print(f"✗ Lỗi xóa worksheet: {e}")
    
    def export_data(self, data, clear_existing=True, sheet_name=None, van_ban=None, ngay_ban_hanh=None):
        """
        Xuất dữ liệu lên Google Sheets theo định dạng Compliance Checklist
        
        Args:
            data (list): Danh sách các entry (dict)
            clear_existing (bool): Xóa dữ liệu cũ hay không
            sheet_name (str): Tên worksheet
            van_ban (str): Tên văn bản
            ngay_ban_hanh (str): Ngày ban hành
            
        Returns:
            bool: True nếu xuất thành công
        """
        # Xác thực nếu chưa
        if not self.client:
            if not self.authenticate():
                return False
        
        # Mở spreadsheet
        if not self.spreadsheet:
            if not self.open_spreadsheet(sheet_name):
                return False
        
        try:
            # Xóa dữ liệu cũ nếu cần
            if clear_existing:
                self.clear_worksheet()
            
            # Chuẩn bị dữ liệu
            if not data:
                print("⚠ Không có dữ liệu để xuất")
                return False
            
            # Dòng 1 của Header
            header_row1 = [
                "STT", "Nội dung tuân thủ", "Loại hóa chất", "Hạng mục tuân thủ", 
                "Căn cứ pháp lý", "", "", "", "", "", # E-J
                "Thời gian dự kiến thực hiện", "Người phụ trách", "Đánh giá tuân thủ", "Ghi chú"
            ]
            
            # Dòng 2 của Header
            header_row2 = [
                "", "", "", "", # A-D merged vertical
                "Văn bản", "Ngày ban hành", "Ngày hiệu lực", "Điều khoản quy định", "Minh chứng", "Kết quả",
                "", "", "", "" # K-N merged vertical
            ]
            
            # Chuyển đổi dữ liệu thành dạng rows
            rows = [header_row1, header_row2]
            
            for idx, entry in enumerate(data, 1):
                ai_class = entry.get('ai_classification') or {}
                
                # Tạo chuỗi Điều khoản quy định: chuong + muc + dieu + khoan + diem
                clause_parts = []
                if entry.get('chuong'): clause_parts.append(entry.get('chuong'))
                if entry.get('muc'): clause_parts.append(entry.get('muc'))
                if entry.get('dieu'): clause_parts.append(entry.get('dieu'))
                if entry.get('khoan'): clause_parts.append(f"khoản {entry.get('khoan')}")
                if entry.get('diem'): clause_parts.append(f"điểm {entry.get('diem')}")
                
                dieu_khoan = ", ".join(clause_parts)
                
                # Lấy tên nhóm hóa chất (list to string)
                nhom_hc = ai_class.get('nhom_hoa_chat', [])
                if isinstance(nhom_hc, list):
                    nhom_hc = ", ".join(nhom_hc)
                
                row = [
                    idx,                                # A: STT
                    entry.get('noi_dung', ''),         # B: Nội dung tuân thủ
                    nhom_hc,                            # C: Loại hóa chất
                    ai_class.get('ten_hang_muc', ''),   # D: Hạng mục tuân thủ
                    van_ban or "",         # E: Văn bản
                    ngay_ban_hanh or "",                # F: Ngày ban hành
                    "01/01/2026",                      # G: Ngày hiệu lực (mặc định)
                    dieu_khoan,                         # H: Điều khoản quy định
                    "",                                 # I: Minh chứng
                    "",                                 # J: Kết quả
                    "",                                 # K: Thời gian dự kiến thực hiện
                    "",                                 # L: Người phụ trách
                    "",                                 # M: Đánh giá tuân thủ
                    ai_class.get('ghi_chu_ai', '')      # N: Ghi chú
                ]
                rows.append(row)
            
            # Ghi dữ liệu vào sheet
            self.worksheet.update('A1', rows, value_input_option='RAW')
            
            # Format header và merge cells
            self._format_compliance_header()
            
            # Thêm metadata
            self._add_metadata(len(data))
            
            print(f"✓ Đã xuất {len(data)} dòng dữ liệu lên Google Sheets (Compliance Checklist format)")
            print(f"  Link: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi xuất dữ liệu: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _format_compliance_header(self):
        """
        Format dòng tiêu đề phức hợp (merge cells, màu sắc)
        """
        try:
            # 1. Merge các ô dọc (A1:A2, B1:B2, etc.)
            merge_ranges = [
                'A1:A2', 'B1:B2', 'C1:C2', 'D1:D2', # STT -> Hạng mục
                'E1:J1', # Căn cứ pháp lý (ngang)
                'K1:K2', 'L1:L2', 'M1:M2', 'N1:N2'  # Phía sau
            ]
            
            for cell_range in merge_ranges:
                self.worksheet.merge_cells(cell_range)
            
            # 2. Định dạng màu sắc và alignment cho Header (Dòng 1 & 2)
            # Blue color for main headers
            blue_bg = {'red': 0.0, 'green': 0.44, 'blue': 0.73} # Navy blue
            # Orange/Amber for sub-headers
            orange_bg = {'red': 1.0, 'green': 0.75, 'blue': 0.0}
            
            # Toàn bộ header row 1 & 2
            self.worksheet.format('A1:N2', {
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}},
                'horizontalAlignment': 'CENTER',
                'verticalAlignment': 'MIDDLE',
                'borders': {
                    'top': {'style': 'SOLID'},
                    'bottom': {'style': 'SOLID'},
                    'left': {'style': 'SOLID'},
                    'right': {'style': 'SOLID'}
                }
            })
            
            # Background blue cho các ô Row 1
            self.worksheet.format('A1:N1', {'backgroundColor': blue_bg})
            
            # Background orange cho các sub-headers ở Row 2 (E2:J2)
            self.worksheet.format('E2:J2', {
                'backgroundColor': orange_bg,
                'textFormat': {'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}} # Black text for orange
            })
            
            # Auto-resize columns
            self.worksheet.columns_auto_resize(0, 13)
            
        except Exception as e:
            print(f"⚠ Không thể format header: {e}")
    
    def _add_metadata(self, row_count):
        """
        Thêm metadata vào sheet (thời gian xuất, số dòng)
        
        Args:
            row_count (int): Số dòng dữ liệu
        """
        try:
            # Tìm worksheet metadata hoặc tạo mới
            try:
                meta_sheet = self.spreadsheet.worksheet('Metadata')
            except gspread.WorksheetNotFound:
                meta_sheet = self.spreadsheet.add_worksheet(
                    title='Metadata',
                    rows=10,
                    cols=2
                )
            
            # Ghi metadata
            metadata = [
                ['Thông tin xuất dữ liệu', ''],
                ['Thời gian', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Số dòng dữ liệu', row_count],
                ['Worksheet', self.worksheet.title]
            ]
            
            meta_sheet.update('A1', metadata)
            meta_sheet.format('A1:B1', {'textFormat': {'bold': True}})
            
        except Exception as e:
            print(f"⚠ Không thể thêm metadata: {e}")
    
    def append_data(self, data):
        """
        Nối thêm dữ liệu vào cuối sheet (không xóa dữ liệu cũ)
        
        Args:
            data (list): Danh sách các entry
            
        Returns:
            bool: True nếu thành công
        """
        try:
            rows = []
            for entry in data:
                row = [
                    entry.get('chuong', ''),
                    entry.get('muc', ''),
                    entry.get('tieu_de_muc', ''),
                    entry.get('dieu', ''),
                    entry.get('tieu_de_dieu', ''),
                    entry.get('khoan', ''),
                    entry.get('diem', ''),
                    entry.get('noi_dung', '')
                ]
                rows.append(row)
            
            self.worksheet.append_rows(rows, value_input_option='RAW')
            print(f"✓ Đã nối thêm {len(rows)} dòng dữ liệu")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi nối dữ liệu: {e}")
            return False
