"""
Model cho Báo cáo Kết quả hoạt động kinh doanh (KQHĐKD).
Mẫu B02-DNN (TT133) / B02-DN (TT200).
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class KQHDKDLineItem(BaseModel):
    """Một dòng chỉ tiêu trên Báo cáo KQHĐKD."""

    model_config = {"populate_by_name": True}

    ma_chi_tieu: str = Field(
        ..., description="Mã chỉ tiêu, vd: ct01, ct10..."
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


class BaoCaoKQHDKD(BaseModel):
    """
    Báo cáo Kết quả hoạt động kinh doanh hoàn chỉnh.
    Phản ánh doanh thu, chi phí, lợi nhuận trong kỳ.
    """

    model_config = {"populate_by_name": True}

    items: List[KQHDKDLineItem] = Field(
        default_factory=list,
        description="Danh sách các dòng chỉ tiêu",
    )

    # ─── Chỉ tiêu tổng hợp (truy nhanh) ──────────────
    doanh_thu_ban_hang: Optional[float] = Field(
        default=None, description="Doanh thu BH và CCDV (ms 01)"
    )
    doanh_thu_thuan: Optional[float] = Field(
        default=None, description="Doanh thu thuần (ms 10)"
    )
    gia_von_hang_ban: Optional[float] = Field(
        default=None, description="Giá vốn hàng bán (ms 11)"
    )
    loi_nhuan_gop: Optional[float] = Field(
        default=None, description="Lợi nhuận gộp (ms 20)"
    )
    loi_nhuan_thuan_hdkd: Optional[float] = Field(
        default=None, description="Lợi nhuận thuần từ HĐKD (ms 30)"
    )
    tong_loi_nhuan_truoc_thue: Optional[float] = Field(
        default=None, description="Tổng LN kế toán trước thuế (ms 50)"
    )
    loi_nhuan_sau_thue: Optional[float] = Field(
        default=None, description="Lợi nhuận sau thuế TNDN (ms 60)"
    )

    def get_item(self, ma_chi_tieu: str) -> Optional[KQHDKDLineItem]:
        """Tìm chỉ tiêu theo mã."""
        for item in self.items:
            if item.ma_chi_tieu == ma_chi_tieu:
                return item
        return None

    def validate_formulas(self) -> List[dict]:
        """
        Kiểm tra các công thức nội bộ KQHĐKD.
        Trả về danh sách các công thức không khớp.
        """
        errors = []
        nam_nay = {item.ma_chi_tieu: item.nam_nay or 0.0 for item in self.items}

        formulas = [
            ("DT thuần = DT - Giảm trừ",
             nam_nay.get("ct10", 0),
             nam_nay.get("ct01", 0) - nam_nay.get("ct02", 0)),
            ("LN gộp = DT thuần - Giá vốn",
             nam_nay.get("ct20", 0),
             nam_nay.get("ct10", 0) - nam_nay.get("ct11", 0)),
            ("LN thuần HĐKD = LN gộp + DT TC - CP TC - CP BH - CP QLDN",
             nam_nay.get("ct30", 0),
             nam_nay.get("ct20", 0) + nam_nay.get("ct21", 0)
             - nam_nay.get("ct22", 0) - nam_nay.get("ct23", 0)
             - nam_nay.get("ct24", 0)),
            ("LN khác = Thu nhập khác - CP khác",
             nam_nay.get("ct40", 0),
             nam_nay.get("ct31", 0) - nam_nay.get("ct32", 0)),
            ("Tổng LN trước thuế = LN thuần HĐKD + LN khác",
             nam_nay.get("ct50", 0),
             nam_nay.get("ct30", 0) + nam_nay.get("ct40", 0)),
            ("LN sau thuế = Tổng LN trước thuế - CP thuế TNDN",
             nam_nay.get("ct60", 0),
             nam_nay.get("ct50", 0) - nam_nay.get("ct51", 0)),
        ]

        for name, actual, expected in formulas:
            diff = actual - expected
            if abs(diff) > 1:
                errors.append({
                    "formula": name,
                    "actual": actual,
                    "expected": expected,
                    "difference": diff,
                })

        return errors

    @classmethod
    def from_parsed_data(
        cls,
        raw_data: dict,
        mapper: dict,
    ) -> "BaoCaoKQHDKD":
        """
        Tạo BaoCaoKQHDKD từ dữ liệu đã parse và mapping chỉ tiêu.

        Args:
            raw_data: Dict chứa thuyet_minh, nam_nay, nam_truoc
            mapper: KQHDKD_MAP từ tt133_mapper hoặc tt200_mapper
        """
        items = []
        nam_nay = raw_data.get("nam_nay", {})
        nam_truoc = raw_data.get("nam_truoc", {})
        thuyet_minh = raw_data.get("thuyet_minh", {})

        for ct_key, info in mapper.items():
            items.append(KQHDKDLineItem(
                ma_chi_tieu=ct_key,
                ten_chi_tieu=info.get("name", ""),
                ma_so=str(info.get("ms", "")),
                thuyet_minh=str(thuyet_minh.get(ct_key, "")) or None,
                nam_nay=_safe_float(nam_nay.get(ct_key)),
                nam_truoc=_safe_float(nam_truoc.get(ct_key)),
            ))

        return cls(
            items=items,
            doanh_thu_ban_hang=_safe_float(nam_nay.get("ct01")),
            doanh_thu_thuan=_safe_float(nam_nay.get("ct10")),
            gia_von_hang_ban=_safe_float(nam_nay.get("ct11")),
            loi_nhuan_gop=_safe_float(nam_nay.get("ct20")),
            loi_nhuan_thuan_hdkd=_safe_float(nam_nay.get("ct30")),
            tong_loi_nhuan_truoc_thue=_safe_float(nam_nay.get("ct50")),
            loi_nhuan_sau_thue=_safe_float(nam_nay.get("ct60")),
        )


def _safe_float(value) -> Optional[float]:
    """Chuyển giá trị sang float an toàn, trả None nếu không hợp lệ."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
