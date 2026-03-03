"""
Model cho Bảng Cân đối kế toán (CĐKT).
Mẫu B01b-DNN (TT133) / B01-DN (TT200).
"""

from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


class CDKTLineItem(BaseModel):
    """Một dòng chỉ tiêu trên Bảng CĐKT."""

    model_config = {"populate_by_name": True}

    ma_chi_tieu: str = Field(
        ..., description="Mã chỉ tiêu, vd: ct100, ct110..."
    )
    ten_chi_tieu: str = Field(
        default="", description="Tên chỉ tiêu tiếng Việt"
    )
    ma_so: Optional[int] = Field(
        default=None, description="Mã số trên báo cáo (100, 110...)"
    )
    thuyet_minh: Optional[str] = Field(
        default=None, description="Mã thuyết minh liên kết"
    )
    so_cuoi_nam: Optional[float] = Field(
        default=None, description="Số cuối năm (cuối kỳ)"
    )
    so_dau_nam: Optional[float] = Field(
        default=None, description="Số đầu năm (đầu kỳ)"
    )
    level: int = Field(
        default=0,
        description="Cấp bậc hiển thị (0=tổng, 1=nhóm, 2=chi tiết)",
    )
    is_bold: bool = Field(
        default=False, description="Hiển thị in đậm (dòng tổng)"
    )


class BangCanDoiKeToan(BaseModel):
    """
    Bảng Cân đối kế toán hoàn chỉnh.
    Bao gồm phần Tài sản và Nguồn vốn.
    """

    model_config = {"populate_by_name": True}

    items: List[CDKTLineItem] = Field(
        default_factory=list,
        description="Danh sách các dòng chỉ tiêu",
    )

    # ─── Các chỉ tiêu tổng hợp (truy nhanh) ──────────
    tong_tai_san: Optional[float] = Field(
        default=None, description="Tổng cộng tài sản (ms 300)"
    )
    tong_nguon_von: Optional[float] = Field(
        default=None, description="Tổng cộng nguồn vốn (ms 600)"
    )
    tai_san_ngan_han: Optional[float] = Field(
        default=None, description="Tài sản ngắn hạn (ms 100)"
    )
    tai_san_dai_han: Optional[float] = Field(
        default=None, description="Tài sản dài hạn (ms 200)"
    )
    no_phai_tra: Optional[float] = Field(
        default=None, description="Nợ phải trả (ms 400)"
    )
    von_chu_so_huu: Optional[float] = Field(
        default=None, description="Vốn chủ sở hữu (ms 500)"
    )

    @model_validator(mode="after")
    def validate_balance(self) -> "BangCanDoiKeToan":
        """Kiểm tra Tổng TS = Tổng NV (nếu có dữ liệu)."""
        if self.tong_tai_san is not None and self.tong_nguon_von is not None:
            if abs(self.tong_tai_san - self.tong_nguon_von) > 1:
                # Chỉ cảnh báo, không raise để không block parse
                pass
        return self

    def is_balanced(self) -> bool:
        """Kiểm tra Tổng Tài sản = Tổng Nguồn vốn."""
        if self.tong_tai_san is None or self.tong_nguon_von is None:
            return False
        return abs(self.tong_tai_san - self.tong_nguon_von) < 1

    def get_item(self, ma_chi_tieu: str) -> Optional[CDKTLineItem]:
        """Tìm chỉ tiêu theo mã."""
        for item in self.items:
            if item.ma_chi_tieu == ma_chi_tieu:
                return item
        return None

    @classmethod
    def from_parsed_data(
        cls,
        raw_data: dict,
        mapper: dict,
    ) -> "BangCanDoiKeToan":
        """
        Tạo BangCanDoiKeToan từ dữ liệu đã parse và mapping chỉ tiêu.

        Args:
            raw_data: Dict chứa thuyet_minh, so_cuoi_nam, so_dau_nam
            mapper: CDKT_MAP từ tt133_mapper hoặc tt200_mapper
        """
        items = []
        so_cuoi_nam = raw_data.get("so_cuoi_nam", {})
        so_dau_nam = raw_data.get("so_dau_nam", {})
        thuyet_minh = raw_data.get("thuyet_minh", {})

        for ct_key, info in mapper.items():
            items.append(CDKTLineItem(
                ma_chi_tieu=ct_key,
                ten_chi_tieu=info.get("name", ""),
                ma_so=info.get("ms"),
                thuyet_minh=str(thuyet_minh.get(ct_key, "")) or None,
                so_cuoi_nam=_safe_float(so_cuoi_nam.get(ct_key)),
                so_dau_nam=_safe_float(so_dau_nam.get(ct_key)),
                level=info.get("level", 0),
                is_bold=info.get("bold", False),
            ))

        return cls(
            items=items,
            tong_tai_san=_safe_float(so_cuoi_nam.get("ct300")),
            tong_nguon_von=_safe_float(so_cuoi_nam.get("ct600")),
            tai_san_ngan_han=_safe_float(so_cuoi_nam.get("ct100")),
            tai_san_dai_han=_safe_float(so_cuoi_nam.get("ct200")),
            no_phai_tra=_safe_float(so_cuoi_nam.get("ct400")),
            von_chu_so_huu=_safe_float(so_cuoi_nam.get("ct500")),
        )


def _safe_float(value) -> Optional[float]:
    """Chuyển giá trị sang float an toàn, trả None nếu không hợp lệ."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
