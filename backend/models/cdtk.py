"""
Model cho Bảng Cân đối tài khoản (CĐTK).
Mẫu F01-DNN (TT133) / F01-DN (TT200).
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CDTKAccount(BaseModel):
    """Một tài khoản trên Bảng CĐTK."""

    model_config = {"populate_by_name": True}

    ma_tai_khoan: str = Field(
        ..., description="Mã tài khoản kế toán, vd: 111, 112, 1121..."
    )
    ten_tai_khoan: str = Field(
        default="", description="Tên tài khoản tiếng Việt"
    )
    loai: str = Field(
        default="",
        description="Loại TK: TS, TS_AM, TS_DP, NV, NV_AM, LK, DT, CP, XDKQ",
    )
    parent_tk: Optional[str] = Field(
        default=None, description="Mã TK cha (nếu là TK chi tiết)"
    )

    # ─── Số dư đầu kỳ ─────────────────────────────────
    du_no_dau_ky: Optional[float] = Field(
        default=None, description="Dư Nợ đầu kỳ"
    )
    du_co_dau_ky: Optional[float] = Field(
        default=None, description="Dư Có đầu kỳ"
    )

    # ─── Phát sinh trong kỳ ────────────────────────────
    phat_sinh_no: Optional[float] = Field(
        default=None, description="Phát sinh Nợ trong kỳ"
    )
    phat_sinh_co: Optional[float] = Field(
        default=None, description="Phát sinh Có trong kỳ"
    )

    # ─── Số dư cuối kỳ ────────────────────────────────
    du_no_cuoi_ky: Optional[float] = Field(
        default=None, description="Dư Nợ cuối kỳ"
    )
    du_co_cuoi_ky: Optional[float] = Field(
        default=None, description="Dư Có cuối kỳ"
    )

    @property
    def net_movement(self) -> float:
        """Biến động ròng trong kỳ (PS Nợ - PS Có)."""
        no = self.phat_sinh_no or 0.0
        co = self.phat_sinh_co or 0.0
        return no - co

    @property
    def is_sub_account(self) -> bool:
        """Có phải TK con hay không."""
        return self.parent_tk is not None


class BangCanDoiTaiKhoan(BaseModel):
    """
    Bảng Cân đối tài khoản hoàn chỉnh.
    Thể hiện số dư và phát sinh của tất cả tài khoản kế toán.
    """

    model_config = {"populate_by_name": True}

    accounts: List[CDTKAccount] = Field(
        default_factory=list,
        description="Danh sách các tài khoản",
    )

    # ─── Tổng cộng ────────────────────────────────────
    tong_no_dau_ky: Optional[float] = Field(
        default=None, description="Tổng cộng dư Nợ đầu kỳ"
    )
    tong_co_dau_ky: Optional[float] = Field(
        default=None, description="Tổng cộng dư Có đầu kỳ"
    )
    tong_no_phat_sinh: Optional[float] = Field(
        default=None, description="Tổng cộng phát sinh Nợ"
    )
    tong_co_phat_sinh: Optional[float] = Field(
        default=None, description="Tổng cộng phát sinh Có"
    )
    tong_no_cuoi_ky: Optional[float] = Field(
        default=None, description="Tổng cộng dư Nợ cuối kỳ"
    )
    tong_co_cuoi_ky: Optional[float] = Field(
        default=None, description="Tổng cộng dư Có cuối kỳ"
    )

    def get_account(self, ma_tk: str) -> Optional[CDTKAccount]:
        """Tìm tài khoản theo mã."""
        for acc in self.accounts:
            if acc.ma_tai_khoan == ma_tk:
                return acc
        return None

    def get_by_type(self, loai: str) -> List[CDTKAccount]:
        """Lấy tất cả TK thuộc loại chỉ định."""
        return [acc for acc in self.accounts if acc.loai == loai]

    def is_balanced_start(self) -> bool:
        """Kiểm tra Tổng Nợ = Tổng Có đầu kỳ."""
        if self.tong_no_dau_ky is None or self.tong_co_dau_ky is None:
            return False
        return abs(self.tong_no_dau_ky - self.tong_co_dau_ky) < 1

    def is_balanced_end(self) -> bool:
        """Kiểm tra Tổng Nợ = Tổng Có cuối kỳ."""
        if self.tong_no_cuoi_ky is None or self.tong_co_cuoi_ky is None:
            return False
        return abs(self.tong_no_cuoi_ky - self.tong_co_cuoi_ky) < 1

    def is_balanced_movement(self) -> bool:
        """Kiểm tra Tổng PS Nợ = Tổng PS Có."""
        if self.tong_no_phat_sinh is None or self.tong_co_phat_sinh is None:
            return False
        return abs(self.tong_no_phat_sinh - self.tong_co_phat_sinh) < 1

    @classmethod
    def from_parsed_data(
        cls,
        raw_data: Dict[str, Any],
        account_map: dict,
    ) -> "BangCanDoiTaiKhoan":
        """
        Tạo BangCanDoiTaiKhoan từ dữ liệu đã parse.

        Args:
            raw_data: Dict chứa SoDuDauKy, SoPhatSinhTrongKy, SoDuCuoiKy
            account_map: CDTK_ACCOUNT_MAP từ mapper
        """
        dk = raw_data.get("SoDuDauKy", {})
        ps = raw_data.get("SoPhatSinhTrongKy", {})
        ck = raw_data.get("SoDuCuoiKy", {})

        dk_no = dk.get("no", {}) if dk else {}
        dk_co = dk.get("co", {}) if dk else {}
        ps_no = ps.get("no", {}) if ps else {}
        ps_co = ps.get("co", {}) if ps else {}
        ck_no = ck.get("no", {}) if ck else {}
        ck_co = ck.get("co", {}) if ck else {}

        accounts = []
        for ct_key, info in account_map.items():
            accounts.append(CDTKAccount(
                ma_tai_khoan=info.get("tk", ""),
                ten_tai_khoan=info.get("name", ""),
                loai=info.get("loai", ""),
                parent_tk=info.get("parent"),
                du_no_dau_ky=_safe_float(dk_no.get(ct_key)),
                du_co_dau_ky=_safe_float(dk_co.get(ct_key)),
                phat_sinh_no=_safe_float(ps_no.get(ct_key)),
                phat_sinh_co=_safe_float(ps_co.get(ct_key)),
                du_no_cuoi_ky=_safe_float(ck_no.get(ct_key)),
                du_co_cuoi_ky=_safe_float(ck_co.get(ct_key)),
            ))

        return cls(
            accounts=accounts,
            tong_no_dau_ky=_safe_float(dk_no.get("tongCong")),
            tong_co_dau_ky=_safe_float(dk_co.get("tongCong")),
            tong_no_phat_sinh=_safe_float(ps_no.get("tongCong")),
            tong_co_phat_sinh=_safe_float(ps_co.get("tongCong")),
            tong_no_cuoi_ky=_safe_float(ck_no.get("tongCong")),
            tong_co_cuoi_ky=_safe_float(ck_co.get("tongCong")),
        )


def _safe_float(value) -> Optional[float]:
    """Chuyển giá trị sang float an toàn, trả None nếu không hợp lệ."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
