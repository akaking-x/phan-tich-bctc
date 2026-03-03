"""
Model cho Bút toán kế toán tái tạo (Journal Entry).
Được suy ra từ bảng CĐTK dựa trên quan hệ đối ứng tài khoản.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class JournalEntry(BaseModel):
    """
    Một bút toán kế toán được tái tạo từ dữ liệu CĐTK.

    Bút toán bao gồm:
    - TK Nợ (debit) và TK Có (credit)
    - Số tiền
    - Phân loại dòng tiền
    - Độ tin cậy của suy luận
    """

    model_config = {"populate_by_name": True}

    description: str = Field(
        ..., description="Diễn giải bút toán"
    )
    debit_account: str = Field(
        ..., description="Mã TK ghi Nợ"
    )
    debit_account_name: str = Field(
        default="", description="Tên TK ghi Nợ"
    )
    credit_account: str = Field(
        ..., description="Mã TK ghi Có"
    )
    credit_account_name: str = Field(
        default="", description="Tên TK ghi Có"
    )
    amount: float = Field(
        ..., ge=0, description="Số tiền (luôn dương)"
    )
    category: Literal[
        "operating", "investing", "financing", "unknown"
    ] = Field(
        default="operating",
        description="Phân loại dòng tiền",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy suy luận (0.0 - 1.0)",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Ghi chú bổ sung (cần kiểm tra, giả định...)",
    )

    @property
    def is_identified(self) -> bool:
        """Bút toán đã xác định được đối ứng hay chưa."""
        return self.credit_account != "???" and self.confidence > 0

    @property
    def category_vi(self) -> str:
        """Tên loại dòng tiền tiếng Việt."""
        mapping = {
            "operating": "Hoạt động kinh doanh",
            "investing": "Hoạt động đầu tư",
            "financing": "Hoạt động tài chính",
            "unknown": "Chưa phân loại",
        }
        return mapping.get(self.category, "Chưa phân loại")


class JournalSummary(BaseModel):
    """Tổng hợp kết quả tái tạo bút toán."""

    model_config = {"populate_by_name": True}

    entries: List[JournalEntry] = Field(
        default_factory=list,
        description="Danh sách bút toán tái tạo",
    )
    total_entries: int = Field(
        default=0,
        description="Tổng số bút toán",
    )
    identified_entries: int = Field(
        default=0,
        description="Số bút toán đã xác định đối ứng",
    )
    unidentified_entries: int = Field(
        default=0,
        description="Số bút toán chưa xác định đối ứng",
    )
    total_amount: float = Field(
        default=0.0,
        description="Tổng giá trị bút toán",
    )
    by_category: dict = Field(
        default_factory=dict,
        description="Phân nhóm theo loại dòng tiền",
    )

    @classmethod
    def from_entries(cls, entries: List[JournalEntry]) -> "JournalSummary":
        """Tạo tổng hợp từ danh sách bút toán."""
        identified = [e for e in entries if e.is_identified]
        unidentified = [e for e in entries if not e.is_identified]

        by_category = {}
        for entry in entries:
            cat = entry.category
            if cat not in by_category:
                by_category[cat] = {"count": 0, "amount": 0.0}
            by_category[cat]["count"] += 1
            by_category[cat]["amount"] += entry.amount

        return cls(
            entries=entries,
            total_entries=len(entries),
            identified_entries=len(identified),
            unidentified_entries=len(unidentified),
            total_amount=sum(e.amount for e in entries),
            by_category=by_category,
        )
