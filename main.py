import os
import argparse
from extractors.techcombank import TechcombankExtractor
from processors.excel_writer import ExcelWriter

def main():
    parser = argparse.ArgumentParser(description="Tự động chiết xuất thông tin kế toán từ PDF")
    parser.add_argument("--input", default="GBC TCB NB.pdf", help="Đường dẫn file PDF hoặc thư mục chứa PDF")
    parser.add_argument("--output", default="ket_qua_chiet_xuat.xlsx", help="Đường dẫn file Excel đầu ra")
    
    args = parser.parse_args()
    
    # Danh sách các file cần xử lý
    files_to_process = []
    if os.path.isdir(args.input):
        for f in os.listdir(args.input):
            if f.lower().endswith(".pdf"):
                files_to_process.append(os.path.join(args.input, f))
    else:
        files_to_process.append(args.input)

    if not files_to_process:
        print("Không tìm thấy file PDF nào để xử lý.")
        return

    # Khởi tạo extractor (Hiện tại mới có TCB)
    tcb_extractor = TechcombankExtractor()
    all_results = []

    for file_path in files_to_process:
        print(f"Đang xử lý: {file_path}...")
        if tcb_extractor.is_supported(file_path):
            try:
                results = tcb_extractor.extract(file_path)
                all_results.extend(results)
            except Exception as e:
                print(f"Lỗi khi xử lý {file_path}: {e}")
        else:
            print(f"Định dạng file {file_path} chưa được hỗ trợ.")

    # Ghi ra Excel
    if all_results:
        writer = ExcelWriter(args.output)
        writer.write(all_results)
    else:
        print("Không có dữ liệu nào được chiết xuất.")

if __name__ == "__main__":
    main()
