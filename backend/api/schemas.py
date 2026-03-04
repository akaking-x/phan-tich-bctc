"""
Pydantic request/response schemas cho BCTC Analyzer API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ─── Validation ──────────────────────────────────────────

class ValidationDetail(BaseModel):
    """Chi tiet mot kiem tra doi chieu."""
    rule_id: str = Field(..., description="Ma quy tac (VD: CDKT_01)")
    rule_name: str = Field(..., description="Ten quy tac")
    severity: str = Field(..., description="Muc do: ok, warning, error, critical")
    message: str = Field(..., description="Mo ta ket qua")
    difference: float = Field(default=0, description="Chenh lech (0 = khop)")


class ValidationResult(BaseModel):
    """Ket qua doi chieu cheo toan bo."""
    total_checks: int = Field(..., description="Tong so kiem tra")
    passed: int = Field(..., description="So kiem tra dat")
    warnings: int = Field(..., description="So canh bao")
    errors: int = Field(..., description="So loi")
    details: List[ValidationDetail] = Field(
        default_factory=list, description="Chi tiet tung kiem tra"
    )


# ─── Anomaly ─────────────────────────────────────────────

class AnomalyItem(BaseModel):
    """Mot bat thuong duoc phat hien."""
    code: str = Field(..., description="Ma bat thuong (VD: CASH_01)")
    title: str = Field(..., description="Tieu de")
    description: str = Field(..., description="Mo ta chi tiet")
    risk_level: str = Field(..., description="Muc rui ro: low, medium, high, critical")
    category: str = Field(..., description="Danh muc: cash, tax, structure, activity")
    suggestion: str = Field(..., description="De xuat xu ly")


class AnomalyResponse(BaseModel):
    """Response danh sach bat thuong."""
    total: int = Field(..., description="Tong so bat thuong")
    anomalies: List[AnomalyItem] = Field(
        default_factory=list, description="Danh sach bat thuong"
    )


# ─── Ratio ───────────────────────────────────────────────

class RatioItem(BaseModel):
    """Mot chi so tai chinh."""
    code: str = Field(..., description="Ma chi so (VD: LIQ_01)")
    name: str = Field(..., description="Ten tieng Viet")
    name_en: str = Field(..., description="Ten tieng Anh")
    value: Optional[float] = Field(None, description="Gia tri chi so")
    unit: str = Field(..., description="Don vi: %, lan, ngay, VND")
    benchmark: str = Field(..., description="Nguong tham chieu")
    interpretation: str = Field(..., description="Nhan xet")
    category: str = Field(..., description="Nhom: liquidity, profitability, leverage, efficiency")


class RatioResponse(BaseModel):
    """Response danh sach chi so tai chinh."""
    ratios: List[RatioItem] = Field(
        default_factory=list, description="Danh sach chi so"
    )


# ─── Journal ─────────────────────────────────────────────

class JournalItem(BaseModel):
    """Mot but toan tai tao."""
    description: str = Field(..., description="Mo ta but toan")
    debit: str = Field(..., description="TK No")
    debit_name: str = Field(..., description="Ten TK No")
    credit: str = Field(..., description="TK Co")
    credit_name: str = Field(..., description="Ten TK Co")
    amount: float = Field(..., description="So tien")
    category: str = Field(..., description="Loai: operating, investing, financing")
    confidence: float = Field(..., description="Do tin cay (0-1)")


# ─── Upload Response ─────────────────────────────────────

class CompanyInfoSchema(BaseModel):
    """Thong tin doanh nghiep."""
    mst: str = Field(default="", description="Ma so thue")
    ten_dn: str = Field(default="", description="Ten doanh nghiep")
    dia_chi: str = Field(default="", description="Dia chi")
    tinh: str = Field(default="", description="Tinh/TP")
    ma_to_khai: str = Field(default="", description="Ma to khai")
    ten_to_khai: str = Field(default="", description="Ten to khai")
    ky_bao_cao: str = Field(default="", description="Ky bao cao")
    tu_ngay: str = Field(default="", description="Tu ngay")
    den_ngay: str = Field(default="", description="Den ngay")
    ngay_lap: str = Field(default="", description="Ngay lap")


class UploadResponse(BaseModel):
    """Response day du tu endpoint /api/upload."""
    success: bool = Field(..., description="Thanh cong hay khong")
    company: CompanyInfoSchema = Field(..., description="Thong tin DN")
    circular: str = Field(..., description="Thong tu: TT133 hoac TT200")
    reports: Dict[str, Any] = Field(
        default_factory=dict,
        description="Du lieu 4 bao cao: cdkt, kqhdkd, lctt, cdtk",
    )
    validation: ValidationResult = Field(..., description="Ket qua doi chieu cheo")
    journals: List[JournalItem] = Field(
        default_factory=list, description="But toan tai tao"
    )
    anomalies: List[AnomalyItem] = Field(
        default_factory=list, description="Bat thuong phat hien"
    )
    ratios: List[RatioItem] = Field(
        default_factory=list, description="Chi so tai chinh"
    )


# ─── Export ──────────────────────────────────────────────

class ExportRequest(BaseModel):
    """Yeu cau xuat bao cao."""
    data: Dict[str, Any] = Field(
        ..., description="Du lieu phan tich (response tu /api/upload)"
    )
    format: str = Field(
        default="excel",
        description="Dinh dang: excel hoac pdf",
    )
    include_sections: List[str] = Field(
        default_factory=lambda: [
            "company", "cdkt", "kqhdkd", "validation", "anomalies", "ratios"
        ],
        description="Cac phan bao gom trong bao cao",
    )


# ─── Compare ─────────────────────────────────────────────

# ─── Auto Correct ───────────────────────────────────────

class CorrectionItemSchema(BaseModel):
    """Mot muc sua doi tu dong."""
    report: str = Field(..., description="Bao cao: cdkt, kqhdkd, lctt")
    section: str = Field(..., description="Phan: so_cuoi_nam, nam_nay, ...")
    code: str = Field(..., description="Ma chi tieu: ct100, ct10, ...")
    old_value: float = Field(..., description="Gia tri cu")
    new_value: float = Field(..., description="Gia tri moi")
    rule_id: str = Field(..., description="Ma quy tac: CDKT_02, KQHDKD_01, ...")
    reason: str = Field(..., description="Ly do sua")


class AutoCorrectResponse(BaseModel):
    """Response tu endpoint /api/auto-correct."""
    success: bool = Field(default=True)
    corrections: List[CorrectionItemSchema] = Field(
        default_factory=list, description="Danh sach cac muc sua"
    )
    corrected_analysis: Dict[str, Any] = Field(
        default_factory=dict, description="Ket qua phan tich sau khi sua"
    )
    original_analysis: Dict[str, Any] = Field(
        default_factory=dict, description="Ket qua phan tich truoc khi sua"
    )


class ApplyCorrectionsRequest(BaseModel):
    """Danh sach corrections de ap dung vao XML."""
    corrections: List[CorrectionItemSchema] = Field(
        ..., description="Danh sach corrections da chon"
    )


# ─── Compare ─────────────────────────────────────────────

class CompareRequest(BaseModel):
    """Yeu cau so sanh 2 ky bao cao (year-over-year)."""
    # Files will be uploaded via form-data, not JSON body.
    # This schema is for documentation and optional JSON-based compare.
    data_year1: Optional[Dict[str, Any]] = Field(
        None, description="Du lieu BCTC nam 1 (ky truoc)"
    )
    data_year2: Optional[Dict[str, Any]] = Field(
        None, description="Du lieu BCTC nam 2 (ky sau)"
    )


class CompareResultItem(BaseModel):
    """Mot chi tieu so sanh."""
    code: str = Field(..., description="Ma chi tieu (VD: ct100)")
    name: str = Field(default="", description="Ten chi tieu")
    value_year1: Optional[float] = Field(None, description="Gia tri nam 1")
    value_year2: Optional[float] = Field(None, description="Gia tri nam 2")
    change: Optional[float] = Field(None, description="Chenh lech tuyet doi")
    change_pct: Optional[float] = Field(None, description="Thay doi % ")


class CompareResponse(BaseModel):
    """Response so sanh 2 ky."""
    success: bool = True
    company_year1: CompanyInfoSchema = Field(..., description="Thong tin DN nam 1")
    company_year2: CompanyInfoSchema = Field(..., description="Thong tin DN nam 2")
    cdkt_comparison: List[CompareResultItem] = Field(
        default_factory=list, description="So sanh CDKT"
    )
    kqhdkd_comparison: List[CompareResultItem] = Field(
        default_factory=list, description="So sanh KQHDKD"
    )
    ratio_comparison: List[Dict[str, Any]] = Field(
        default_factory=list, description="So sanh chi so tai chinh"
    )
