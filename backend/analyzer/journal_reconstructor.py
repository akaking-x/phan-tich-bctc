# backend/analyzer/journal_reconstructor.py

"""
Tái tạo bút toán kế toán từ bảng Cân đối Tài khoản (CĐTK).

Logic: So sánh PS Nợ và PS Có của từng TK,
kết hợp với quan hệ đối ứng thông dụng để suy ra bút toán.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class JournalEntry:
    """Một bút toán kế toán được tái tạo."""
    description: str
    debit_account: str
    debit_account_name: str
    credit_account: str
    credit_account_name: str
    amount: float
    category: str           # "operating", "investing", "financing"
    confidence: float       # 0-1, độ tin cậy của suy luận
    notes: Optional[str] = None


class JournalReconstructor:
    """
    Tái tạo bút toán kế toán từ bảng CĐTK.

    Logic: So sánh PS Nợ và PS Có của từng TK,
    kết hợp với quan hệ đối ứng thông dụng để suy ra bút toán.
    """

    # Các cặp đối ứng phổ biến (debit_tk, credit_tk, description)
    COMMON_PAIRS = [
        # Góp vốn
        ("111", "411", "Góp vốn bằng tiền mặt"),
        ("112", "411", "Góp vốn qua ngân hàng"),
        # Gửi/rút tiền NH
        ("112", "111", "Nộp tiền mặt vào ngân hàng"),
        ("111", "112", "Rút tiền mặt từ ngân hàng"),
        # DT tài chính
        ("112", "515", "Lãi tiền gửi ngân hàng"),
        # CP tài chính
        ("635", "112", "Phí dịch vụ ngân hàng"),
        ("635", "111", "Chi phí tài chính (tiền mặt)"),
        # CP QLDN
        ("642", "111", "Chi phí QLDN (tiền mặt)"),
        ("642", "112", "Chi phí QLDN (chuyển khoản)"),
        ("642", "331", "Chi phí QLDN (nợ NCC)"),
        # VAT
        ("133", "111", "Thuế GTGT đầu vào (tiền mặt)"),
        ("133", "112", "Thuế GTGT đầu vào (chuyển khoản)"),
        ("133", "331", "Thuế GTGT đầu vào (nợ NCC)"),
        # Mua hàng
        ("156", "111", "Mua hàng hoá (tiền mặt)"),
        ("156", "112", "Mua hàng hoá (chuyển khoản)"),
        ("156", "331", "Mua hàng hoá (nợ NCC)"),
        # Bán hàng
        ("111", "511", "Bán hàng thu tiền mặt"),
        ("112", "511", "Bán hàng thu chuyển khoản"),
        ("131", "511", "Bán hàng ghi nợ"),
        # Giá vốn
        ("632", "156", "Xuất kho hàng bán"),
        # Kết chuyển
        ("511", "911", "Kết chuyển doanh thu"),
        ("515", "911", "Kết chuyển DT tài chính"),
        ("711", "911", "Kết chuyển thu nhập khác"),
        ("911", "632", "Kết chuyển giá vốn"),
        ("911", "635", "Kết chuyển CP tài chính"),
        ("911", "642", "Kết chuyển CP QLDN"),
        ("911", "811", "Kết chuyển CP khác"),
        ("911", "821", "Kết chuyển CP thuế TNDN"),
        # Kết chuyển lãi/lỗ
        ("911", "421", "Kết chuyển lãi"),
        ("421", "911", "Kết chuyển lỗ"),
        # Lương
        ("642", "334", "Chi phí lương"),
        ("334", "111", "Trả lương tiền mặt"),
        ("334", "112", "Trả lương chuyển khoản"),
        # Thuế
        ("821", "3334", "Thuế TNDN phải nộp"),
        ("3334", "112", "Nộp thuế TNDN"),
        ("3331", "112", "Nộp thuế GTGT"),
    ]

    def __init__(self, cdtk_data: Dict[str, Any], account_map: Dict):
        self.ps = cdtk_data.get("SoPhatSinhTrongKy", {})
        self.account_map = account_map

    def reconstruct(self) -> List[JournalEntry]:
        """
        Tái tạo bút toán từ phát sinh Nợ/Có.

        Thuật toán:
        1. Lấy tất cả TK có phát sinh != 0
        2. Với mỗi cặp đối ứng phổ biến, kiểm tra xem
           PS Nợ bên này có khớp PS Có bên kia không
        3. Phân bổ số tiền theo min(PS Nợ, PS Có)
        4. Số dư còn lại đánh dấu "chưa xác định"
        """
        no_ps = self.ps.get("no", {})
        co_ps = self.ps.get("co", {})

        # Tạo bản sao để trừ dần
        no_remaining: Dict[str, float] = {}
        co_remaining: Dict[str, float] = {}

        for ct_key, val in no_ps.items():
            if ct_key == "tongCong" or not val:
                continue
            tk = self._ct_to_tk(ct_key)
            if tk:
                no_remaining[tk] = no_remaining.get(tk, 0) + float(val)

        for ct_key, val in co_ps.items():
            if ct_key == "tongCong" or not val:
                continue
            tk = self._ct_to_tk(ct_key)
            if tk:
                co_remaining[tk] = co_remaining.get(tk, 0) + float(val)

        entries: List[JournalEntry] = []

        # Match theo cặp đối ứng
        for debit_tk, credit_tk, desc in self.COMMON_PAIRS:
            no_amt = no_remaining.get(debit_tk, 0)
            co_amt = co_remaining.get(credit_tk, 0)

            if no_amt > 0 and co_amt > 0:
                amount = min(no_amt, co_amt)
                entries.append(JournalEntry(
                    description=desc,
                    debit_account=debit_tk,
                    debit_account_name=self._tk_name(debit_tk),
                    credit_account=credit_tk,
                    credit_account_name=self._tk_name(credit_tk),
                    amount=amount,
                    category=self._categorize(debit_tk, credit_tk),
                    confidence=0.8,
                ))
                no_remaining[debit_tk] -= amount
                co_remaining[credit_tk] -= amount

        # Báo cáo phần chưa match
        for tk, amt in no_remaining.items():
            if amt > 0.5:  # tolerance
                entries.append(JournalEntry(
                    description="PS Nợ chưa xác định đối ứng",
                    debit_account=tk,
                    debit_account_name=self._tk_name(tk),
                    credit_account="???",
                    credit_account_name="Chưa xác định",
                    amount=amt,
                    category="unknown",
                    confidence=0.0,
                    notes="Cần kiểm tra sổ chi tiết",
                ))

        for tk, amt in co_remaining.items():
            if amt > 0.5:  # tolerance
                entries.append(JournalEntry(
                    description="PS Có chưa xác định đối ứng",
                    debit_account="???",
                    debit_account_name="Chưa xác định",
                    credit_account=tk,
                    credit_account_name=self._tk_name(tk),
                    amount=amt,
                    category="unknown",
                    confidence=0.0,
                    notes="Cần kiểm tra sổ chi tiết",
                ))

        return entries

    def _ct_to_tk(self, ct_key: str) -> Optional[str]:
        """Convert ct111 -> '111', ct1121 -> '1121', etc."""
        info = self.account_map.get(ct_key)
        return info["tk"] if info else None

    def _tk_name(self, tk: str) -> str:
        """Tra tên tài khoản từ mã TK."""
        for info in self.account_map.values():
            if info.get("tk") == tk:
                return info["name"]
        return tk

    @staticmethod
    def _categorize(debit_tk: str, credit_tk: str) -> str:
        """Phân loại bút toán: financing, investing, operating."""
        financing_tks = {"411", "341", "419"}
        investing_tks = {"211", "217", "228", "241", "121", "128"}

        if debit_tk in financing_tks or credit_tk in financing_tks:
            return "financing"
        if debit_tk in investing_tks or credit_tk in investing_tks:
            return "investing"
        return "operating"
