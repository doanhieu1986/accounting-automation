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


# Hướng dẫn sử dụng Hệ thống Tự động Chiết xuất Chứng từ

Hệ thống đã được xây dựng để xử lý các file PDF chứng từ (đặc biệt là Techcombank) bằng công nghệ OCR (PaddleOCR) để đảm bảo độ chính xác cao nhất ngay cả khi PDF chỉ chứa ảnh.

## Kết quả đạt được

Hệ thống đã chiết xuất thành công các thông tin từ file mẫu `GBC TCB NB.pdf`:

| Trường thông tin | Giá trị chiết xuất |
|------------------|-------------------|
| **Số giao dịch** | FT26126128607100\BNK |
| **Số tham chiếu**| 213116324342575.010001 |
| **Ngày giao dịch**| 06/05/2026 |
| **Tên tài khoản đối ứng**| NGUYEN THI MY DUYEN |
| **Số tài khoản đối ứng**| 19073746290010 |
| **Nội dung thanh toán**| M0261613371,NGUYEN THI MY DUYEN... |

## Cách chạy hệ thống

1. **Cài đặt môi trường** (nếu chưa có):
   ```bash
   pip install paddlepaddle paddleocr pdfplumber openpyxl pandas
   ```

2. **Chạy chiết xuất**:
   Bạn có thể truyền vào 1 file hoặc cả 1 thư mục chứa nhiều file PDF.
   ```bash
   python3 main.py --input "đường/dẫn/file/pdf" --output "ket_qua.xlsx"
   ```

3. **Cấu trúc project**:
   - `main.py`: File chạy chính.
   - `extractors/`: Chứa logic xử lý cho từng ngân hàng (hiện tại là Techcombank).
   - `processors/`: Chứa logic ghi file Excel.
   - `config/`: Chứa các thiết lập hệ thống.

## Lưu ý kỹ thuật

- **Công nghệ**: Sử dụng **PaddleOCR v3** với model tiếng Việt (vi) để nhận diện văn bản từ ảnh nhúng trong PDF.
- **Xử lý không gian**: Hệ thống sử dụng thuật toán gom dòng (spatial grouping) để nhận diện nhãn (label) và giá trị (value) chính xác dựa trên tọa độ hình ảnh, giúp xử lý tốt các layout dạng bảng phức tạp.
- **Mở rộng**: Bạn có thể dễ dàng thêm các ngân hàng khác bằng cách tạo thêm file trong thư mục `extractors/` kế thừa từ `BaseExtractor`.

> [!TIP]
> File kết quả chính thức đã được lưu tại: [ket_qua_chinh_thuc.xlsx](file:///Users/doanhieu/accounting-automation/ket_qua_chinh_thuc.xlsx)
