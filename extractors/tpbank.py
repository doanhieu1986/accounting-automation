import re
import pdfplumber
from .base import BaseExtractor
from typing import List, Dict, Any


class TPBankExtractor(BaseExtractor):

    def is_supported(self, file_path: str) -> bool:
        try:
            with pdfplumber.open(file_path) as pdf:
                text = pdf.pages[0].extract_text() or ""
                return "TPBank" in text or "Tien Phong" in text or "TIEN PHONG" in text
        except:
            return False

    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        with pdfplumber.open(file_path) as pdf:
            text = pdf.pages[0].extract_text() or ""

        data = {
            "Số giao dịch": "",
            "Số tham chiếu": "",
            "Ngày giao dịch": "",
            "Tên tài khoản": "",
            "Số tài khoản": "",
            "Nội dung thanh toán": "",
            "Source": "TPBank",
        }

        # Số giao dịch
        m = re.search(r'Mã giao dịch \(Transaction ID\):\s*(\S+)', text)
        if m:
            data["Số giao dịch"] = m.group(1).strip()

        # Ngày giao dịch
        m = re.search(r'Ngày giao dịch \(Transaction date\):\s*([\d/]+)', text)
        if m:
            data["Ngày giao dịch"] = m.group(1).strip()

        # Tên tài khoản đối ứng (bên ghi nợ - người chuyển tiền)
        # Dòng có dạng: "... Tên tài khoản (Account name): TEN_CONG_TY Tên tài khoản (Account name): TEN_DOI_UNG"
        name_parts = text.split("Tên tài khoản (Account name):")
        if len(name_parts) >= 3:
            raw = name_parts[2].strip().splitlines()[0].strip()
            data["Tên tài khoản"] = raw

        # Số tài khoản đối ứng (bên ghi nợ)
        acc_parts = text.split("Số tài khoản (Account no):")
        if len(acc_parts) >= 3:
            raw = acc_parts[2].strip().split()[0].strip()
            data["Số tài khoản"] = raw

        # Nội dung thanh toán
        m = re.search(r'Nội dung \(Description\):\s*(.+)', text)
        if m:
            data["Nội dung thanh toán"] = m.group(1).strip()

        return [data]
