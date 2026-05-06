# Tự động chiết xuất chứng từ kế toán (Accounting Automation)

Hệ thống sử dụng Python và OCR để tự động hóa việc nhập liệu từ các file PDF chứng từ ngân hàng vào file Excel.

## Tính năng
- Trích xuất ảnh từ PDF nếu nội dung là ảnh nhúng.
- Sử dụng PaddleOCR (Local OCR) để nhận diện văn bản tiếng Việt chính xác.
- Thuật toán xử lý không gian (Spatial Processing) để ghép nối thông tin đúng vị trí.
- Hỗ trợ xử lý hàng loạt (Batch processing).
- Xuất kết quả ra Excel theo chuẩn yêu cầu.

## Cài đặt
```bash
pip install -r requirements.txt
```

## Sử dụng
```bash
python main.py --input "file_mau.pdf" --output "ket_qua.xlsx"
```

## Cấu trúc dự án
- `extractors/`: Chứa logic trích xuất riêng cho từng loại chứng từ/ngân hàng.
- `processors/`: Xử lý dữ liệu và xuất file.
- `main.py`: Entry point của ứng dụng.
