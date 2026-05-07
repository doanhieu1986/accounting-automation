from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Chiết xuất thông tin từ file PDF.
        Trả về danh sách các bản ghi (giao dịch).
        """
        pass

    @abstractmethod
    def is_supported(self, file_path: str) -> bool:
        """
        Kiểm tra xem file này có được hỗ trợ bởi extractor này không.
        """
        pass