import os
import zlib
import re
from PIL import Image
import pdfplumber
from paddleocr import PaddleOCR
from .base import BaseExtractor
from typing import List, Dict, Any

class TechcombankExtractor(BaseExtractor):
    def __init__(self):
        # Khởi tạo PaddleOCR - sẽ dùng cache nếu đã tải model
        self.ocr = PaddleOCR(use_textline_orientation=True, lang='vi')

    def is_supported(self, file_path: str) -> bool:
        # Kiểm tra nhanh nội dung text (nếu có) hoặc metadata
        try:
            with pdfplumber.open(file_path) as pdf:
                # Thử tìm keyword trong text layer (footer thường có text)
                text = pdf.pages[0].extract_text() or ""
                if "Techcombank" in text or "TECHCOMBANK" in text:
                    return True
                
                # Nếu không có text layer, kiểm tra xem có ảnh logo TCB không (phức tạp hơn)
                # Tạm thời check tên file hoặc mặc định hỗ trợ nếu có ảnh
                if len(pdf.pages[0].images) > 0:
                    return True
        except:
            pass
        return False

    def _extract_image_from_pdf(self, file_path: str) -> str:
        """Trích xuất ảnh từ PDF và lưu vào file tạm."""
        temp_image_path = "/tmp/tcb_extracted.png"
        with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[0]
            if not page.images:
                # Nếu không có ảnh nhúng, render cả trang
                img = page.to_image(resolution=300).original
            else:
                img_info = page.images[0]
                stream = img_info['stream']
                raw_data = stream.get_rawdata()
                decompressed = zlib.decompress(raw_data)
                w, h = img_info['srcsize']
                img = Image.frombytes('RGB', (w, h), decompressed)
                # Upscale để OCR tốt hơn
                img = img.resize((w*2, h*2), Image.LANCZOS)
            
            img.save(temp_image_path)
        return temp_image_path

    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        image_path = self._extract_image_from_pdf(file_path)
        
        # Chạy OCR
        ocr_results = self.ocr.predict(image_path)
        
        # Thu thập toàn bộ text theo dòng để phân tích
        lines = []
        for result in ocr_results:
            texts = result['rec_texts']
            polys = result['rec_polys']
            # zip 3 items but only unpack 2 - fixed
            for text, poly in zip(texts, polys):
                # Lưu text, tọa độ y (trung bình của 4 góc) và x
                y_coords = [p[1] for p in poly]
                avg_y = sum(y_coords) / len(y_coords)
                lines.append({"text": text, "y": avg_y, "x": poly[0][0], "poly": poly})

        # Gom các dòng có cùng y (sai số nhỏ) thành 1 visual line
        visual_lines = []
        lines.sort(key=lambda x: x['y'])
        
        if lines:
            current_row = [lines[0]]
            for i in range(1, len(lines)):
                if abs(lines[i]['y'] - current_row[0]['y']) < 15: # Ngưỡng 15 pixel
                    current_row.append(lines[i])
                else:
                    current_row.sort(key=lambda x: x['x'])
                    visual_lines.append(current_row)
                    current_row = [lines[i]]
            current_row.sort(key=lambda x: x['x'])
            visual_lines.append(current_row)

        extracted_data = {
            "Số giao dịch": "",
            "Số tham chiếu": "",
            "Ngày giao dịch": "",
            "Tên tài khoản": "",
            "Số tài khoản": "",
            "Nội dung thanh toán": ""
        }

        def get_value_next_to(label_keywords, row_index, item_index):
            """Tìm giá trị nằm bên phải hoặc dòng ngay dưới của label."""
            row = visual_lines[row_index]
            
            # Nếu item hiện tại có dấu :, lấy phần sau dấu :
            current_text = row[item_index]['text']
            if ":" in current_text:
                parts = current_text.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    val = parts[1].strip()
                    # Loại bỏ các label khác vô tình bị dính vào (ví dụ label cột bên phải)
                    for kw in ["Số tài khoản", "só tài khon", "Tên tài khoản", "Tên tài khoàn"]:
                        if kw in val:
                            val = val.split(kw)[0].strip()
                    return val
            
            # Thử lấy item tiếp theo cùng dòng nếu item đó KHÔNG phải là một label khác
            if item_index + 1 < len(row):
                next_item_text = row[item_index + 1]['text']
                # Check if next_item is another known label
                is_another_label = any(kw in next_item_text for kw in ["Số tài khoản", "só tài khon", "Tên tài khoản", "Tên tài khoàn", "Tại Ngân hàng", "Ti Ngân hàng"])
                if not is_another_label:
                    return next_item_text.strip()
            
            # Thử dòng tiếp theo
            if row_index + 1 < len(visual_lines):
                next_row = visual_lines[row_index + 1]
                if len(next_row) == 1:
                    return next_row[0]['text'].strip()
                for item in next_row:
                    if abs(item['x'] - row[item_index]['x']) < 50:
                        return item['text'].strip()
            return ""

        for r_idx, row in enumerate(visual_lines):
            row_text = " ".join([item['text'] for item in row])
            
            for i, item in enumerate(row):
                text = item['text']
                
                if any(kw in text for kw in ["Số giao dịch", "Só giao dich"]):
                    extracted_data["Số giao dịch"] = get_value_next_to(["Số giao dịch", "Só giao dich"], r_idx, i)
                
                elif any(kw in text for kw in ["Số tham chiếu", "Só tham chiéu"]):
                    extracted_data["Số tham chiếu"] = get_value_next_to(["Số tham chiếu", "Só tham chiéu"], r_idx, i)

                elif any(kw in text for kw in ["Ngày giao dịch", "Ngày giao dch"]):
                    # Ngày thường nằm ở cột bên phải xa (x > 800)
                    for other in row:
                        if other['x'] > 800:
                            extracted_data["Ngày giao dịch"] = other['text'].strip()
                            break

                elif any(kw in text for kw in ["Người chuyển tiền", "Ngưi chuyn tin"]):
                    # Tìm thông tin người chuyển trong các dòng tiếp theo
                    for j in range(r_idx + 1, min(r_idx + 10, len(visual_lines))):
                        next_row_text = " ".join([it['text'] for it in visual_lines[j]])
                        if any(kw in next_row_text for kw in ["Tên tài khoản", "Tên tài khon"]):
                            extracted_data["Tên tài khoản"] = get_value_next_to(["Tên tài khoản", "Tên tài khon"], j, 0)
                        if any(kw in next_row_text for kw in ["Số tài khoản", "só tài khon"]):
                            extracted_data["Số tài khoản"] = get_value_next_to(["Số tài khoản", "só tài khon"], j, 0)
                        if "Người nhận tiền" in next_row_text or "Ngưi nhn tin" in next_row_text:
                            break

                elif any(kw in text for kw in ["Nội dung thanh toán", "Ni dung thanh toán"]):
                    extracted_data["Nội dung thanh toán"] = get_value_next_to(["Nội dung thanh toán", "Ni dung thanh toán"], r_idx, i)

        return [extracted_data]
