import os
import zlib
import argparse
from PIL import Image
import pdfplumber
from paddleocr import PaddleOCR
import pandas as pd


COLUMNS = [
    "Số giao dịch",
    "Số tham chiếu",
    "Ngày giao dịch",
    "Tên tài khoản",
    "Số tài khoản",
    "Nội dung thanh toán",
]


def extract_image_from_pdf(file_path: str) -> str:
    temp_image_path = "/tmp/tcb_extracted.png"
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        if not page.images:
            img = page.to_image(resolution=300).original
        else:
            img_info = page.images[0]
            stream = img_info['stream']
            raw_data = stream.get_rawdata()
            decompressed = zlib.decompress(raw_data)
            w, h = img_info['srcsize']
            img = Image.frombytes('RGB', (w, h), decompressed)
            img = img.resize((w * 2, h * 2), Image.LANCZOS)
        img.save(temp_image_path)
    return temp_image_path


def is_techcombank(file_path: str) -> bool:
    try:
        with pdfplumber.open(file_path) as pdf:
            text = pdf.pages[0].extract_text() or ""
            if "Techcombank" in text or "TECHCOMBANK" in text:
                return True
            if len(pdf.pages[0].images) > 0:
                return True
    except:
        pass
    return False


def extract_transactions(file_path: str, ocr: PaddleOCR) -> list:
    image_path = extract_image_from_pdf(file_path)

    ocr_results = ocr.predict(image_path)

    lines = []
    for result in ocr_results:
        for text, poly in zip(result['rec_texts'], result['rec_polys']):
            y_coords = [p[1] for p in poly]
            avg_y = sum(y_coords) / len(y_coords)
            lines.append({"text": text, "y": avg_y, "x": poly[0][0], "poly": poly})

    visual_lines = []
    lines.sort(key=lambda x: x['y'])

    if lines:
        current_row = [lines[0]]
        for i in range(1, len(lines)):
            if abs(lines[i]['y'] - current_row[0]['y']) < 15:
                current_row.append(lines[i])
            else:
                current_row.sort(key=lambda x: x['x'])
                visual_lines.append(current_row)
                current_row = [lines[i]]
        current_row.sort(key=lambda x: x['x'])
        visual_lines.append(current_row)

    data = {col: "" for col in COLUMNS}

    def get_value_next_to(row_index, item_index):
        row = visual_lines[row_index]
        current_text = row[item_index]['text']
        if ":" in current_text:
            parts = current_text.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                val = parts[1].strip()
                for kw in ["Số tài khoản", "só tài khon", "Tên tài khoản", "Tên tài khoàn"]:
                    if kw in val:
                        val = val.split(kw)[0].strip()
                return val

        if item_index + 1 < len(row):
            next_text = row[item_index + 1]['text']
            is_label = any(kw in next_text for kw in [
                "Số tài khoản", "só tài khon", "Tên tài khoản",
                "Tên tài khoàn", "Tại Ngân hàng", "Ti Ngân hàng"
            ])
            if not is_label:
                return next_text.strip()

        if row_index + 1 < len(visual_lines):
            next_row = visual_lines[row_index + 1]
            if len(next_row) == 1:
                return next_row[0]['text'].strip()
            for item in next_row:
                if abs(item['x'] - row[item_index]['x']) < 50:
                    return item['text'].strip()
        return ""

    for r_idx, row in enumerate(visual_lines):
        for i, item in enumerate(row):
            text = item['text']

            if any(kw in text for kw in ["Số giao dịch", "Só giao dich"]):
                data["Số giao dịch"] = get_value_next_to(r_idx, i)

            elif any(kw in text for kw in ["Số tham chiếu", "Só tham chiéu"]):
                data["Số tham chiếu"] = get_value_next_to(r_idx, i)

            elif any(kw in text for kw in ["Ngày giao dịch", "Ngày giao dch"]):
                for other in row:
                    if other['x'] > 800:
                        data["Ngày giao dịch"] = other['text'].strip()
                        break

            elif any(kw in text for kw in ["Người chuyển tiền", "Ngưi chuyn tin"]):
                for j in range(r_idx + 1, min(r_idx + 10, len(visual_lines))):
                    next_row_text = " ".join([it['text'] for it in visual_lines[j]])
                    if any(kw in next_row_text for kw in ["Tên tài khoản", "Tên tài khon"]):
                        data["Tên tài khoản"] = get_value_next_to(j, 0)
                    if any(kw in next_row_text for kw in ["Số tài khoản", "só tài khon"]):
                        data["Số tài khoản"] = get_value_next_to(j, 0)
                    if "Người nhận tiền" in next_row_text or "Ngưi nhn tin" in next_row_text:
                        break

            elif any(kw in text for kw in ["Nội dung thanh toán", "Ni dung thanh toán"]):
                data["Nội dung thanh toán"] = get_value_next_to(r_idx, i)

    return [data]


def save_to_excel(records: list, output_path: str):
    df = pd.DataFrame(records)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"Đã lưu kết quả vào: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Chiết xuất thông tin kế toán từ PDF")
    parser.add_argument("--input", default="GBC TCB NB.pdf", help="File PDF hoặc thư mục chứa PDF")
    parser.add_argument("--output", default="ket_qua_chiet_xuat.xlsx", help="File Excel đầu ra")
    args = parser.parse_args()

    files = []
    if os.path.isdir(args.input):
        for f in os.listdir(args.input):
            if f.lower().endswith(".pdf"):
                files.append(os.path.join(args.input, f))
    else:
        files.append(args.input)

    if not files:
        print("Không tìm thấy file PDF nào.")
        return

    ocr = PaddleOCR(use_textline_orientation=True, lang='vi')
    all_records = []

    for file_path in files:
        print(f"Đang xử lý: {file_path}...")
        if not is_techcombank(file_path):
            print(f"  -> Định dạng chưa được hỗ trợ, bỏ qua.")
            continue
        try:
            records = extract_transactions(file_path, ocr)
            all_records.extend(records)
        except Exception as e:
            print(f"  -> Lỗi: {e}")

    if all_records:
        save_to_excel(all_records, args.output)
    else:
        print("Không có dữ liệu nào được chiết xuất.")


if __name__ == "__main__":
    main()
