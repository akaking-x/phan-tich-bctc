# backend/analyzer/ratio_analyzer.py

"""
Phân tích chỉ số tài chính cơ bản từ BCTC.

Bao gồm 4 nhóm chỉ số:
- Thanh khoản (Liquidity)
- Sinh lời (Profitability)
- Đòn bẩy (Leverage)
- Hiệu quả (Efficiency)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class FinancialRatio:
    code: str
    name: str
    name_en: str
    value: Optional[float]
    unit: str              # "%", "lần", "ngày", "VNĐ"
    benchmark: str         # Mô tả ngưỡng tham khảo
    interpretation: str    # Nhận xét
    category: str          # "liquidity", "profitability", "leverage", "efficiency"


class RatioAnalyzer:
    """Tính toán các chỉ số tài chính cơ bản."""

    def __init__(self, parsed_data: Dict[str, Any]):
        self.cn = parsed_data.get("cdkt", {}).get("so_cuoi_nam", {})
        self.dn = parsed_data.get("cdkt", {}).get("so_dau_nam", {})
        self.kq = parsed_data.get("kqhdkd", {}).get("nam_nay", {})

    def analyze(self) -> List[FinancialRatio]:
        """Tính toán toàn bộ chỉ số tài chính."""
        ratios: List[FinancialRatio] = []
        ratios.extend(self._liquidity_ratios())
        ratios.extend(self._profitability_ratios())
        ratios.extend(self._leverage_ratios())
        ratios.extend(self._efficiency_ratios())
        return ratios

    def _liquidity_ratios(self) -> List[FinancialRatio]:
        """Nhóm chỉ số thanh khoản: Current Ratio, Quick Ratio, Cash Ratio."""
        tsnh = self._g(self.cn, "ct100")
        nnh = self._g(self.cn, "ct410")
        tien = self._g(self.cn, "ct110")
        htk = self._g(self.cn, "ct140")

        results: List[FinancialRatio] = []

        # Current ratio
        cr = tsnh / nnh if nnh != 0 else None
        results.append(FinancialRatio(
            code="LIQ_01",
            name="Hệ số thanh toán ngắn hạn",
            name_en="Current Ratio",
            value=cr,
            unit="lần",
            benchmark=">1.0 là an toàn, >2.0 là tốt",
            interpretation=self._interpret_ratio(cr, 1.0, 2.0),
            category="liquidity",
        ))

        # Quick ratio
        qr = (tsnh - htk) / nnh if nnh != 0 else None
        results.append(FinancialRatio(
            code="LIQ_02",
            name="Hệ số thanh toán nhanh",
            name_en="Quick Ratio",
            value=qr,
            unit="lần",
            benchmark=">0.5 là chấp nhận, >1.0 là tốt",
            interpretation=self._interpret_ratio(qr, 0.5, 1.0),
            category="liquidity",
        ))

        # Cash ratio
        cash_r = tien / nnh if nnh != 0 else None
        results.append(FinancialRatio(
            code="LIQ_03",
            name="Hệ số thanh toán tức thì",
            name_en="Cash Ratio",
            value=cash_r,
            unit="lần",
            benchmark=">0.2 là an toàn",
            interpretation=self._interpret_ratio(cash_r, 0.2, 0.5),
            category="liquidity",
        ))

        return results

    def _profitability_ratios(self) -> List[FinancialRatio]:
        """Nhóm chỉ số sinh lời: Gross Margin, Net Margin, ROA, ROE."""
        dt = self._g(self.kq, "ct10")
        ln_gop = self._g(self.kq, "ct20")
        lnst = self._g(self.kq, "ct60")
        tong_ts = self._g(self.cn, "ct300")
        vcsh = self._g(self.cn, "ct500")

        results: List[FinancialRatio] = []

        # Gross margin
        gm = (ln_gop / dt * 100) if dt != 0 else None
        results.append(FinancialRatio(
            code="PROF_01",
            name="Biên lợi nhuận gộp",
            name_en="Gross Margin",
            value=gm,
            unit="%",
            benchmark="Tùy ngành, thường 20-40%",
            interpretation=f"{gm:.1f}%" if gm is not None else "Không có DT",
            category="profitability",
        ))

        # Net margin
        nm = (lnst / dt * 100) if dt != 0 else None
        results.append(FinancialRatio(
            code="PROF_02",
            name="Biên lợi nhuận ròng",
            name_en="Net Margin",
            value=nm,
            unit="%",
            benchmark="Tùy ngành, thường 5-15%",
            interpretation=f"{nm:.1f}%" if nm is not None else "Không có DT",
            category="profitability",
        ))

        # ROA
        roa = (lnst / tong_ts * 100) if tong_ts != 0 else None
        results.append(FinancialRatio(
            code="PROF_03",
            name="Tỷ suất sinh lời trên tổng TS",
            name_en="ROA",
            value=roa,
            unit="%",
            benchmark=">5% là tốt",
            interpretation=f"{roa:.2f}%" if roa is not None else "N/A",
            category="profitability",
        ))

        # ROE
        roe = (lnst / vcsh * 100) if vcsh != 0 else None
        results.append(FinancialRatio(
            code="PROF_04",
            name="Tỷ suất sinh lời trên VCSH",
            name_en="ROE",
            value=roe,
            unit="%",
            benchmark=">10% là tốt",
            interpretation=f"{roe:.2f}%" if roe is not None else "N/A",
            category="profitability",
        ))

        return results

    def _leverage_ratios(self) -> List[FinancialRatio]:
        """Nhóm chỉ số đòn bẩy: Debt to Assets, Debt to Equity."""
        no_pt = self._g(self.cn, "ct400")
        tong_ts = self._g(self.cn, "ct300")
        vcsh = self._g(self.cn, "ct500")

        results: List[FinancialRatio] = []

        # D/A
        da = (no_pt / tong_ts * 100) if tong_ts != 0 else None
        results.append(FinancialRatio(
            code="LEV_01",
            name="Hệ số nợ trên tổng TS",
            name_en="Debt to Assets",
            value=da,
            unit="%",
            benchmark="<60% là an toàn",
            interpretation=f"{da:.1f}%" if da is not None else "N/A",
            category="leverage",
        ))

        # D/E
        de = (no_pt / vcsh) if vcsh != 0 else None
        results.append(FinancialRatio(
            code="LEV_02",
            name="Hệ số nợ trên VCSH",
            name_en="Debt to Equity",
            value=de,
            unit="lần",
            benchmark="<1.5 lần là an toàn",
            interpretation=f"{de:.2f} lần" if de is not None else "N/A",
            category="leverage",
        ))

        return results

    def _efficiency_ratios(self) -> List[FinancialRatio]:
        """Nhóm chỉ số hiệu quả: Asset Turnover."""
        dt = self._g(self.kq, "ct10")
        tong_ts = self._g(self.cn, "ct300")

        # Asset turnover
        at = dt / tong_ts if tong_ts != 0 else None
        return [FinancialRatio(
            code="EFF_01",
            name="Vòng quay tổng tài sản",
            name_en="Asset Turnover",
            value=at,
            unit="lần",
            benchmark="Tùy ngành, >1 lần là tốt",
            interpretation=f"{at:.2f} lần" if at is not None else "N/A",
            category="efficiency",
        )]

    @staticmethod
    def _g(data: Dict, key: str) -> float:
        """Lấy giá trị số từ dict, mặc định 0."""
        if data is None:
            return 0.0
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0

    @staticmethod
    def _interpret_ratio(value: Optional[float], low: float, good: float) -> str:
        """Nhận xét chỉ số dựa trên ngưỡng tham khảo."""
        if value is None:
            return "Không tính được (mẫu số = 0)"
        if value >= good:
            return f"{value:.2f} — Tốt"
        elif value >= low:
            return f"{value:.2f} — Chấp nhận được"
        else:
            return f"{value:.2f} — Cần cải thiện"
