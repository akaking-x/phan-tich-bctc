# backend/analyzer/cash_flow_analyzer.py

"""
Phân tích dòng tiền từ Báo cáo Lưu chuyển Tiền tệ (LCTT) và các báo cáo liên quan.

Bao gồm:
- Phân tích cơ cấu dòng tiền (operating/investing/financing)
- Dòng tiền tự do (Free Cash Flow)
- Ước tính chu kỳ chuyển đổi tiền mặt (Cash Conversion Cycle)
- Đánh giá chất lượng dòng tiền (Operating CF vs Net Income)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class CashFlowItem:
    """Một mục trong kết quả phân tích dòng tiền."""
    code: str
    name: str
    value: Optional[float]
    unit: str               # "VNĐ", "%", "ngày", "lần"
    interpretation: str
    category: str           # "structure", "free_cash_flow", "cycle", "quality"


@dataclass
class CashFlowAnalysis:
    """Kết quả phân tích dòng tiền tổng hợp."""
    # Cơ cấu dòng tiền
    operating_cf: float
    investing_cf: float
    financing_cf: float
    net_change: float

    # Tỷ trọng
    operating_pct: Optional[float]
    investing_pct: Optional[float]
    financing_pct: Optional[float]

    # Free Cash Flow
    free_cash_flow: Optional[float]
    fcf_to_revenue: Optional[float]

    # Cash Conversion Cycle (ước tính)
    days_receivable: Optional[float]
    days_inventory: Optional[float]
    days_payable: Optional[float]
    cash_conversion_cycle: Optional[float]

    # Chất lượng dòng tiền
    cf_to_net_income: Optional[float]
    cf_quality: str         # "Tốt", "Trung bình", "Kém"

    # Chi tiết phân tích
    items: List[CashFlowItem] = field(default_factory=list)

    # Cảnh báo / nhận xét
    warnings: List[str] = field(default_factory=list)


class CashFlowAnalyzer:
    """
    Phân tích dòng tiền doanh nghiệp.

    Dựa trên LCTT (trực tiếp), CĐKT và KQHĐKD.
    """

    def __init__(self, parsed_data: Dict[str, Any]):
        self.data = parsed_data
        self.lctt = parsed_data.get("lctt", {}).get("nam_nay", {})
        self.lctt_truoc = parsed_data.get("lctt", {}).get("nam_truoc", {})
        self.cdkt_cn = parsed_data.get("cdkt", {}).get("so_cuoi_nam", {})
        self.cdkt_dn = parsed_data.get("cdkt", {}).get("so_dau_nam", {})
        self.kqhdkd = parsed_data.get("kqhdkd", {}).get("nam_nay", {})

    def analyze(self) -> CashFlowAnalysis:
        """Phân tích toàn diện dòng tiền."""
        items: List[CashFlowItem] = []
        warnings: List[str] = []

        # 1. Cơ cấu dòng tiền
        operating_cf = self._g(self.lctt, "ct20")
        investing_cf = self._g(self.lctt, "ct30")
        financing_cf = self._g(self.lctt, "ct40")
        net_change = self._g(self.lctt, "ct50")

        structure_items, structure_warnings = self._analyze_structure(
            operating_cf, investing_cf, financing_cf
        )
        items.extend(structure_items)
        warnings.extend(structure_warnings)

        # Tỷ trọng dòng tiền
        total_abs = abs(operating_cf) + abs(investing_cf) + abs(financing_cf)
        operating_pct = (abs(operating_cf) / total_abs * 100) if total_abs > 0 else None
        investing_pct = (abs(investing_cf) / total_abs * 100) if total_abs > 0 else None
        financing_pct = (abs(financing_cf) / total_abs * 100) if total_abs > 0 else None

        # 2. Free Cash Flow
        fcf, fcf_to_revenue = self._calc_free_cash_flow(operating_cf)
        fcf_items = self._analyze_fcf(fcf, fcf_to_revenue)
        items.extend(fcf_items)

        # 3. Cash Conversion Cycle
        days_recv, days_inv, days_pay, ccc = self._calc_cash_conversion_cycle()
        ccc_items = self._analyze_ccc(days_recv, days_inv, days_pay, ccc)
        items.extend(ccc_items)

        # 4. Chất lượng dòng tiền
        cf_to_ni, cf_quality = self._assess_quality(operating_cf)
        quality_items, quality_warnings = self._analyze_quality(
            operating_cf, cf_to_ni, cf_quality
        )
        items.extend(quality_items)
        warnings.extend(quality_warnings)

        return CashFlowAnalysis(
            operating_cf=operating_cf,
            investing_cf=investing_cf,
            financing_cf=financing_cf,
            net_change=net_change,
            operating_pct=operating_pct,
            investing_pct=investing_pct,
            financing_pct=financing_pct,
            free_cash_flow=fcf,
            fcf_to_revenue=fcf_to_revenue,
            days_receivable=days_recv,
            days_inventory=days_inv,
            days_payable=days_pay,
            cash_conversion_cycle=ccc,
            cf_to_net_income=cf_to_ni,
            cf_quality=cf_quality,
            items=items,
            warnings=warnings,
        )

    # ─── 1. Cơ cấu dòng tiền ──────────────────────────────

    def _analyze_structure(
        self,
        operating_cf: float,
        investing_cf: float,
        financing_cf: float,
    ) -> tuple:
        """Phân tích cơ cấu dòng tiền hoạt động / đầu tư / tài chính."""
        items: List[CashFlowItem] = []
        warnings: List[str] = []

        # Dòng tiền HĐKD
        if operating_cf > 0:
            op_interp = f"{operating_cf:,.0f} — DN tạo được tiền từ hoạt động kinh doanh"
        elif operating_cf == 0:
            op_interp = "Không có dòng tiền từ HĐKD"
        else:
            op_interp = (
                f"{operating_cf:,.0f} — DN đang chi nhiều hơn thu từ HĐKD, "
                f"cần theo dõi khả năng duy trì"
            )
            warnings.append(
                "Dòng tiền hoạt động kinh doanh âm: DN chi ra nhiều hơn thu vào "
                "từ hoạt động chính."
            )

        items.append(CashFlowItem(
            code="CF_STRUCT_01",
            name="Dòng tiền từ hoạt động kinh doanh",
            value=operating_cf,
            unit="VNĐ",
            interpretation=op_interp,
            category="structure",
        ))

        # Dòng tiền đầu tư
        if investing_cf < 0:
            inv_interp = (
                f"{investing_cf:,.0f} — DN đang đầu tư mở rộng "
                f"(mua TSCĐ, cho vay...)"
            )
        elif investing_cf > 0:
            inv_interp = (
                f"{investing_cf:,.0f} — DN đang thu hồi vốn đầu tư "
                f"(bán TSCĐ, thu nợ cho vay...)"
            )
        else:
            inv_interp = "Không có dòng tiền đầu tư"

        items.append(CashFlowItem(
            code="CF_STRUCT_02",
            name="Dòng tiền từ hoạt động đầu tư",
            value=investing_cf,
            unit="VNĐ",
            interpretation=inv_interp,
            category="structure",
        ))

        # Dòng tiền tài chính
        if financing_cf > 0:
            fin_interp = (
                f"{financing_cf:,.0f} — DN huy động vốn "
                f"(vay NH, nhận vốn góp...)"
            )
        elif financing_cf < 0:
            fin_interp = (
                f"{financing_cf:,.0f} — DN trả nợ vay hoặc "
                f"chi trả cổ tức"
            )
        else:
            fin_interp = "Không có dòng tiền tài chính"

        items.append(CashFlowItem(
            code="CF_STRUCT_03",
            name="Dòng tiền từ hoạt động tài chính",
            value=financing_cf,
            unit="VNĐ",
            interpretation=fin_interp,
            category="structure",
        ))

        # Cảnh báo cơ cấu bất thường
        if operating_cf < 0 and financing_cf > 0:
            warnings.append(
                "HĐKD âm nhưng huy động tài chính dương: DN phụ thuộc vào "
                "vốn vay/vốn góp để duy trì hoạt động."
            )

        if operating_cf < 0 and investing_cf > 0:
            warnings.append(
                "HĐKD âm nhưng thu hồi đầu tư: DN có thể đang bán tài sản "
                "để bù đắp thiếu hụt dòng tiền hoạt động."
            )

        return items, warnings

    # ─── 2. Free Cash Flow ─────────────────────────────────

    def _calc_free_cash_flow(
        self, operating_cf: float
    ) -> tuple:
        """
        Tính dòng tiền tự do (Free Cash Flow).

        FCF = Dòng tiền HĐKD - Chi mua sắm TSCĐ (ct21)
        """
        # ct21 = Tiền chi mua sắm, xây dựng TSCĐ (thường âm)
        capex = abs(self._g(self.lctt, "ct21"))
        dt = self._g(self.kqhdkd, "ct10")

        fcf = operating_cf - capex
        fcf_to_revenue = (fcf / dt * 100) if dt != 0 else None

        return fcf, fcf_to_revenue

    def _analyze_fcf(
        self,
        fcf: Optional[float],
        fcf_to_revenue: Optional[float],
    ) -> List[CashFlowItem]:
        """Phân tích dòng tiền tự do."""
        items: List[CashFlowItem] = []

        capex = abs(self._g(self.lctt, "ct21"))

        if fcf is not None:
            if fcf > 0:
                interp = (
                    f"{fcf:,.0f} — DN tạo đủ tiền từ HĐKD sau khi đầu tư TSCĐ. "
                    f"Có khả năng trả nợ, chia cổ tức."
                )
            else:
                interp = (
                    f"{fcf:,.0f} — DN chưa tạo đủ tiền từ HĐKD "
                    f"sau khi đầu tư TSCĐ ({capex:,.0f}). "
                    f"Cần huy động thêm vốn."
                )
        else:
            interp = "Không tính được FCF"

        items.append(CashFlowItem(
            code="FCF_01",
            name="Dòng tiền tự do (FCF)",
            value=fcf,
            unit="VNĐ",
            interpretation=interp,
            category="free_cash_flow",
        ))

        if fcf_to_revenue is not None:
            items.append(CashFlowItem(
                code="FCF_02",
                name="FCF / Doanh thu thuần",
                value=fcf_to_revenue,
                unit="%",
                interpretation=(
                    f"{fcf_to_revenue:.1f}% — "
                    + ("Tốt" if fcf_to_revenue > 5 else
                       "Chấp nhận được" if fcf_to_revenue > 0 else
                       "Cần cải thiện")
                ),
                category="free_cash_flow",
            ))

        return items

    # ─── 3. Cash Conversion Cycle ──────────────────────────

    def _calc_cash_conversion_cycle(self) -> tuple:
        """
        Ước tính chu kỳ chuyển đổi tiền mặt.

        CCC = DSO + DIO - DPO

        DSO = (Phải thu KH bình quân / DT thuần) * 365
        DIO = (HTK bình quân / Giá vốn) * 365
        DPO = (Phải trả NCC bình quân / Giá vốn) * 365
        """
        dt = self._g(self.kqhdkd, "ct10")  # DT thuần
        gia_von = self._g(self.kqhdkd, "ct11")  # Giá vốn

        # Số dư bình quân
        pt_kh_cn = self._g(self.cdkt_cn, "ct131")  # Phải thu KH cuối năm
        pt_kh_dn = self._g(self.cdkt_dn, "ct131")  # Phải thu KH đầu năm
        pt_kh_bq = (pt_kh_cn + pt_kh_dn) / 2

        htk_cn = self._g(self.cdkt_cn, "ct140")   # HTK cuối năm
        htk_dn = self._g(self.cdkt_dn, "ct140")   # HTK đầu năm
        htk_bq = (htk_cn + htk_dn) / 2

        pt_ncc_cn = self._g(self.cdkt_cn, "ct411")  # Phải trả NCC cuối năm
        pt_ncc_dn = self._g(self.cdkt_dn, "ct411")  # Phải trả NCC đầu năm
        pt_ncc_bq = (pt_ncc_cn + pt_ncc_dn) / 2

        # Days Sales Outstanding
        days_recv = (pt_kh_bq / dt * 365) if dt > 0 else None

        # Days Inventory Outstanding
        days_inv = (htk_bq / gia_von * 365) if gia_von > 0 else None

        # Days Payable Outstanding
        days_pay = (pt_ncc_bq / gia_von * 365) if gia_von > 0 else None

        # Cash Conversion Cycle
        if days_recv is not None and days_inv is not None and days_pay is not None:
            ccc = days_recv + days_inv - days_pay
        else:
            ccc = None

        return days_recv, days_inv, days_pay, ccc

    def _analyze_ccc(
        self,
        days_recv: Optional[float],
        days_inv: Optional[float],
        days_pay: Optional[float],
        ccc: Optional[float],
    ) -> List[CashFlowItem]:
        """Phân tích chu kỳ chuyển đổi tiền mặt."""
        items: List[CashFlowItem] = []

        # DSO
        if days_recv is not None:
            dso_interp = (
                f"{days_recv:.0f} ngày — "
                + ("Tốt" if days_recv < 30 else
                   "Bình thường" if days_recv < 60 else
                   "Cần cải thiện, thu tiền chậm")
            )
        else:
            dso_interp = "Không tính được (DT = 0)"

        items.append(CashFlowItem(
            code="CCC_01",
            name="Số ngày thu tiền bình quân (DSO)",
            value=days_recv,
            unit="ngày",
            interpretation=dso_interp,
            category="cycle",
        ))

        # DIO
        if days_inv is not None:
            dio_interp = (
                f"{days_inv:.0f} ngày — "
                + ("Tốt" if days_inv < 30 else
                   "Bình thường" if days_inv < 90 else
                   "Hàng tồn kho quay chậm")
            )
        else:
            dio_interp = "Không tính được (giá vốn = 0)"

        items.append(CashFlowItem(
            code="CCC_02",
            name="Số ngày tồn kho bình quân (DIO)",
            value=days_inv,
            unit="ngày",
            interpretation=dio_interp,
            category="cycle",
        ))

        # DPO
        if days_pay is not None:
            dpo_interp = (
                f"{days_pay:.0f} ngày — "
                + ("Nhanh" if days_pay < 15 else
                   "Bình thường" if days_pay < 45 else
                   "Chiếm dụng vốn NCC lâu")
            )
        else:
            dpo_interp = "Không tính được (giá vốn = 0)"

        items.append(CashFlowItem(
            code="CCC_03",
            name="Số ngày trả tiền NCC bình quân (DPO)",
            value=days_pay,
            unit="ngày",
            interpretation=dpo_interp,
            category="cycle",
        ))

        # CCC
        if ccc is not None:
            if ccc < 0:
                ccc_interp = (
                    f"{ccc:.0f} ngày — Rất tốt, DN nhận tiền trước khi phải trả NCC"
                )
            elif ccc < 30:
                ccc_interp = f"{ccc:.0f} ngày — Tốt"
            elif ccc < 90:
                ccc_interp = f"{ccc:.0f} ngày — Trung bình"
            else:
                ccc_interp = (
                    f"{ccc:.0f} ngày — Chu kỳ tiền mặt dài, "
                    f"DN cần nhiều vốn lưu động"
                )
        else:
            ccc_interp = "Không tính được"

        items.append(CashFlowItem(
            code="CCC_04",
            name="Chu kỳ chuyển đổi tiền mặt (CCC)",
            value=ccc,
            unit="ngày",
            interpretation=ccc_interp,
            category="cycle",
        ))

        return items

    # ─── 4. Chất lượng dòng tiền ───────────────────────────

    def _assess_quality(self, operating_cf: float) -> tuple:
        """
        Đánh giá chất lượng dòng tiền.

        So sánh dòng tiền HĐKD với lợi nhuận sau thuế.
        Dòng tiền HĐKD > LNST -> chất lượng lợi nhuận tốt (tiền thực).
        """
        lnst = self._g(self.kqhdkd, "ct60")

        if lnst != 0:
            cf_to_ni = operating_cf / lnst
        else:
            cf_to_ni = None

        # Đánh giá
        if cf_to_ni is None:
            cf_quality = "Không xác định"
        elif lnst > 0 and cf_to_ni >= 1.0:
            cf_quality = "Tốt"
        elif lnst > 0 and cf_to_ni >= 0.5:
            cf_quality = "Trung bình"
        elif lnst > 0 and cf_to_ni > 0:
            cf_quality = "Kém"
        elif lnst > 0 and cf_to_ni <= 0:
            cf_quality = "Kém"
        elif lnst < 0 and operating_cf > 0:
            cf_quality = "Chấp nhận được"  # Lỗ kế toán nhưng dòng tiền dương
        elif lnst < 0 and operating_cf <= 0:
            cf_quality = "Kém"
        else:
            cf_quality = "Không xác định"

        return cf_to_ni, cf_quality

    def _analyze_quality(
        self,
        operating_cf: float,
        cf_to_ni: Optional[float],
        cf_quality: str,
    ) -> tuple:
        """Phân tích chất lượng dòng tiền."""
        items: List[CashFlowItem] = []
        warnings: List[str] = []
        lnst = self._g(self.kqhdkd, "ct60")

        # CF / Net Income ratio
        if cf_to_ni is not None:
            interp = (
                f"{cf_to_ni:.2f} lần — "
                f"{'LN được hỗ trợ bởi dòng tiền thực' if cf_to_ni >= 1.0 else 'LN chưa chuyển hoá hết thành tiền'}"
            )
        else:
            interp = "Không tính được (LNST = 0)"

        items.append(CashFlowItem(
            code="CFQ_01",
            name="Dòng tiền HĐKD / LNST",
            value=cf_to_ni,
            unit="lần",
            interpretation=interp,
            category="quality",
        ))

        # Đánh giá tổng thể
        items.append(CashFlowItem(
            code="CFQ_02",
            name="Chất lượng dòng tiền",
            value=None,
            unit="",
            interpretation=cf_quality,
            category="quality",
        ))

        # Cảnh báo chất lượng
        if lnst > 0 and operating_cf <= 0:
            warnings.append(
                f"Có lãi kế toán ({lnst:,.0f}) nhưng dòng tiền HĐKD âm "
                f"({operating_cf:,.0f}). Lợi nhuận chủ yếu trên sổ sách, "
                f"chưa thu được tiền thực."
            )

        if cf_to_ni is not None and lnst > 0 and cf_to_ni < 0.5:
            warnings.append(
                f"Tỷ lệ dòng tiền HĐKD/LNST chỉ đạt {cf_to_ni:.2f} lần. "
                f"Cần kiểm tra công nợ, hàng tồn kho tăng bất thường."
            )

        # Phân tích chi tiết dòng tiền HĐKD
        tien_thu_bh = self._g(self.lctt, "ct01")
        tien_chi_ncc = self._g(self.lctt, "ct02")
        tien_chi_luong = self._g(self.lctt, "ct03")
        tien_chi_lai_vay = self._g(self.lctt, "ct04")
        tien_chi_thue = self._g(self.lctt, "ct05")

        items.append(CashFlowItem(
            code="CFQ_03",
            name="Tiền thu từ bán hàng, cung cấp DV",
            value=tien_thu_bh,
            unit="VNĐ",
            interpretation=f"{tien_thu_bh:,.0f}",
            category="quality",
        ))

        items.append(CashFlowItem(
            code="CFQ_04",
            name="Tiền chi trả cho NCC",
            value=tien_chi_ncc,
            unit="VNĐ",
            interpretation=f"{tien_chi_ncc:,.0f}",
            category="quality",
        ))

        items.append(CashFlowItem(
            code="CFQ_05",
            name="Tiền chi trả cho NLĐ",
            value=tien_chi_luong,
            unit="VNĐ",
            interpretation=f"{tien_chi_luong:,.0f}",
            category="quality",
        ))

        items.append(CashFlowItem(
            code="CFQ_06",
            name="Tiền chi trả lãi vay",
            value=tien_chi_lai_vay,
            unit="VNĐ",
            interpretation=f"{tien_chi_lai_vay:,.0f}",
            category="quality",
        ))

        items.append(CashFlowItem(
            code="CFQ_07",
            name="Tiền chi nộp thuế TNDN",
            value=tien_chi_thue,
            unit="VNĐ",
            interpretation=f"{tien_chi_thue:,.0f}",
            category="quality",
        ))

        return items, warnings

    # ─── Helper ────────────────────────────────────────────

    @staticmethod
    def _g(data: Dict, key: str) -> float:
        """Lấy giá trị số từ dict, mặc định 0."""
        if data is None:
            return 0.0
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
