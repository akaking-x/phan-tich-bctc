# backend/analyzer/anomaly_detector.py

"""
Phát hiện các bất thường & rủi ro thuế trong BCTC.
Dựa trên kinh nghiệm kiểm toán và các red flags phổ biến.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    code: str
    title: str
    description: str
    risk_level: RiskLevel
    category: str        # "cash", "tax", "structure", "activity"
    suggestion: str
    data: Optional[Dict[str, Any]] = field(default=None)


class AnomalyDetector:
    """
    Phát hiện các bất thường & rủi ro thuế trong BCTC.
    Dựa trên kinh nghiệm kiểm toán và các red flags phổ biến.
    """

    def __init__(self, parsed_data: Dict[str, Any]):
        self.data = parsed_data
        self.cdkt = parsed_data.get("cdkt", {}).get("so_cuoi_nam", {})
        self.cdkt_dn = parsed_data.get("cdkt", {}).get("so_dau_nam", {})
        self.kqhdkd = parsed_data.get("kqhdkd", {}).get("nam_nay", {})
        self.lctt = parsed_data.get("lctt", {}).get("nam_nay", {})
        self.cdtk_ck = parsed_data.get("cdtk", {}).get("SoDuCuoiKy", {})
        self.anomalies: List[Anomaly] = []

    def detect_all(self) -> List[Anomaly]:
        """Chạy toàn bộ kiểm tra bất thường."""
        self._check_cash_heavy()
        self._check_negative_equity()
        self._check_revenue_vs_cash()
        self._check_dormant_company()
        self._check_large_receivables()
        self._check_inventory_vs_revenue()
        self._check_expense_structure()
        self._check_related_party_signs()
        self._check_vat_anomaly()
        return self.anomalies

    def _check_cash_heavy(self):
        """Cảnh báo: Tiền mặt tồn quỹ quá lớn (TK111 > 50% tổng TS)."""
        no = self.cdtk_ck.get("no", {})
        tk111 = self._g(no, "ct111")
        tk112 = self._g(no, "ct112")
        tong_ts = self._g(self.cdkt, "ct300")

        if tong_ts > 0 and tk111 > 0:
            ratio = tk111 / tong_ts
            if ratio > 0.5:
                self.anomalies.append(Anomaly(
                    code="CASH_01",
                    title="Tiền mặt tồn quỹ bất thường",
                    description=(
                        f"TK111 = {tk111:,.0f} chiếm {ratio:.0%} tổng TS. "
                        f"Cơ quan thuế có thể nghi vấn tính thực của tiền mặt, "
                        f"yêu cầu kiểm đếm quỹ thực tế."
                    ),
                    risk_level=RiskLevel.HIGH,
                    category="cash",
                    suggestion=(
                        "Nên chuyển tiền mặt vào ngân hàng "
                        "để có chứng từ xác thực. "
                        "Hoặc giải trình nguồn gốc tiền mặt."
                    ),
                    data={"tk111": tk111, "tk112": tk112, "ratio": ratio},
                ))

    def _check_negative_equity(self):
        """Cảnh báo: VCSH âm hoặc lỗ luỹ kế (loss ratio > 50%)."""
        vcsh = self._g(self.cdkt, "ct500")
        lnst = self._g(self.cdkt, "ct517")

        if vcsh < 0:
            self.anomalies.append(Anomaly(
                code="EQUITY_01",
                title="Vốn chủ sở hữu âm",
                description=f"VCSH = {vcsh:,.0f}. DN có thể mất khả năng thanh toán.",
                risk_level=RiskLevel.CRITICAL,
                category="structure",
                suggestion="Cần tăng vốn hoặc xem xét tái cơ cấu.",
            ))

        if lnst < 0:
            von_gop = self._g(self.cdkt, "ct511")
            if von_gop > 0:
                loss_ratio = abs(lnst) / von_gop
                if loss_ratio > 0.5:
                    self.anomalies.append(Anomaly(
                        code="EQUITY_02",
                        title="Lỗ luỹ kế chiếm tỷ trọng lớn so với vốn góp",
                        description=(
                            f"Lỗ luỹ kế = {lnst:,.0f}, "
                            f"chiếm {loss_ratio:.0%} vốn góp {von_gop:,.0f}"
                        ),
                        risk_level=RiskLevel.HIGH,
                        category="structure",
                        suggestion="Cần có phương án kinh doanh cải thiện.",
                    ))

    def _check_revenue_vs_cash(self):
        """Cảnh báo: DT lớn nhưng thu tiền < 50% doanh thu."""
        dt = self._g(self.kqhdkd, "ct01")
        tien_thu = abs(self._g(self.lctt, "ct01"))

        if dt > 0 and tien_thu > 0:
            ratio = tien_thu / dt
            if ratio < 0.5:
                self.anomalies.append(Anomaly(
                    code="REV_01",
                    title="Doanh thu cao nhưng thu tiền thấp",
                    description=(
                        f"DT = {dt:,.0f}, tiền thu = {tien_thu:,.0f} "
                        f"({ratio:.0%}). Có thể DT ảo hoặc công nợ cao."
                    ),
                    risk_level=RiskLevel.MEDIUM,
                    category="activity",
                    suggestion="Kiểm tra công nợ phải thu và chính sách tín dụng.",
                ))

    def _check_dormant_company(self):
        """Cảnh báo: Công ty có vốn lớn nhưng không hoạt động (zero revenue)."""
        von_gop = self._g(self.cdkt, "ct511")
        dt = self._g(self.kqhdkd, "ct01")
        cp_qldn = self._g(self.kqhdkd, "ct24")

        if von_gop > 1_000_000_000 and dt == 0 and cp_qldn < 50_000_000:
            self.anomalies.append(Anomaly(
                code="DORMANT_01",
                title="Công ty vốn lớn nhưng chưa hoạt động",
                description=(
                    f"Vốn góp = {von_gop:,.0f} nhưng DT = 0, "
                    f"CP QLDN chỉ = {cp_qldn:,.0f}. "
                    f"Có thể là công ty mới thành lập hoặc để ngủ đông."
                ),
                risk_level=RiskLevel.MEDIUM,
                category="activity",
                suggestion=(
                    "Nếu mới thành lập, cần triển khai kinh doanh. "
                    "CQT có thể yêu cầu giải trình mục đích sử dụng vốn."
                ),
                data={"von_gop": von_gop, "dt": dt, "cp": cp_qldn},
            ))

    def _check_large_receivables(self):
        """Cảnh báo: Phải thu > 70% tổng tài sản."""
        pt = self._g(self.cdkt, "ct130")
        tong_ts = self._g(self.cdkt, "ct300")

        if tong_ts > 0 and pt / tong_ts > 0.7:
            self.anomalies.append(Anomaly(
                code="AR_01",
                title="Phải thu chiếm tỷ trọng quá lớn",
                description=(
                    f"Phải thu = {pt:,.0f} ({pt/tong_ts:.0%} tổng TS). "
                    f"Rủi ro nợ xấu cao."
                ),
                risk_level=RiskLevel.HIGH,
                category="structure",
                suggestion="Kiểm tra tuổi nợ, trích lập dự phòng.",
            ))

    def _check_inventory_vs_revenue(self):
        """Cảnh báo: HTK > 2 lần doanh thu."""
        htk = self._g(self.cdkt, "ct140")
        dt = self._g(self.kqhdkd, "ct01")

        if dt > 0 and htk > dt * 2:
            self.anomalies.append(Anomaly(
                code="INV_01",
                title="Hàng tồn kho quá lớn so với doanh thu",
                description=(
                    f"HTK = {htk:,.0f}, DT = {dt:,.0f}. "
                    f"Vòng quay HTK rất thấp."
                ),
                risk_level=RiskLevel.MEDIUM,
                category="activity",
                suggestion="Kiểm tra hàng chậm luân chuyển, giảm giá trị.",
            ))

    def _check_expense_structure(self):
        """Cảnh báo: CP QLDN > doanh thu."""
        cp_qldn = self._g(self.kqhdkd, "ct24")
        dt = self._g(self.kqhdkd, "ct01")

        # CP QLDN > DT (nếu có DT)
        if dt > 0 and cp_qldn > dt:
            self.anomalies.append(Anomaly(
                code="EXP_01",
                title="CP QLDN vượt doanh thu",
                description=f"CP QLDN = {cp_qldn:,.0f} > DT = {dt:,.0f}",
                risk_level=RiskLevel.MEDIUM,
                category="activity",
                suggestion="Kiểm tra chi tiết CP, có thể CP không hợp lý.",
            ))

    def _check_related_party_signs(self):
        """Cảnh báo: Phải thu/trả khác lớn (dấu hiệu giao dịch liên kết)."""
        pt_noi_bo = self._g(self.cdkt, "ct133")  # Phải thu khác
        npt_noi_bo = self._g(self.cdkt, "ct416")  # Phải trả khác

        if pt_noi_bo > 500_000_000 or npt_noi_bo > 500_000_000:
            self.anomalies.append(Anomaly(
                code="RP_01",
                title="Công nợ khác lớn (có thể liên kết)",
                description=(
                    f"Phải thu khác = {pt_noi_bo:,.0f}, "
                    f"Phải trả khác = {npt_noi_bo:,.0f}. "
                    f"Cần kiểm tra có phải giao dịch liên kết."
                ),
                risk_level=RiskLevel.MEDIUM,
                category="tax",
                suggestion="Lập hồ sơ xác định giá GDLK nếu có.",
            ))

    def _check_vat_anomaly(self):
        """Cảnh báo: VAT đầu vào lớn (>100 triệu) nhưng chưa có doanh thu."""
        vat = self._g(self.cdkt, "ct151")
        dt = self._g(self.kqhdkd, "ct01")

        if vat > 100_000_000 and dt == 0:
            self.anomalies.append(Anomaly(
                code="VAT_01",
                title="VAT đầu vào lớn nhưng chưa có doanh thu",
                description=(
                    f"Thuế GTGT khấu trừ = {vat:,.0f} nhưng DT = 0. "
                    f"CQT có thể yêu cầu giải trình hoá đơn đầu vào."
                ),
                risk_level=RiskLevel.MEDIUM,
                category="tax",
                suggestion="Đảm bảo hoá đơn đầu vào hợp lệ, có HĐKD thực.",
            ))

    @staticmethod
    def _g(data: Dict, key: str) -> float:
        """Lấy giá trị số từ dict, mặc định 0."""
        if data is None:
            return 0.0
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
