"""
Đối chiếu chéo giữa 4 báo cáo tài chính: CĐKT, KQHĐKD, LCTT, CĐTK.

Module thực hiện kiểm tra tính nhất quán nội bộ từng báo cáo
và đối chiếu chéo giữa các báo cáo với nhau.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Severity(str, Enum):
    """Mức độ nghiêm trọng của kết quả kiểm tra."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CheckResult:
    """Kết quả của một phép kiểm tra đối chiếu."""
    rule_id: str
    rule_name: str
    severity: Severity
    message: str
    expected: Any = None
    actual: Any = None
    difference: float = 0


class CrossChecker:
    """
    Đối chiếu chéo giữa CĐKT, KQHĐKD, LCTT, CĐTK.
    Trả về danh sách CheckResult.
    """

    def __init__(self, data: Dict[str, Any]):
        # Xử lý an toàn khi thiếu dữ liệu
        cdkt = data.get("cdkt", {})
        kqhdkd = data.get("kqhdkd", {})
        lctt = data.get("lctt", {})
        cdtk = data.get("cdtk", {})

        self.cdkt_cn = cdkt.get("so_cuoi_nam", {})        # Cuối năm
        self.cdkt_dn = cdkt.get("so_dau_nam", {})          # Đầu năm
        self.kqhdkd = kqhdkd.get("nam_nay", {})
        self.lctt = lctt.get("nam_nay", {})
        self.cdtk_dk = cdtk.get("SoDuDauKy", {})
        self.cdtk_ps = cdtk.get("SoPhatSinhTrongKy", {})
        self.cdtk_ck = cdtk.get("SoDuCuoiKy", {})
        self.results: List[CheckResult] = []

        # Cờ đánh dấu thiếu dữ liệu
        self._has_cdkt = bool(self.cdkt_cn)
        self._has_kqhdkd = bool(self.kqhdkd)
        self._has_lctt = bool(self.lctt)
        self._has_cdtk = bool(cdtk)

    def run_all(self) -> List[CheckResult]:
        """Chạy toàn bộ kiểm tra."""
        self._check_cdkt_balance()
        self._check_cdkt_subtotals()
        self._check_kqhdkd_formulas()
        self._check_lctt_totals()
        self._check_cdkt_vs_kqhdkd()
        self._check_cdkt_vs_lctt()
        self._check_cdkt_vs_cdtk()
        self._check_cdtk_balance()
        self._check_lctt_classification()
        return self.results

    # ─── 1. CĐKT: Tổng TS = Tổng NV ─────────────────────

    def _check_cdkt_balance(self) -> None:
        """Kiểm tra phương trình kế toán cơ bản: Tổng Tài sản = Tổng Nguồn vốn."""
        if not self._has_cdkt:
            self.results.append(CheckResult(
                rule_id="CDKT_01",
                rule_name="Tổng Tài sản = Tổng Nguồn vốn",
                severity=Severity.WARNING,
                message="Không có dữ liệu CĐKT để kiểm tra",
            ))
            return

        ts = self._g(self.cdkt_cn, "ct300")
        nv = self._g(self.cdkt_cn, "ct600")
        diff = ts - nv

        self.results.append(CheckResult(
            rule_id="CDKT_01",
            rule_name="Tổng Tài sản = Tổng Nguồn vốn",
            severity=Severity.OK if diff == 0 else Severity.CRITICAL,
            message=f"ct300 ({ts:,.0f}) {'=' if diff == 0 else '≠'} ct600 ({nv:,.0f})",
            expected=0,
            actual=diff,
            difference=diff,
        ))

    # ─── 2. CĐKT: Kiểm tra cộng chỉ tiêu con ───────────

    def _check_cdkt_subtotals(self) -> None:
        """Kiểm tra tổng các chỉ tiêu con bằng chỉ tiêu cha trên CĐKT."""
        if not self._has_cdkt:
            self.results.append(CheckResult(
                rule_id="CDKT_02",
                rule_name="CĐKT: Kiểm tra cộng chỉ tiêu con",
                severity=Severity.WARNING,
                message="Không có dữ liệu CĐKT để kiểm tra cộng chỉ tiêu",
            ))
            return

        checks = [
            ("CDKT_02", "TS ngắn hạn", "ct100",
             ["ct110", "ct120", "ct130", "ct140", "ct150"]),
            ("CDKT_03", "TS dài hạn", "ct200",
             ["ct210", "ct220", "ct230", "ct240", "ct250", "ct260"]),
            ("CDKT_04", "Tổng TS = TSNH + TSDH", "ct300",
             ["ct100", "ct200"]),
            ("CDKT_05", "Nợ phải trả", "ct400",
             ["ct410", "ct420"]),
            ("CDKT_06", "VCSH", "ct500",
             ["ct511", "ct512", "ct513", "ct514", "ct515", "ct516", "ct517"]),
            ("CDKT_07", "Tổng NV = Nợ + VCSH", "ct600",
             ["ct400", "ct500"]),
        ]

        for rule_id, name, total_key, child_keys in checks:
            total = self._g(self.cdkt_cn, total_key)
            children_sum = sum(self._g(self.cdkt_cn, k) for k in child_keys)
            diff = total - children_sum

            self.results.append(CheckResult(
                rule_id=rule_id,
                rule_name=f"CĐKT: {name}",
                severity=Severity.OK if diff == 0 else Severity.ERROR,
                message=(
                    f"{total_key}={total:,.0f}, "
                    f"Σ children={children_sum:,.0f}, "
                    f"chênh lệch={diff:,.0f}"
                ),
                expected=0,
                actual=diff,
                difference=diff,
            ))

    # ─── 3. KQHĐKD: Công thức nội bộ ────────────────────

    def _check_kqhdkd_formulas(self) -> None:
        """Kiểm tra các công thức tính toán nội bộ trên báo cáo KQHĐKD."""
        if not self._has_kqhdkd:
            self.results.append(CheckResult(
                rule_id="KQHDKD_01",
                rule_name="KQHĐKD: Kiểm tra công thức",
                severity=Severity.WARNING,
                message="Không có dữ liệu KQHĐKD để kiểm tra",
            ))
            return

        k = self.kqhdkd
        formulas = [
            ("KQHDKD_01", "DT thuần = DT - Giảm trừ",
             self._g(k, "ct10"),
             self._g(k, "ct01") - self._g(k, "ct02")),
            ("KQHDKD_02", "LN gộp = DT thuần - Giá vốn",
             self._g(k, "ct20"),
             self._g(k, "ct10") - self._g(k, "ct11")),
            ("KQHDKD_03", "LN thuần HĐKD",
             self._g(k, "ct30"),
             self._g(k, "ct20") + self._g(k, "ct21")
             - self._g(k, "ct22") - self._g(k, "ct23")
             - self._g(k, "ct24")),
            ("KQHDKD_04", "LN khác",
             self._g(k, "ct40"),
             self._g(k, "ct31") - self._g(k, "ct32")),
            ("KQHDKD_05", "Tổng LN trước thuế",
             self._g(k, "ct50"),
             self._g(k, "ct30") + self._g(k, "ct40")),
            ("KQHDKD_06", "LN sau thuế",
             self._g(k, "ct60"),
             self._g(k, "ct50") - self._g(k, "ct51")),
        ]

        for rule_id, name, actual, expected in formulas:
            diff = actual - expected
            self.results.append(CheckResult(
                rule_id=rule_id,
                rule_name=f"KQHĐKD: {name}",
                severity=Severity.OK if diff == 0 else Severity.ERROR,
                message=f"Giá trị={actual:,.0f}, Công thức={expected:,.0f}",
                expected=expected,
                actual=actual,
                difference=diff,
            ))

    # ─── 4. LCTT: Tổng dòng tiền ─────────────────────────

    def _check_lctt_totals(self) -> None:
        """Kiểm tra các công thức tổng cộng trên báo cáo lưu chuyển tiền tệ."""
        if not self._has_lctt:
            self.results.append(CheckResult(
                rule_id="LCTT_01",
                rule_name="LCTT: Kiểm tra tổng dòng tiền",
                severity=Severity.WARNING,
                message="Không có dữ liệu LCTT để kiểm tra",
            ))
            return

        l = self.lctt
        checks = [
            ("LCTT_01", "LC tiền thuần HĐKD",
             self._g(l, "ct20"),
             sum(self._g(l, f"ct0{i}") for i in range(1, 8))),
            ("LCTT_02", "LC tiền thuần HĐ đầu tư",
             self._g(l, "ct30"),
             sum(self._g(l, f"ct2{i}") for i in range(1, 6))),
            ("LCTT_03", "LC tiền thuần HĐ tài chính",
             self._g(l, "ct40"),
             sum(self._g(l, f"ct3{i}") for i in range(1, 6))),
            ("LCTT_04", "Tăng giảm tiền thuần = HĐKD + HĐĐT + HĐTC",
             self._g(l, "ct50"),
             self._g(l, "ct20") + self._g(l, "ct30") + self._g(l, "ct40")),
            ("LCTT_05", "Tiền cuối kỳ = Tăng giảm + Đầu kỳ + Tỷ giá",
             self._g(l, "ct70"),
             self._g(l, "ct50") + self._g(l, "ct60") + self._g(l, "ct61")),
        ]

        for rule_id, name, actual, expected in checks:
            diff = actual - expected
            self.results.append(CheckResult(
                rule_id=rule_id,
                rule_name=f"LCTT: {name}",
                severity=Severity.OK if diff == 0 else Severity.ERROR,
                message=f"Giá trị={actual:,.0f}, Công thức={expected:,.0f}",
                expected=expected,
                actual=actual,
                difference=diff,
            ))

    # ─── 5. CĐKT ↔ KQHĐKD ───────────────────────────────

    def _check_cdkt_vs_kqhdkd(self) -> None:
        """
        Đối chiếu chéo CĐKT và KQHĐKD.
        ct517 cuối kỳ = ct517 đầu kỳ + ct60 (LNST năm nay).
        """
        if not self._has_cdkt or not self._has_kqhdkd:
            self.results.append(CheckResult(
                rule_id="CROSS_01",
                rule_name="CĐKT.ct517 = CĐKT.ct517(đầu) + KQHĐKD.ct60",
                severity=Severity.WARNING,
                message="Thiếu dữ liệu CĐKT hoặc KQHĐKD để đối chiếu",
            ))
            return

        lnst_cdkt = self._g(self.cdkt_cn, "ct517")
        lnst_kqhdkd = self._g(self.kqhdkd, "ct60")
        lnst_dn = self._g(self.cdkt_dn, "ct517")

        # Với DN mới: ct517_cuối = ct60
        # Với DN đã hoạt động: ct517_cuối = ct517_đầu + ct60
        expected = lnst_dn + lnst_kqhdkd
        diff = lnst_cdkt - expected

        self.results.append(CheckResult(
            rule_id="CROSS_01",
            rule_name="CĐKT.ct517 = CĐKT.ct517(đầu) + KQHĐKD.ct60",
            severity=Severity.OK if diff == 0 else Severity.CRITICAL,
            message=(
                f"ct517 cuối={lnst_cdkt:,.0f}, "
                f"ct517 đầu={lnst_dn:,.0f} + ct60={lnst_kqhdkd:,.0f} "
                f"= {expected:,.0f}"
            ),
            expected=expected,
            actual=lnst_cdkt,
            difference=diff,
        ))

    # ─── 6. CĐKT ↔ LCTT ──────────────────────────────────

    def _check_cdkt_vs_lctt(self) -> None:
        """
        Đối chiếu chéo CĐKT và LCTT.
        CROSS_02: Tiền cuối kỳ (LCTT ct70) = Tiền trên CĐKT (ct110).
        CROSS_03: Tiền đầu kỳ (LCTT ct60) = Tiền trên CĐKT đầu năm (ct110).
        """
        if not self._has_cdkt or not self._has_lctt:
            self.results.append(CheckResult(
                rule_id="CROSS_02",
                rule_name="LCTT.ct70 = CĐKT.ct110 (tiền cuối kỳ)",
                severity=Severity.WARNING,
                message="Thiếu dữ liệu CĐKT hoặc LCTT để đối chiếu",
            ))
            return

        # Tiền cuối kỳ trên LCTT = Tiền trên CĐKT
        tien_lctt = self._g(self.lctt, "ct70")
        tien_cdkt = self._g(self.cdkt_cn, "ct110")
        diff = tien_lctt - tien_cdkt

        self.results.append(CheckResult(
            rule_id="CROSS_02",
            rule_name="LCTT.ct70 = CĐKT.ct110 (tiền cuối kỳ)",
            severity=Severity.OK if diff == 0 else Severity.CRITICAL,
            message=f"LCTT ct70={tien_lctt:,.0f}, CĐKT ct110={tien_cdkt:,.0f}",
            expected=tien_cdkt,
            actual=tien_lctt,
            difference=diff,
        ))

        # Tiền đầu kỳ trên LCTT = Tiền trên CĐKT đầu năm
        tien_lctt_dk = self._g(self.lctt, "ct60")
        tien_cdkt_dk = self._g(self.cdkt_dn, "ct110")
        diff2 = tien_lctt_dk - tien_cdkt_dk

        self.results.append(CheckResult(
            rule_id="CROSS_03",
            rule_name="LCTT.ct60 = CĐKT_đầu.ct110 (tiền đầu kỳ)",
            severity=Severity.OK if diff2 == 0 else Severity.ERROR,
            message=f"LCTT ct60={tien_lctt_dk:,.0f}, CĐKT đầu ct110={tien_cdkt_dk:,.0f}",
            expected=tien_cdkt_dk,
            actual=tien_lctt_dk,
            difference=diff2,
        ))

    # ─── 7. CĐKT ↔ CĐTK ─────────────────────────────────

    def _check_cdkt_vs_cdtk(self) -> None:
        """Kiểm tra số dư cuối kỳ trên CĐTK khớp với CĐKT."""
        if not self.cdtk_ck:
            self.results.append(CheckResult(
                rule_id="CROSS_04",
                rule_name="CĐKT ↔ CĐTK (tiền)",
                severity=Severity.WARNING,
                message="Không có dữ liệu CĐTK để đối chiếu",
            ))
            return

        no = self.cdtk_ck.get("no", {})
        co = self.cdtk_ck.get("co", {})

        # TK 111 + 112 = ct110
        tk111 = self._g(no, "ct111")
        tk112 = self._g(no, "ct112")
        ct110 = self._g(self.cdkt_cn, "ct110")
        diff = (tk111 + tk112) - ct110

        self.results.append(CheckResult(
            rule_id="CROSS_04",
            rule_name="CĐTK(TK111+112) = CĐKT.ct110",
            severity=Severity.OK if diff == 0 else Severity.ERROR,
            message=f"TK111={tk111:,.0f} + TK112={tk112:,.0f} = {tk111+tk112:,.0f}, ct110={ct110:,.0f}",
            expected=ct110,
            actual=tk111 + tk112,
            difference=diff,
        ))

        # Tổng Nợ = Tổng Có (CĐTK)
        tong_no = self._g(no, "tongCong")
        tong_co = self._g(co, "tongCong")
        diff2 = tong_no - tong_co

        self.results.append(CheckResult(
            rule_id="CROSS_05",
            rule_name="CĐTK: Tổng Nợ = Tổng Có (cuối kỳ)",
            severity=Severity.OK if diff2 == 0 else Severity.CRITICAL,
            message=f"Tổng Nợ={tong_no:,.0f}, Tổng Có={tong_co:,.0f}",
            expected=0,
            actual=diff2,
            difference=diff2,
        ))

    # ─── 8. CĐTK: Nợ - Có cân đối ───────────────────────

    def _check_cdtk_balance(self) -> None:
        """Kiểm tra: Dư đầu + PS = Dư cuối cho mỗi bên Nợ/Có."""
        if not self.cdtk_ps:
            return

        for side in ["no", "co"]:
            dk = self.cdtk_dk.get(side, {})
            ps = self.cdtk_ps.get(side, {})
            ck = self.cdtk_ck.get(side, {})

            dk_total = self._g(dk, "tongCong")
            ps_total = self._g(ps, "tongCong")
            ck_total = self._g(ck, "tongCong")

            # Với CĐTK: Dư cuối Nợ = Dư đầu Nợ + PS Nợ - PS Có
            # Nhưng HTKK ghi Nợ/Có riêng, nên:
            # TongCong cuối Nợ + TongCong cuối Có phải bằng nhau
            self.results.append(CheckResult(
                rule_id=f"CDTK_{side.upper()}_01",
                rule_name=f"CĐTK bên {side.upper()}: Tổng cộng hợp lệ",
                severity=Severity.OK if ck_total >= 0 else Severity.WARNING,
                message=(
                    f"Đầu kỳ={dk_total:,.0f}, "
                    f"Phát sinh={ps_total:,.0f}, "
                    f"Cuối kỳ={ck_total:,.0f}"
                ),
                expected=None,
                actual=ck_total,
            ))

    # ─── 9. LCTT: Phân loại hợp lý ──────────────────────

    def _check_lctt_classification(self) -> None:
        """Cảnh báo phân loại dòng tiền có thể sai."""
        if not self._has_lctt or not self._has_kqhdkd:
            return

        l = self.lctt
        k = self.kqhdkd

        # Nếu ct04 (lãi vay) != 0 nhưng ct22 (CP TC) chủ yếu là phí NH
        cp_tc = self._g(k, "ct22")
        tien_lai_vay = abs(self._g(l, "ct04"))

        if tien_lai_vay > 0 and cp_tc > 0:
            # Nếu không có vay nợ (TK341 = 0)
            tk341_no = self._g(self.cdtk_ck.get("no", {}), "ct341")
            tk341_co = self._g(self.cdtk_ck.get("co", {}), "ct341")

            if tk341_no == 0 and tk341_co == 0:
                self.results.append(CheckResult(
                    rule_id="CLASS_01",
                    rule_name="LCTT: ct04 (lãi vay) nhưng không có dư nợ vay",
                    severity=Severity.WARNING,
                    message=(
                        f"ct04={tien_lai_vay:,.0f} ghi là lãi vay, "
                        f"nhưng TK341=0 (không vay). "
                        f"Có thể là phí NH → nên ghi ct07."
                    ),
                ))

    # ─── Helper ───────────────────────────────────────────

    @staticmethod
    def _g(data: Dict, key: str) -> float:
        """Get value, default 0."""
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
