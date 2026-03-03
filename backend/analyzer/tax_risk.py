# backend/analyzer/tax_risk.py

"""
Đánh giá rủi ro thuế trong BCTC.

Bao gồm:
- Rủi ro chuyển giá (Transfer Pricing)
- Rủi ro thuế TNDN (CIT)
- Rủi ro thuế GTGT (VAT)
- Rủi ro thuế TNCN (PIT)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class TaxRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaxRiskItem:
    code: str
    risk_type: str          # "transfer_pricing", "cit", "vat", "pit"
    title: str
    risk_level: TaxRiskLevel
    description: str
    suggestion: str
    data: Optional[Dict[str, Any]] = field(default=None)


class TaxRiskAssessor:
    """
    Đánh giá rủi ro thuế dựa trên dữ liệu BCTC.

    Phân tích 4 loại rủi ro chính:
    - Transfer pricing (chuyển giá/giao dịch liên kết)
    - CIT (thuế TNDN)
    - VAT (thuế GTGT)
    - PIT (thuế TNCN)
    """

    def __init__(self, parsed_data: Dict[str, Any]):
        self.data = parsed_data
        self.cdkt = parsed_data.get("cdkt", {}).get("so_cuoi_nam", {})
        self.cdkt_dn = parsed_data.get("cdkt", {}).get("so_dau_nam", {})
        self.kqhdkd = parsed_data.get("kqhdkd", {}).get("nam_nay", {})
        self.lctt = parsed_data.get("lctt", {}).get("nam_nay", {})
        self.cdtk_ck = parsed_data.get("cdtk", {}).get("SoDuCuoiKy", {})
        self.cdtk_ps = parsed_data.get("cdtk", {}).get("SoPhatSinhTrongKy", {})
        self.risks: List[TaxRiskItem] = []

    def assess_all(self) -> List[TaxRiskItem]:
        """Chạy toàn bộ đánh giá rủi ro thuế."""
        self._check_transfer_pricing_risk()
        self._check_cit_risk()
        self._check_vat_risk()
        self._check_pit_risk()
        return self.risks

    # ─── Transfer Pricing (Chuyển giá) ─────────────────────

    def _check_transfer_pricing_risk(self):
        """
        Đánh giá rủi ro chuyển giá / giao dịch liên kết.

        Dấu hiệu:
        - Phải thu/trả nội bộ lớn (TK136, TK336)
        - Phải thu/trả khác lớn bất thường (TK138, TK338)
        - Đầu tư vào đơn vị khác (TK228) lớn
        - Lỗ liên tục khi có GDLK
        """
        # Kiểm tra TK phải thu nội bộ / phải trả nội bộ
        no_ck = self.cdtk_ck.get("no", {})
        co_ck = self.cdtk_ck.get("co", {})

        tk136 = self._g(no_ck, "ct136")  # Phải thu nội bộ
        tk336 = self._g(co_ck, "ct336")  # Phải trả nội bộ
        tk228 = self._g(no_ck, "ct228")  # Đầu tư góp vốn vào đơn vị khác
        tk138 = self._g(no_ck, "ct138")  # Phải thu khác
        tk338 = self._g(co_ck, "ct338")  # Phải trả, phải nộp khác

        tong_ts = self._g(self.cdkt, "ct300")
        lnst = self._g(self.kqhdkd, "ct60")

        # Có đầu tư vào đơn vị khác -> có khả năng GDLK
        has_related_parties = tk228 > 0 or tk136 > 0 or tk336 > 0

        if has_related_parties:
            # DN có GDLK mà lỗ -> rủi ro cao
            if lnst < 0:
                self.risks.append(TaxRiskItem(
                    code="TP_01",
                    risk_type="transfer_pricing",
                    title="Lỗ khi có dấu hiệu giao dịch liên kết",
                    risk_level=TaxRiskLevel.HIGH,
                    description=(
                        f"DN có đầu tư/phải thu nội bộ "
                        f"(TK228={tk228:,.0f}, TK136={tk136:,.0f}, TK336={tk336:,.0f}) "
                        f"nhưng LNST = {lnst:,.0f}. "
                        f"CQT có thể yêu cầu lập hồ sơ xác định giá GDLK."
                    ),
                    suggestion=(
                        "Lập hồ sơ xác định giá giao dịch liên kết theo Nghị định 132/2020. "
                        "Chuẩn bị hồ sơ Local File, Master File nếu thuộc diện bắt buộc."
                    ),
                    data={
                        "tk228": tk228,
                        "tk136": tk136,
                        "tk336": tk336,
                        "lnst": lnst,
                    },
                ))
            else:
                self.risks.append(TaxRiskItem(
                    code="TP_02",
                    risk_type="transfer_pricing",
                    title="Có dấu hiệu giao dịch liên kết",
                    risk_level=TaxRiskLevel.MEDIUM,
                    description=(
                        f"DN có đầu tư/công nợ nội bộ "
                        f"(TK228={tk228:,.0f}, TK136={tk136:,.0f}, TK336={tk336:,.0f}). "
                        f"Cần đảm bảo tuân thủ quy định về GDLK."
                    ),
                    suggestion=(
                        "Rà soát các giao dịch với bên liên kết, đảm bảo giá thị trường. "
                        "Nộp phụ lục GDLK kèm tờ khai quyết toán thuế TNDN nếu thuộc diện."
                    ),
                    data={
                        "tk228": tk228,
                        "tk136": tk136,
                        "tk336": tk336,
                    },
                ))

        # Phải thu/trả khác quá lớn so với tổng TS
        if tong_ts > 0:
            pt_khac_ratio = tk138 / tong_ts if tk138 > 0 else 0
            npt_khac_ratio = tk338 / tong_ts if tk338 > 0 else 0

            if pt_khac_ratio > 0.3 or npt_khac_ratio > 0.3:
                self.risks.append(TaxRiskItem(
                    code="TP_03",
                    risk_type="transfer_pricing",
                    title="Phải thu/trả khác chiếm tỷ trọng lớn",
                    risk_level=TaxRiskLevel.MEDIUM,
                    description=(
                        f"TK138 (phải thu khác) = {tk138:,.0f} ({pt_khac_ratio:.0%} tổng TS), "
                        f"TK338 (phải trả khác) = {tk338:,.0f} ({npt_khac_ratio:.0%} tổng TS). "
                        f"Có thể ẩn chứa giao dịch liên kết không kê khai."
                    ),
                    suggestion=(
                        "Chi tiết hoá các khoản phải thu/trả khác. "
                        "Xác định đối tượng công nợ, bản chất giao dịch."
                    ),
                    data={
                        "tk138": tk138,
                        "tk338": tk338,
                        "pt_khac_ratio": pt_khac_ratio,
                        "npt_khac_ratio": npt_khac_ratio,
                    },
                ))

    # ─── CIT (Thuế TNDN) ──────────────────────────────────

    def _check_cit_risk(self):
        """
        Đánh giá rủi ro thuế TNDN.

        Dấu hiệu:
        - Thuế suất hiệu dụng bất thường (quá thấp hoặc quá cao so với 20%)
        - Lỗ liên tục nhiều năm
        - Chi phí lớn bất thường so với doanh thu
        """
        lntt = self._g(self.kqhdkd, "ct50")  # LN trước thuế
        cp_thue = self._g(self.kqhdkd, "ct51")  # CP thuế TNDN
        dt = self._g(self.kqhdkd, "ct10")  # DT thuần
        lnst = self._g(self.kqhdkd, "ct60")  # LNST
        gia_von = self._g(self.kqhdkd, "ct11")  # Giá vốn
        cp_tc = self._g(self.kqhdkd, "ct22")  # CP tài chính
        cp_qldn = self._g(self.kqhdkd, "ct24")  # CP QLDN

        # Thuế suất hiệu dụng
        if lntt > 0 and cp_thue >= 0:
            effective_rate = cp_thue / lntt if lntt != 0 else 0
            standard_rate = 0.20  # Thuế suất chuẩn 20%

            if effective_rate < 0.10 and lntt > 100_000_000:
                self.risks.append(TaxRiskItem(
                    code="CIT_01",
                    risk_type="cit",
                    title="Thuế suất hiệu dụng thấp bất thường",
                    risk_level=TaxRiskLevel.HIGH,
                    description=(
                        f"LNTT = {lntt:,.0f}, CP thuế TNDN = {cp_thue:,.0f}. "
                        f"Thuế suất hiệu dụng = {effective_rate:.1%} "
                        f"(chuẩn 20%). Có thể DN đang hưởng ưu đãi hoặc "
                        f"kê khai chưa đúng."
                    ),
                    suggestion=(
                        "Kiểm tra ưu đãi thuế TNDN (nếu có). "
                        "Đối chiếu với tờ khai quyết toán thuế TNDN. "
                        "Rà soát các khoản chi phí không được trừ."
                    ),
                    data={
                        "lntt": lntt,
                        "cp_thue": cp_thue,
                        "effective_rate": effective_rate,
                    },
                ))
            elif effective_rate > 0.25 and lntt > 100_000_000:
                self.risks.append(TaxRiskItem(
                    code="CIT_02",
                    risk_type="cit",
                    title="Thuế suất hiệu dụng cao bất thường",
                    risk_level=TaxRiskLevel.MEDIUM,
                    description=(
                        f"LNTT = {lntt:,.0f}, CP thuế TNDN = {cp_thue:,.0f}. "
                        f"Thuế suất hiệu dụng = {effective_rate:.1%} > 20%. "
                        f"Có thể có chi phí không được trừ đáng kể."
                    ),
                    suggestion=(
                        "Rà soát các khoản chi phí không được trừ khi tính thuế. "
                        "Kiểm tra chênh lệch tạm thời và chênh lệch vĩnh viễn."
                    ),
                    data={
                        "lntt": lntt,
                        "cp_thue": cp_thue,
                        "effective_rate": effective_rate,
                    },
                ))

        # Lỗ nhưng có doanh thu -> kiểm tra chi phí
        if dt > 0 and lnst < 0:
            tong_cp = gia_von + cp_tc + cp_qldn
            cp_ratio = tong_cp / dt if dt != 0 else 0

            self.risks.append(TaxRiskItem(
                code="CIT_03",
                risk_type="cit",
                title="Lỗ dù có doanh thu - cần rà soát chi phí",
                risk_level=TaxRiskLevel.MEDIUM,
                description=(
                    f"DT thuần = {dt:,.0f} nhưng LNST = {lnst:,.0f}. "
                    f"Tổng CP = {tong_cp:,.0f} ({cp_ratio:.0%} DT). "
                    f"CQT có thể yêu cầu giải trình chi phí."
                ),
                suggestion=(
                    "Rà soát tính hợp lý của chi phí. "
                    "Kiểm tra hoá đơn, chứng từ đầu vào. "
                    "Đặc biệt lưu ý các khoản CP không có hoá đơn hợp lệ."
                ),
                data={
                    "dt": dt,
                    "lnst": lnst,
                    "gia_von": gia_von,
                    "cp_tc": cp_tc,
                    "cp_qldn": cp_qldn,
                    "cp_ratio": cp_ratio,
                },
            ))

        # Doanh thu = 0 nhưng có chi phí lớn
        if dt == 0 and cp_qldn > 100_000_000:
            self.risks.append(TaxRiskItem(
                code="CIT_04",
                risk_type="cit",
                title="Không có doanh thu nhưng chi phí lớn",
                risk_level=TaxRiskLevel.MEDIUM,
                description=(
                    f"DT = 0 nhưng CP QLDN = {cp_qldn:,.0f}. "
                    f"CQT có thể không chấp nhận CP khi chưa có doanh thu."
                ),
                suggestion=(
                    "Kiểm tra giai đoạn DN (mới thành lập, chuẩn bị sản xuất?). "
                    "Các CP phát sinh trước khi có DT có thể bị loại trừ khi quyết toán thuế."
                ),
                data={"dt": dt, "cp_qldn": cp_qldn},
            ))

    # ─── VAT (Thuế GTGT) ──────────────────────────────────

    def _check_vat_risk(self):
        """
        Đánh giá rủi ro thuế GTGT.

        Dấu hiệu:
        - VAT đầu vào tồn đọng lớn không có DT
        - Chênh lệch VAT đầu vào với giá vốn/chi phí
        - VAT đầu vào lớn hơn VAT đầu ra bất thường
        """
        # Số dư cuối kỳ
        no_ck = self.cdtk_ck.get("no", {})
        co_ck = self.cdtk_ck.get("co", {})

        tk133 = self._g(no_ck, "ct133")    # Thuế GTGT đầu vào được khấu trừ
        tk1331 = self._g(no_ck, "ct1331")  # VAT hàng hoá, DV
        tk1332 = self._g(no_ck, "ct1332")  # VAT TSCĐ
        tk3331 = self._g(co_ck, "ct3331")  # Thuế GTGT phải nộp

        # Phát sinh trong kỳ
        no_ps = self.cdtk_ps.get("no", {})
        co_ps = self.cdtk_ps.get("co", {})

        vat_dv_ps_no = self._g(no_ps, "ct133")   # PS Nợ TK133 (VAT đầu vào phát sinh)
        vat_dn_ps_co = self._g(co_ps, "ct3331")  # PS Có TK3331 (VAT đầu ra phát sinh)

        dt = self._g(self.kqhdkd, "ct01")
        gia_von = self._g(self.kqhdkd, "ct11")
        vat_cdkt = self._g(self.cdkt, "ct151")  # Thuế GTGT được khấu trừ trên CĐKT

        # VAT đầu vào tồn đọng lớn khi không có DT
        if vat_cdkt > 100_000_000 and dt == 0:
            self.risks.append(TaxRiskItem(
                code="VAT_01",
                risk_type="vat",
                title="VAT đầu vào tồn đọng lớn, chưa có doanh thu",
                risk_level=TaxRiskLevel.HIGH,
                description=(
                    f"Thuế GTGT được khấu trừ = {vat_cdkt:,.0f} nhưng DT = 0. "
                    f"CQT sẽ rà soát hoá đơn đầu vào khi DN xin hoàn thuế."
                ),
                suggestion=(
                    "Đảm bảo hoá đơn đầu vào hợp lệ, hợp pháp. "
                    "Lưu ý DN mới thành lập xin hoàn thuế sẽ bị kiểm tra trước."
                ),
                data={"vat_cdkt": vat_cdkt, "dt": dt},
            ))

        # VAT đầu vào phát sinh lớn so với giá vốn/mua hàng
        if dt > 0 and gia_von > 0:
            # Ước tính VAT đầu vào hợp lý: khoảng 10% (giá vốn + CP)
            cp_qldn = self._g(self.kqhdkd, "ct24")
            vat_uoc_tinh = (gia_von + cp_qldn) * 0.10
            if vat_dv_ps_no > 0 and vat_uoc_tinh > 0:
                vat_ratio = vat_dv_ps_no / vat_uoc_tinh
                if vat_ratio > 1.5:
                    self.risks.append(TaxRiskItem(
                        code="VAT_02",
                        risk_type="vat",
                        title="VAT đầu vào cao bất thường so với chi phí",
                        risk_level=TaxRiskLevel.MEDIUM,
                        description=(
                            f"VAT đầu vào PS = {vat_dv_ps_no:,.0f}, "
                            f"ước tính hợp lý ~ {vat_uoc_tinh:,.0f} "
                            f"(dựa trên giá vốn + CP QLDN). "
                            f"Chênh lệch có thể do mua sắm TSCĐ hoặc "
                            f"hoá đơn đầu vào không thực."
                        ),
                        suggestion=(
                            "Đối chiếu bảng kê hoá đơn đầu vào với sổ mua hàng. "
                            "Kiểm tra hoá đơn TSCĐ riêng."
                        ),
                        data={
                            "vat_ps_no": vat_dv_ps_no,
                            "vat_uoc_tinh": vat_uoc_tinh,
                            "vat_ratio": vat_ratio,
                        },
                    ))

        # Tồn dư TK133 cuối kỳ lớn -> có thể hoàn thuế hoặc sai sót
        if tk133 > 500_000_000:
            self.risks.append(TaxRiskItem(
                code="VAT_03",
                risk_type="vat",
                title="Số dư thuế GTGT được khấu trừ lớn",
                risk_level=TaxRiskLevel.MEDIUM,
                description=(
                    f"TK133 cuối kỳ = {tk133:,.0f}. "
                    f"DN có thể đang tích luỹ VAT đầu vào chưa khấu trừ hết. "
                    f"Cần xem xét xin hoàn thuế hoặc kiểm tra sai sót."
                ),
                suggestion=(
                    "Kiểm tra đã kê khai đầy đủ VAT đầu ra chưa. "
                    "Xem xét nộp hồ sơ hoàn thuế nếu đủ điều kiện."
                ),
                data={
                    "tk133": tk133,
                    "tk1331": tk1331,
                    "tk1332": tk1332,
                },
            ))

    # ─── PIT (Thuế TNCN) ──────────────────────────────────

    def _check_pit_risk(self):
        """
        Đánh giá rủi ro thuế TNCN.

        Dấu hiệu:
        - Chi phí lương lớn nhưng thuế TNCN nộp thấp
        - Phải trả người lao động (TK334) tồn đọng lớn
        """
        no_ck = self.cdtk_ck.get("no", {})
        co_ck = self.cdtk_ck.get("co", {})
        no_ps = self.cdtk_ps.get("no", {})
        co_ps = self.cdtk_ps.get("co", {})

        tk334_co = self._g(co_ck, "ct334")  # Phải trả NLĐ (dư Có)
        tk3335 = self._g(co_ck, "ct3335")   # Thuế TNCN phải nộp (dư Có)

        # PS Có TK334 = Tổng chi phí lương tính trong kỳ
        luong_ps_co = self._g(co_ps, "ct334")
        # PS Nợ TK3335 = Thuế TNCN đã nộp
        thue_tncn_nop = self._g(no_ps, "ct3335")
        # PS Có TK3335 = Thuế TNCN phải nộp phát sinh
        thue_tncn_phat_sinh = self._g(co_ps, "ct3335")

        cp_qldn = self._g(self.kqhdkd, "ct24")  # CP QLDN (bao gồm lương)

        # Chi phí lương lớn nhưng thuế TNCN thấp
        if luong_ps_co > 500_000_000 and thue_tncn_phat_sinh >= 0:
            # Ước tính thuế TNCN tối thiểu (giả sử ~ 5-10% quỹ lương)
            thue_uoc_tinh_min = luong_ps_co * 0.05

            if thue_tncn_phat_sinh < thue_uoc_tinh_min:
                self.risks.append(TaxRiskItem(
                    code="PIT_01",
                    risk_type="pit",
                    title="Chi phí lương lớn nhưng thuế TNCN thấp",
                    risk_level=TaxRiskLevel.MEDIUM,
                    description=(
                        f"Tổng lương PS (TK334 Có) = {luong_ps_co:,.0f}, "
                        f"thuế TNCN PS (TK3335 Có) = {thue_tncn_phat_sinh:,.0f}. "
                        f"Ước tính thuế TNCN tối thiểu ~ {thue_uoc_tinh_min:,.0f}. "
                        f"Có thể DN chưa khấu trừ thuế TNCN đầy đủ."
                    ),
                    suggestion=(
                        "Rà soát bảng lương, hợp đồng lao động. "
                        "Kiểm tra khấu trừ thuế TNCN theo biểu luỹ tiến hoặc toàn phần. "
                        "Đối chiếu với tờ khai thuế TNCN hàng tháng/quý."
                    ),
                    data={
                        "luong_ps_co": luong_ps_co,
                        "thue_tncn_ps": thue_tncn_phat_sinh,
                        "thue_uoc_tinh_min": thue_uoc_tinh_min,
                    },
                ))

        # Nợ lương tồn đọng lớn
        if tk334_co > 500_000_000:
            self.risks.append(TaxRiskItem(
                code="PIT_02",
                risk_type="pit",
                title="Phải trả người lao động tồn đọng lớn",
                risk_level=TaxRiskLevel.MEDIUM,
                description=(
                    f"TK334 dư Có = {tk334_co:,.0f}. "
                    f"Nợ lương lớn có thể do chưa trả lương hoặc "
                    f"trích lương nhưng chưa chi."
                ),
                suggestion=(
                    "Kiểm tra lương đã chi trả chưa. "
                    "CP lương chưa chi trả có thể bị loại trừ khi quyết toán thuế TNDN. "
                    "Theo Thông tư 78/2014, CP tiền lương chưa chi trả trước thời điểm "
                    "nộp hồ sơ quyết toán sẽ không được trừ."
                ),
                data={"tk334_co": tk334_co},
            ))

        # Thuế TNCN phải nộp tồn đọng
        if tk3335 > 50_000_000:
            self.risks.append(TaxRiskItem(
                code="PIT_03",
                risk_type="pit",
                title="Thuế TNCN phải nộp tồn đọng",
                risk_level=TaxRiskLevel.HIGH,
                description=(
                    f"TK3335 dư Có = {tk3335:,.0f}. "
                    f"DN đã khấu trừ thuế TNCN nhưng chưa nộp ngân sách. "
                    f"Có thể phát sinh tiền phạt chậm nộp."
                ),
                suggestion=(
                    "Nộp ngay số thuế TNCN đã khấu trừ. "
                    "Tính tiền chậm nộp (0.03%/ngày theo Luật Quản lý thuế 2019). "
                    "Đối chiếu với tờ khai thuế TNCN đã nộp."
                ),
                data={"tk3335": tk3335},
            ))

    # ─── Helper ────────────────────────────────────────────

    @staticmethod
    def _g(data: Dict, key: str) -> float:
        """Lấy giá trị số từ dict, mặc định 0."""
        if data is None:
            return 0.0
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
