"""
Base Pydantic models cho BCTC Analyzer.
Chứa các model dùng chung: thông tin doanh nghiệp, kỳ báo cáo,
và container chính ParsedBCTC gom 4 báo cáo.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CompanyInfo(BaseModel):
    """Thông tin doanh nghiệp trích từ XML HTKK."""

    model_config = {"populate_by_name": True}

    mst: str = Field(default="", description="Mã số thuế")
    ten_dn: str = Field(default="", description="Tên doanh nghiệp")
    dia_chi: str = Field(default="", description="Địa chỉ")
    tinh: str = Field(default="", description="Tỉnh/thành phố")
    ma_to_khai: str = Field(default="", description="Mã tờ khai (684=TT133, 405=TT200)")
    ten_to_khai: str = Field(default="", description="Tên tờ khai")
    ky_bao_cao: str = Field(default="", description="Kỳ báo cáo (N=Năm, Q=Quý...)")
    tu_ngay: str = Field(default="", description="Từ ngày (dd/MM/yyyy)")
    den_ngay: str = Field(default="", description="Đến ngày (dd/MM/yyyy)")
    ngay_lap: str = Field(default="", description="Ngày lập tờ khai")


class ReportPeriod(BaseModel):
    """Kỳ báo cáo tài chính."""

    model_config = {"populate_by_name": True}

    ky_bao_cao: str = Field(default="", description="Loại kỳ: N (năm), Q (quý)")
    tu_ngay: str = Field(default="", description="Ngày bắt đầu kỳ")
    den_ngay: str = Field(default="", description="Ngày kết thúc kỳ")
    nam_tai_chinh: Optional[int] = Field(default=None, description="Năm tài chính")


class BalanceSheetData(BaseModel):
    """Dữ liệu Bảng Cân đối kế toán (CĐKT) - raw dict từ XML."""

    model_config = {"populate_by_name": True}

    thuyet_minh: Dict[str, Any] = Field(default_factory=dict, description="Mã thuyết minh")
    so_cuoi_nam: Dict[str, Any] = Field(default_factory=dict, description="Số cuối năm/cuối kỳ")
    so_dau_nam: Dict[str, Any] = Field(default_factory=dict, description="Số đầu năm/đầu kỳ")


class IncomeStatementData(BaseModel):
    """Dữ liệu Kết quả hoạt động kinh doanh (KQHĐKD) - raw dict từ XML."""

    model_config = {"populate_by_name": True}

    thuyet_minh: Dict[str, Any] = Field(default_factory=dict, description="Mã thuyết minh")
    nam_nay: Dict[str, Any] = Field(default_factory=dict, description="Số liệu năm nay")
    nam_truoc: Dict[str, Any] = Field(default_factory=dict, description="Số liệu năm trước")


class CashFlowData(BaseModel):
    """Dữ liệu Lưu chuyển tiền tệ (LCTT) - raw dict từ XML."""

    model_config = {"populate_by_name": True}

    thuyet_minh: Dict[str, Any] = Field(default_factory=dict, description="Mã thuyết minh")
    nam_nay: Dict[str, Any] = Field(default_factory=dict, description="Số liệu năm nay")
    nam_truoc: Dict[str, Any] = Field(default_factory=dict, description="Số liệu năm trước")


class PeriodBalance(BaseModel):
    """Số dư Nợ/Có cho một kỳ trong bảng CĐTK."""

    model_config = {"populate_by_name": True}

    no: Dict[str, Any] = Field(default_factory=dict, description="Bên Nợ")
    co: Dict[str, Any] = Field(default_factory=dict, description="Bên Có")


class TrialBalanceData(BaseModel):
    """Dữ liệu Cân đối tài khoản (CĐTK) - raw dict từ XML."""

    model_config = {"populate_by_name": True}

    SoDuDauKy: Optional[PeriodBalance] = Field(
        default=None, description="Số dư đầu kỳ (Nợ/Có)"
    )
    SoPhatSinhTrongKy: Optional[PeriodBalance] = Field(
        default=None, description="Số phát sinh trong kỳ (Nợ/Có)"
    )
    SoDuCuoiKy: Optional[PeriodBalance] = Field(
        default=None, description="Số dư cuối kỳ (Nợ/Có)"
    )


class ParsedBCTC(BaseModel):
    """
    Container chính chứa toàn bộ dữ liệu BCTC đã parse.
    Gom 4 báo cáo: CĐKT, KQHĐKD, LCTT, CĐTK cùng thông tin DN.
    """

    model_config = {"populate_by_name": True}

    company: CompanyInfo = Field(
        default_factory=CompanyInfo,
        description="Thông tin doanh nghiệp",
    )
    circular: str = Field(
        default="",
        description="Thông tư áp dụng: TT133 hoặc TT200",
    )
    cdkt: BalanceSheetData = Field(
        default_factory=BalanceSheetData,
        description="Bảng Cân đối kế toán",
    )
    kqhdkd: IncomeStatementData = Field(
        default_factory=IncomeStatementData,
        description="Báo cáo Kết quả hoạt động kinh doanh",
    )
    lctt: CashFlowData = Field(
        default_factory=CashFlowData,
        description="Báo cáo Lưu chuyển tiền tệ",
    )
    cdtk: TrialBalanceData = Field(
        default_factory=TrialBalanceData,
        description="Bảng Cân đối tài khoản",
    )
