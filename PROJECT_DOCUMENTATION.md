# Tài Liệu Dự Án: Chiết Xuất Thông Tin Kế Toán từ PDF

## 1. Tổng Quan Dự Án

**Mục tiêu:** Tự động hóa việc chiết xuất thông tin giao dịch từ các file PDF chứng từ kế toán của các ngân hàng.

**Input:** File PDF từ các ngân hàng (TPBank, Techcombank, v.v.)

**Output:** File Excel (.xlsx) chứa các thông tin được chiết xuất theo cột chuẩn:
- Số giao dịch
- Số tham chiếu
- Ngày giao dịch
- Tên tài khoản (người chuyển/nhận tiền)
- Số tài khoản (người chuyển/nhận tiền)
- Nội dung thanh toán

---

## 2. Kiến Trúc Hệ Thống

### Quy Trình Chính

```
File PDF đầu vào
    ↓
[main.py] - Điểm khởi đầu
    ↓
Duyệt danh sách file PDF
    ↓
Với mỗi file:
  1. Xác định loại ngân hàng (is_supported)
  2. Chọn Extractor phù hợp
  3. Chiết xuất dữ liệu
    ↓
[processors/excel_writer.py] - Ghi dữ liệu ra Excel
    ↓
File Excel đầu ra
```

### Design Pattern: Strategy Pattern

Dự án sử dụng **Strategy Pattern** để hỗ trợ nhiều định dạng PDF từ các ngân hàng khác nhau:

- **BaseExtractor** (base.py): Lớp trừu tượng định nghĩa interface
- **TPBankExtractor** (tpbank.py): Chiến lược chiết xuất cho TPBank
- **TechcombankExtractor** (techcombank.py): Chiến lược chiết xuất cho Techcombank

---

## 3. Cấu Trúc Thư Mục

```
accounting-automation/
├── main.py                      # Điểm khởi đầu chính của ứng dụng
├── chiet_xuat.py               # Script thử nghiệm riêng cho Techcombank
├── requirements.txt             # Danh sách thư viện cần thiết
├── extractors/                  # Folder chứa các Extractor (chiến lược)
│   ├── __init__.py
│   ├── base.py                 # Lớp trừu tượng BaseExtractor
│   ├── tpbank.py               # Extractor cho TPBank
│   └── techcombank.py          # Extractor cho Techcombank
├── processors/                  # Folder xử lý output
│   ├── __init__.py
│   └── excel_writer.py         # Ghi dữ liệu vào Excel
└── sample_pdfs/                # Thư mục chứa PDF mẫu
```

---

## 4. Chi Tiết Từng Folder và File

### 4.1 Root Files

#### `main.py` - Điểm Khởi Đầu Chính

**Mục đích:** Điều phối toàn bộ quy trình chiết xuất dữ liệu.

**Logic:**
1. Parse command line arguments (`--input`, `--output`)
2. Xác định file(s) cần xử lý (file đơn hoặc thư mục)
3. Khởi tạo danh sách Extractors (TPBank, Techcombank)
4. Với mỗi file PDF:
   - Duyệt qua các Extractors
   - Gọi `is_supported()` để kiểm tra ngân hàng
   - Gọi `extract()` để chiết xuất dữ liệu
   - Tập hợp kết quả
5. Ghi dữ liệu vào Excel bằng `ExcelWriter`

**Sử dụng:**
```bash
python main.py --input "GBC TCB NB.pdf" --output "ket_qua_chiet_xuat.xlsx"
python main.py --input "./sample_pdfs/" --output "ket_qua.xlsx"
```

#### `chiet_xuat.py` - Script Thử Nghiệm (Deprecated)

**Mục đích:** Script thử nghiệm riêng cho Techcombank, được viết trước khi refactor thành `main.py`.

**Tình trạng:** Không dùng nữa - `main.py` đã thay thế chức năng này.

**Lý do còn lại:** 
- Có thể dùng để test từng loại ngân hàng riêng lẻ
- Hoặc để tham khảo logic cũ

---

### 4.2 Folder `extractors/`

**Mục đích:** Chứa các lớp chiết xuất dữ liệu cho từng loại ngân hàng.

#### `base.py` - Lớp Trừu Tượng

**Mục đích:** Định nghĩa interface (hợp đồng) cho tất cả các Extractors.

**Các method trừu tượng:**

```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(file_path: str) -> List[Dict[str, Any]]:
        """
        Chiết xuất thông tin từ file PDF.
        Input: Đường dẫn file PDF
        Output: Danh sách các bản ghi (giao dịch)
        """
        
    @abstractmethod
    def is_supported(file_path: str) -> bool:
        """
        Kiểm tra xem file có được hỗ trợ bởi Extractor này không.
        Input: Đường dẫn file PDF
        Output: True/False
        """
```

**Lợi ích:**
- Đảm bảo tất cả Extractors đều tuân theo cùng một giao diện
- Cho phép dễ dàng thêm Extractors mới (VietcomBank, BIDV, v.v.)

---

#### `tpbank.py` - Extractor cho TPBank

**Mục đích:** Chiết xuất dữ liệu từ PDF của TPBank.

**Phương pháp:**
- **Text-based extraction** (không dùng OCR)
- PDF của TPBank chứa text layer, có thể extract trực tiếp

**Các bước:**

1. **`is_supported(file_path)`**
   - Mở file PDF với `pdfplumber`
   - Kiểm tra nếu trang đầu chứa từ khóa: "TPBank", "Tien Phong", "TIEN PHONG"
   - Trả về True nếu tìm thấy

2. **`extract(file_path)`**
   - Mở PDF và extract text từ trang đầu
   - Dùng regex để tìm các thông tin:
     
     | Trường | Regex Pattern |
     |--------|---------------|
     | Số giao dịch | `Mã giao dịch \(Transaction ID\):\s*(\S+)` |
     | Ngày giao dịch | `Ngày giao dịch \(Transaction date\):\s*([\d/]+)` |
     | Tên tài khoản | Split by `"Tên tài khoản (Account name):"` - lấy phần thứ 3 |
     | Số tài khoản | Split by `"Số tài khoản (Account no):"` - lấy phần thứ 3 |
     | Nội dung | `Nội dung \(Description\):\s*(.+)` |

   - Trả về danh sách chứa 1 bản ghi (dict)

**Ưu điểm:**
- Nhanh vì không cần OCR
- Chính xác cao vì dùng regex trên text gốc

**Nhược điểm:**
- Chỉ hoạt động nếu PDF có text layer
- Cần điều chỉnh regex nếu format thay đổi

---

#### `techcombank.py` - Extractor cho Techcombank

**Mục đích:** Chiết xuất dữ liệu từ PDF của Techcombank.

**Phương pháp:**
- **Image-based extraction** (dùng OCR)
- PDF của Techcombank thường là hình ảnh scan, cần OCR

**Các bước:**

1. **`__init__()`**
   - Khởi tạo PaddleOCR với tiếng Việt
   - Model sẽ được tải từ cache nếu đã có

2. **`is_supported(file_path)`**
   - Kiểm tra text layer có chứa "Techcombank" hoặc "TECHCOMBANK"
   - Hoặc kiểm tra nếu PDF chứa ảnh nhúng
   - Trả về True nếu thỏa điều kiện

3. **`_extract_image_from_pdf(file_path)` - Trích xuất ảnh**
   - Nếu PDF có ảnh nhúng:
     - Giải nén dữ liệu (zlib decompress)
     - Upscale 2x để OCR tốt hơn
   - Nếu PDF là text-based:
     - Render trang PDF thành hình ảnh (300 DPI)
   - Lưu vào `/tmp/tcb_extracted.png`

4. **`extract(file_path)` - Chiết xuất dữ liệu**

   **Bước 4.1: Chạy OCR**
   - Dùng PaddleOCR trên ảnh để nhận diện text
   - OCR trả về:
     - `rec_texts`: danh sách text nhận diện được
     - `rec_polys`: tọa độ của mỗi text (4 góc của box)

   **Bước 4.2: Tổ chức dữ liệu theo hàng (visual lines)**
   - Lấy tọa độ y (trung bình) của mỗi text
   - Gom các text có cùng y (sai số < 15 pixel) vào 1 "visual line"
   - Mục đích: Phục hồi cấu trúc bảng ban đầu

   ```
   Text từ OCR:        Visual Lines:
   [ID]  [Value]   → [ID,    Value]
   [Name] [Value]  → [Name,  Value]
   ```

   **Bước 4.3: Tìm các trường dữ liệu**
   - Duyệt qua các visual lines
   - Tìm label keywords: "Số giao dịch", "Ngày giao dịch", v.v.
   - Gọi `get_value_next_to()` để lấy giá trị

   **Hàm `get_value_next_to()` - Lôgic tìm giá trị:**
   - **Ưu tiên 1:** Nếu label chứa dấu `:`, lấy phần sau dấu
   - **Ưu tiên 2:** Lấy item tiếp theo cùng dòng (nếu nó không phải label khác)
   - **Ưu tiên 3:** Lấy text từ dòng tiếp theo cùng cột (x gần nhất)
   - **Fallback:** Trả về chuỗi rỗng

   **Ví dụ:**
   ```
   Visual Line 0: [Số giao dịch:] [12345]
   → get_value_next_to() → "12345"
   
   Visual Line 1: [Ngày giao dịch]
   Visual Line 2: [10/05/2024]
   → get_value_next_to() → "10/05/2024"
   ```

   **Bước 4.4: Trường đặc biệt "Người chuyển tiền"**
   - Tìm label "Người chuyển tiền"
   - Duyệt 10 dòng tiếp theo tìm "Tên tài khoản" và "Số tài khoản"
   - Dừng khi gặp "Người nhận tiền"

**Ưu điểm:**
- Hoạt động với PDF scan
- Linh hoạt xử lý nhiều format khác nhau

**Nhược điểm:**
- Chậm hơn (cần OCR)
- Độ chính xác phụ thuộc vất chất ảnh

---

### 4.3 Folder `processors/`

**Mục đích:** Xử lý và xuất kết quả cuối cùng.

#### `excel_writer.py` - Ghi Excel

**Mục đích:** Chuyển đổi dữ liệu thành file Excel.

**Logic:**

```python
class ExcelWriter:
    def __init__(self, output_path: str):
        # Khởi tạo với đường dẫn output
        # Định nghĩa các cột chuẩn
    
    def write(self, data: List[Dict[str, Any]]):
        # 1. Chuyển danh sách dict thành DataFrame (pandas)
        # 2. Đảm bảo tất cả cột chuẩn đều có (thêm cột rỗng nếu thiếu)
        # 3. Sắp xếp theo thứ tự cột chuẩn
        # 4. Ghi ra file Excel bằng openpyxl
```

**Cột xuất ra (theo thứ tự):**
1. Số giao dịch
2. Số tham chiếu
3. Ngày giao dịch
4. Tên tài khoản
5. Số tài khoản
6. Nội dung thanh toán

**Ví dụ:**
```python
data = [
    {
        "Số giao dịch": "TXN123",
        "Ngày giao dịch": "10/05/2024",
        "Nội dung thanh toán": "Thanh toán hoá đơn"
    }
]
writer = ExcelWriter("output.xlsx")
writer.write(data)
# → Excel file với các cột đầy đủ, các ô trống được điền ""
```

---

## 5. Mối Liên Hệ Giữa Các Script

```
main.py (Điều phối chính)
├─ Khởi tạo các Extractors
│  ├─ TPBankExtractor
│  │  └─ base.py (thừa kế)
│  │  └─ tpbank.py (implement)
│  │
│  └─ TechcombankExtractor
│     └─ base.py (thừa kế)
│     └─ techcombank.py (implement)
│
├─ Gọi is_supported() để xác định loại ngân hàng
├─ Gọi extract() để lấy dữ liệu
└─ Dùng ExcelWriter (processors/excel_writer.py)
   └─ Ghi toàn bộ kết quả vào file Excel

chiet_xuat.py (Deprecated - không dùng)
└─ Chứa logic cũ của Techcombank (được di chuyển vào techcombank.py)
```

---

## 6. Flow Chi Tiết - Ví Dụ Thực Tế

### Scenario: Xử lý 2 file PDF (1 TPBank, 1 Techcombank)

```
1. Người dùng chạy:
   $ python main.py --input "./sample_pdfs/" --output "ket_qua.xlsx"

2. main.py:
   - Parse arguments: input="./sample_pdfs/", output="ket_qua.xlsx"
   - Tìm tất cả .pdf trong thư mục → [file1.pdf, file2.pdf]
   
3. Xử lý file1.pdf (TPBank):
   - TPBankExtractor.is_supported(file1.pdf) → True
   - TPBankExtractor.extract(file1.pdf)
     → Regex extract text → Dict
     → {Số giao dịch: "TXN001", Ngày: "10/05/2024", ...}
   
4. Xử lý file2.pdf (Techcombank):
   - TPBankExtractor.is_supported(file2.pdf) → False
   - TechcombankExtractor.is_supported(file2.pdf) → True
   - TechcombankExtractor.extract(file2.pdf)
     → Extract image → Run OCR → Sắp xếp visual lines
     → Tìm từng trường → Dict
     → {Số giao dịch: "TCB002", Ngày: "11/05/2024", ...}

5. Gộp kết quả:
   all_results = [
       {Số giao dịch: "TXN001", Ngày: "10/05/2024", ...},
       {Số giao dịch: "TCB002", Ngày: "11/05/2024", ...}
   ]

6. Ghi Excel:
   ExcelWriter.write(all_results)
   → Tạo DataFrame
   → Đảm bảo 6 cột chuẩn
   → Xuất file "ket_qua.xlsx"

7. Output:
   ket_qua.xlsx
   ├─ Row 1 (Header): Số giao dịch | Số tham chiếu | Ngày giao dịch | ...
   ├─ Row 2: TXN001 | | 10/05/2024 | ...
   └─ Row 3: TCB002 | | 11/05/2024 | ...
```

---

## 7. Cách Mở Rộng - Thêm Ngân Hàng Mới

**Để hỗ trợ ngân hàng mới (ví dụ: VietcomBank):**

1. **Tạo file mới:** `extractors/vietcombank.py`

2. **Implement class:**
```python
from .base import BaseExtractor

class VietcombankExtractor(BaseExtractor):
    def is_supported(self, file_path: str) -> bool:
        # Kiểm tra file có phải VietcomBank không
        
    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        # Chiết xuất dữ liệu từ VietcomBank PDF
```

3. **Thêm vào main.py:**
```python
from extractors.vietcombank import VietcombankExtractor

extractors = [
    TPBankExtractor(),
    TechcombankExtractor(),
    VietcombankExtractor(),  # ← Thêm dòng này
]
```

4. **Hoàn tất!** Ứng dụng sẽ tự động hỗ trợ VietcomBank.

---

## 8. Yêu Cầu Thư Viện (requirements.txt)

```
pdfplumber         # Đọc file PDF
paddleocr          # OCR (text recognition)
pandas             # Xử lý dữ liệu, ghi Excel
openpyxl           # Engine ghi Excel
Pillow (PIL)       # Xử lý hình ảnh
```

**Cài đặt:**
```bash
pip install -r requirements.txt
```

---

## 9. Tổng Kết Kiến Trúc

| Thành Phần | Chức Năng | Kiểu Dữ Liệu |
|-----------|----------|-------------|
| **main.py** | Điều phối chính, quản lý flow | - |
| **BaseExtractor** | Interface chung cho extractors | Abstract class |
| **TPBankExtractor** | Chiết xuất TPBank (text-based) | Class |
| **TechcombankExtractor** | Chiết xuất Techcombank (OCR) | Class |
| **ExcelWriter** | Ghi dữ liệu ra Excel | Class |
| **chiet_xuat.py** | Script thử nghiệm cũ | Deprecated |

---

## 10. Lợi Ích của Thiết Kế Hiện Tại

✅ **Dễ mở rộng:** Thêm ngân hàng mới chỉ cần 1 class mới
✅ **Dễ bảo trì:** Logic của mỗi ngân hàng tách biệt
✅ **Dễ test:** Có thể test từng extractor riêng lẻ
✅ **Tái sử dụng:** ExcelWriter có thể dùng cho bất kỳ dữ liệu nào
✅ **Linh hoạt:** Hỗ trợ cả text-based và image-based PDFs
