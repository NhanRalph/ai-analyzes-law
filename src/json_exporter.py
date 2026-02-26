"""
Module xuất dữ liệu ra file JSON
"""

import json
import os
from datetime import datetime

class JSONExporter:
    """
    Class xuất dữ liệu ra file JSON
    """
    
    def __init__(self, output_dir='output'):
        """
        Khởi tạo JSONExporter
        
        Args:
            output_dir (str): Thư mục đầu ra
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """
        Đảm bảo thư mục output tồn tại
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def export_flat(self, data, filename=None):
        """
        Xuất dữ liệu dạng phẳng ra JSON
        
        Args:
            data (list): Danh sách các entry
            filename (str): Tên file output (tùy chọn)
            
        Returns:
            str: Đường dẫn file đã lưu
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'legal_data_flat_{timestamp}.json'
        
        filepath = os.path.join(self.output_dir, filename)
        
        output = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'total_entries': len(data),
                'format': 'flat'
            },
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Đã xuất dữ liệu phẳng ra: {filepath}")
        return filepath
    
    def export_nested(self, nested_data, filename=None):
        """
        Xuất dữ liệu dạng cây nested ra JSON
        
        Args:
            nested_data (dict): Cấu trúc cây nested
            filename (str): Tên file output (tùy chọn)
            
        Returns:
            str: Đường dẫn file đã lưu
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'legal_data_nested_{timestamp}.json'
        
        filepath = os.path.join(self.output_dir, filename)
        
        output = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'total_chapters': len(nested_data.get('chapters', [])),
                'format': 'nested'
            },
            'structure': nested_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Đã xuất dữ liệu nested ra: {filepath}")
        return filepath
    
    def export_both(self, flat_data, nested_data, base_filename=None):
        """
        Xuất cả hai dạng dữ liệu
        
        Args:
            flat_data (list): Dữ liệu dạng phẳng
            nested_data (dict): Dữ liệu dạng cây
            base_filename (str): Tên cơ sở cho file (tùy chọn)
            
        Returns:
            tuple: (flat_filepath, nested_filepath)
        """
        if base_filename:
            flat_file = f"{base_filename}_flat.json"
            nested_file = f"{base_filename}_nested.json"
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            flat_file = f'legal_data_flat_{timestamp}.json'
            nested_file = f'legal_data_nested_{timestamp}.json'
        
        flat_path = self.export_flat(flat_data, flat_file)
        nested_path = self.export_nested(nested_data, nested_file)
        
        return flat_path, nested_path
