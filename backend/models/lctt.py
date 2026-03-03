"""
Model cho Báo cáo Lưu chuyển tiền tệ (LCTT).
Mẫu B03-DNN (TT133) / B03-DN (TT200).
Hỗ trợ cả phương pháp trực tiếp và gián tiếp.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class LCTTLineItem(BaseModel):
    """Một dòng chỉ tiêu trên Báo cáo LCTT."""

    model_config = {"populate_by_name": True}

    ma_chi_tieu: str = Field(
        ..., description="Mã chỉ tiêu, vd: ct01, ct20..."
    )
    ten_chi_tieu: str = Field(
        default="", description="Tên chỉ tiêu tiếng Việt"
    )
    ma_so: Optional[str] = Field(
        default=None, description="Mã số trên báo cáo"
    )
    thuyet_minh: Optional[str] = Field(
        default=None, description="Mã thuyết minh liên kết"
    )
    nam_nay: Optional[float] = Field(
        default=None, description="Số liệu năm nay (kỳ này)"
    )
    nam_truoc: Optional[float] = Field(
        default=None, description="Số liệu năm trước (kỳ trước)"
    )
    flow_type: Optional[str] = Field(
        default=None,
        description="Loại dòng tiền: operating, investing, financing",
    )
    is_subtotal: bool = Field(
        default=False, description="Là dòng tổng phụ"
    )
    is_total: bool = Field(
        default=False, description="Là dòng tổng cộng"
    )


class BaoCaoLCTT(BaseModel):
    """
    Báo cáo Lưu chuyển tiền tệ hoàn chỉnh.
    Gồm 3 luồng: HĐKD, HĐ đầu tư, HĐ tài chính.
    """

    model_config = {"populate_by_name": True}

    phuong_phap: Literal["TT", "GT"] = Field(
        default="TT",
        description="Phương pháp lập: TT=trực tiếp, GT=gián tiếp",
    )
    items: List[LCTTLineItem] = Field(
        default_factory=list,
        description="Danh sách các dòng chỉ tiêu",
    )

    # ─── Chỉ tiêu tổng hợp (truy nhanh) ──────────────
    luu_chuyen_tien_hdkd: Optional[float] = Field(
        default=None,
        description="Lưu chuyển tiền thuần từ HĐKD (ms 20)",
    )
    luu_chuyen_tien_hddt: Optional[float] = Field(
        default=None,
        description="Lưu chuyển tiền thuần từ HĐ đầu tư (ms 30)",
    )
    luu_chuyen_tien_hdtc: Optional[float] = Field(
        default=None,
        description="Lưu chuyển tiền thuần từ HĐ tài chính (ms 40)",
    )
    tang_giam_tien_thuan: Optional[float] = Field(
        default=None,
        description="Tăng/giảm tiền thuần trong kỳ (ms 50)",
    )
    tien_dau_ky: Optional[float] = Field(
        default=None,
        description="Tiền và tương đương tiền đầu kỳ (ms 60)",
    )
    tien_cuoi_ky: Optional[float] = Field(
        default=None,
        description="Tiền và tương đương tiền cuối kỳ (ms 70)",
    )

    def get_item(self, ma_chi_tieu: str) -> Optional[LCTTLineItem]:
        """Tìm chỉ tiêu theo mã."""
        for item in self.items:
            if item.ma_chi_tieu == ma_chi_tieu:
                return item
        return None

    def get_by_flow(self, flow_type: str) -> List[LCTTLineItem]:
        """Lấy tất cả chỉ tiêu thuộc một loại dòng tiền."""
        return [
            item for item in self.items
            if item.flow_type == flow_type
        ]

    def validate_totals(self) -> List[dict]:
        """
        Kiểm tra các công thức tổng LCTT.
        Trả về danh sách các công thức không khớp.
        """
        errors = []
        nam_nay = {item.ma_chi_tieu: item.nam_nay or 0.0 for item in self.items}

        # ct50 = ct20 + ct30 + ct40
        ct50 = nam_nay.get("ct50", 0)
        expected_50 = (
            nam_nay.get("ct20", 0)
            + nam_nay.get("ct30", 0)
            + nam_nay.get("ct40", 0)
        )
        if abs(ct50 - expected_50) > 1:
            errors.append({
                "formula": "Tăng/giảm tiền thuần = HĐKD + HĐĐT + HĐTC",
                "actual": ct50,
                "expected": expected_50,
                "difference": ct50 - expected_50,
            })

        # ct70 = ct50 + ct60 + ct61
        ct70 = nam_nay.get("ct70", 0)
        expected_70 = (
            nam_nay.get("ct50", 0)
            + nam_nay.get("ct60", 0)
            + nam_nay.get("ct61", 0)
        )
        if abs(ct70 - expected_70) > 1:
            errors.append({
                "formula": "Tiền cuối kỳ = Tăng giảm + Đầu kỳ + Tỷ giá",
                "actual": ct70,
                "expected": expected_70,
                "difference": ct70 - expected_70,
            })

        return errors

    @classmethod
    def from_parsed_data(
        cls,
        raw_data: dict,
        mapper: dict,
        phuong_phap: str = "TT",
    ) -> "BaoCaoLCTT":
        """
        Tạo BaoCaoLCTT từ dữ liệu đã parse và mapping chỉ tiêu.

        Args:
            raw_data: Dict chứa thuyet_minh, nam_nay, nam_truoc
            mapper: LCTT_TT_MAP từ tt133_mapper hoặc tt200_mapper
            phuong_phap: "TT" (trực tiếp) hoặc "GT" (gián tiếp)
        """
        items = []
        nam_nay = raw_data.get("nam_nay", {})
        nam_truoc = raw_data.get("nam_truoc", {})
        thuyet_minh = raw_data.get("thuyet_minh", {})

        for ct_key, info in mapper.items():
            items.append(LCTTLineItem(
                ma_chi_tieu=ct_key,
                ten_chi_tieu=info.get("name", ""),
                ma_so=str(info.get("ms", "")),
                thuyet_minh=str(thuyet_minh.get(ct_key, "")) or None,
                nam_nay=_safe_float(nam_nay.get(ct_key)),
                nam_truoc=_safe_float(nam_truoc.get(ct_key)),
                flow_type=info.get("flow"),
                is_subtotal=info.get("subtotal", False),
                is_total=info.get("total", False),
            ))

        return cls(
            phuong_phap=phuong_phap,
            items=items,
            luu_chuyen_tien_hdkd=_safe_float(nam_nay.get("ct20")),
            luu_chuyen_tien_hddt=_safe_float(nam_nay.get("ct30")),
            luu_chuyen_tien_hdtc=_safe_float(nam_nay.get("ct40")),
            tang_giam_tien_thuan=_safe_float(nam_nay.get("ct50")),
            tien_dau_ky=_safe_float(nam_nay.get("ct60")),
            tien_cuoi_ky=_safe_float(nam_nay.get("ct70")),
        )


def _safe_float(value) -> Optional[float]:
    """Chuyển giá trị sang float an toàn, trả None nếu không hợp lệ."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
