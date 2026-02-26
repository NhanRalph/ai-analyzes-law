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
    
    def export_data(self, data, clear_existing=True, sheet_name=None):
        """
        Xuất dữ liệu lên Google Sheets
        
        Args:
            data (list): Danh sách các entry (dict)
            clear_existing (bool): Xóa dữ liệu cũ hay không
            sheet_name (str): Tên worksheet
            
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
            
            # Tiêu đề cột
            headers = ['chuong', 'muc', 'tieu_de_muc', 'dieu', 'tieu_de_dieu', 'khoan', 'diem', 'noi_dung']
            
            # Chuyển đổi dữ liệu thành dạng rows
            rows = [headers]
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
            
            # Ghi dữ liệu vào sheet
            self.worksheet.update('A1', rows, value_input_option='RAW')
            
            # Format header
            self._format_header()
            
            # Thêm metadata
            self._add_metadata(len(data))
            
            print(f"✓ Đã xuất {len(data)} dòng dữ liệu lên Google Sheets")
            print(f"  Link: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi xuất dữ liệu: {e}")
            return False
    
    def _format_header(self):
        """
        Format dòng tiêu đề (bôi đậm, màu nền)
        """
        try:
            # Định dạng header row (dòng 1)
            self.worksheet.format('A1:H1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                'horizontalAlignment': 'CENTER',
                'borders': {
                    'top': {'style': 'SOLID'},
                    'bottom': {'style': 'SOLID'},
                    'left': {'style': 'SOLID'},
                    'right': {'style': 'SOLID'}
                }
            })
            
            # Auto-resize columns
            self.worksheet.columns_auto_resize(0, 7)
            
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
