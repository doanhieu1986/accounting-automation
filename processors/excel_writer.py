import pandas as pd
from typing import List, Dict, Any

class ExcelWriter:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.columns = [
            "Số giao dịch",
            "Số tham chiếu",
            "Ngày giao dịch",
            "Tên tài khoản",
            "Số tài khoản",
            "Nội dung thanh toán",
            "Source"
        ]

    def write(self, data: List[Dict[str, Any]]):
        """Ghi danh sách dữ liệu vào file Excel."""
        df = pd.DataFrame(data)
        
        # Đảm bảo các cột theo đúng thứ tự yêu cầu
        # Nếu cột nào thiếu thì gán rỗng
        for col in self.columns:
            if col not in df.columns:
                df[col] = ""
        
        df = df[self.columns]
        
        # Xuất ra Excel
        df.to_excel(self.output_path, index=False, engine='openpyxl')
        print(f"Đã lưu kết quả vào: {self.output_path}")
