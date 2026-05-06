"""
Cấu hình hệ thống chiết xuất chứng từ kế toán.
Sao chép file này thành settings_local.py và điền API key vào.
"""

import os

# Gemini API Key - lấy từ https://aistudio.google.com/app/apikey
# Ưu tiên đọc từ biến môi trường GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Model Gemini sử dụng (gemini-2.0-flash-lite miễn phí và đủ nhanh)
GEMINI_MODEL = "gemini-2.0-flash"

# Độ phân giải khi render PDF ra ảnh (DPI)
PDF_RENDER_DPI = 200

# Thư mục output mặc định
DEFAULT_OUTPUT_DIR = "."
DEFAULT_OUTPUT_FILENAME = "ket_qua_chiet_xuat.xlsx"

# Tên công ty của bạn (để loại trừ khỏi cột "tài khoản đối ứng")
# Điền tên công ty để hệ thống nhận biết đâu là tài khoản mình
OUR_COMPANY_KEYWORDS = [
    "VPS",
    "CHUNG KHOAN VPS",
    "CONG TY CO PHAN CHUNG KHOAN VPS",
]
