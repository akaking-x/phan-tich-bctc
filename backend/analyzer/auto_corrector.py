"""
Tự động sửa số liệu BCTC cho hợp lệ.

Thuật toán 3 giai đoạn:
- Giai đoạn 1: Sửa nội bộ từng báo cáo (CĐKT, KQHĐKD, LCTT) — bottom-up
- Giai đoạn 2: Sửa chéo giữa báo cáo (CROSS_01, CROSS_02, CROSS_03)
- Giai đoạn 3: Chạy lại giai đoạn 1 để cascade cho nhất quán
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import copy


@dataclass
class CorrectionItem:
    """Một mục sửa đổi."""
    report: str          # cdkt, kqhdkd, lctt
    section: str         # so_cuoi_nam, nam_nay, ...
    code: str            # ct100, ct10, ...
    old_value: float
    new_value: float
    rule_id: str         # CDKT_02, KQHDKD_01, ...
    reason: str


class AutoCorrector:
    """
    Tự động sửa số liệu BCTC theo quy tắc kế toán.
    Nguyên tắc: sửa giá trị tính toán (derived/tổng), giữ nguyên giá trị gốc (source/chi tiết).
    """

    def __init__(self, data: Dict[str, Any]):
        # Deep copy để không ảnh hưởng dữ liệu gốc
        self.data = copy.deepcopy(data)
        self.corrections: List[CorrectionItem] = []

    def correct_all(self) -> List[CorrectionItem]:
        """Chạy toàn bộ 3 giai đoạn sửa. Trả về danh sách corrections."""
        # Giai đoạn 1: Sửa nội bộ
        self._correct_cdkt()
        self._correct_kqhdkd()
        self._correct_lctt()

        # Giai đoạn 2: Sửa chéo
        self._correct_cross_01()
        self._correct_cross_02()
        self._correct_cross_03()

        # Giai đoạn 3: Cascade — chạy lại giai đoạn 1
        self._correct_cdkt()
        self._correct_kqhdkd()
        self._correct_lctt()

        return self.corrections

    def get_corrected_data(self) -> Dict[str, Any]:
        """Trả về dữ liệu đã sửa."""
        return self.data

    # ─── Giai đoạn 1: CĐKT ────────────────────────────────

    def _correct_cdkt(self) -> None:
        """Sửa nội bộ CĐKT bottom-up."""
        cdkt = self.data.get("cdkt", {})
        cn = cdkt.get("so_cuoi_nam", {})
        if not cn:
            return

        # TSNH = sum children
        self._fix_sum(
            cn, "cdkt", "so_cuoi_nam", "ct100",
            ["ct110", "ct120", "ct130", "ct140", "ct150"],
            "CDKT_02", "TS ngan han = sum(ct110..ct150)",
        )

        # TSDH = sum children
        self._fix_sum(
            cn, "cdkt", "so_cuoi_nam", "ct200",
            ["ct210", "ct220", "ct230", "ct240", "ct250", "ct260"],
            "CDKT_03", "TS dai han = sum(ct210..ct260)",
        )

        # Tong TS = TSNH + TSDH
        self._fix_sum(
            cn, "cdkt", "so_cuoi_nam", "ct300",
            ["ct100", "ct200"],
            "CDKT_04", "Tong tai san = ct100 + ct200",
        )

        # No phai tra
        self._fix_sum(
            cn, "cdkt", "so_cuoi_nam", "ct400",
            ["ct410", "ct420"],
            "CDKT_05", "No phai tra = ct410 + ct420",
        )

        # VCSH
        self._fix_sum(
            cn, "cdkt", "so_cuoi_nam", "ct500",
            ["ct511", "ct512", "ct513", "ct514", "ct515", "ct516", "ct517"],
            "CDKT_06", "VCSH = sum(ct511..ct517)",
        )

        # Tong NV = No + VCSH
        self._fix_sum(
            cn, "cdkt", "so_cuoi_nam", "ct600",
            ["ct400", "ct500"],
            "CDKT_07", "Tong nguon von = ct400 + ct500",
        )

        # CDKT_01: ct300 == ct600 — nếu lệch, sửa ct600 theo ct300
        ts = self._g(cn, "ct300")
        nv = self._g(cn, "ct600")
        if ts != nv:
            self._record(cn, "cdkt", "so_cuoi_nam", "ct600", nv, ts,
                         "CDKT_01", "Tong nguon von = Tong tai san")

    # ─── Giai đoạn 1: KQHĐKD ─────────────────────────────

    def _correct_kqhdkd(self) -> None:
        """Sửa nội bộ KQHĐKD theo chuỗi công thức."""
        kqhdkd = self.data.get("kqhdkd", {})
        k = kqhdkd.get("nam_nay", {})
        if not k:
            return

        # ct10 = ct01 - ct02
        expected = self._g(k, "ct01") - self._g(k, "ct02")
        self._fix_formula(k, "kqhdkd", "nam_nay", "ct10", expected,
                          "KQHDKD_01", "DT thuan = ct01 - ct02")

        # ct20 = ct10 - ct11
        expected = self._g(k, "ct10") - self._g(k, "ct11")
        self._fix_formula(k, "kqhdkd", "nam_nay", "ct20", expected,
                          "KQHDKD_02", "LN gop = ct10 - ct11")

        # ct30 = ct20 + ct21 - ct22 - ct23 - ct24
        expected = (self._g(k, "ct20") + self._g(k, "ct21")
                    - self._g(k, "ct22") - self._g(k, "ct23")
                    - self._g(k, "ct24"))
        self._fix_formula(k, "kqhdkd", "nam_nay", "ct30", expected,
                          "KQHDKD_03", "LN thuan HDKD = ct20 + ct21 - ct22 - ct23 - ct24")

        # ct40 = ct31 - ct32
        expected = self._g(k, "ct31") - self._g(k, "ct32")
        self._fix_formula(k, "kqhdkd", "nam_nay", "ct40", expected,
                          "KQHDKD_04", "LN khac = ct31 - ct32")

        # ct50 = ct30 + ct40
        expected = self._g(k, "ct30") + self._g(k, "ct40")
        self._fix_formula(k, "kqhdkd", "nam_nay", "ct50", expected,
                          "KQHDKD_05", "Tong LN truoc thue = ct30 + ct40")

        # ct60 = ct50 - ct51
        expected = self._g(k, "ct50") - self._g(k, "ct51")
        self._fix_formula(k, "kqhdkd", "nam_nay", "ct60", expected,
                          "KQHDKD_06", "LNST = ct50 - ct51")

    # ─── Giai đoạn 1: LCTT ───────────────────────────────

    def _correct_lctt(self) -> None:
        """Sửa nội bộ LCTT bottom-up."""
        lctt = self.data.get("lctt", {})
        l = lctt.get("nam_nay", {})
        if not l:
            return

        # ct20 = sum(ct01..ct07)
        children = [f"ct0{i}" for i in range(1, 8)]
        self._fix_sum(l, "lctt", "nam_nay", "ct20", children,
                      "LCTT_01", "LC tien thuan HDKD = sum(ct01..ct07)")

        # ct30 = sum(ct21..ct25)
        children = [f"ct2{i}" for i in range(1, 6)]
        self._fix_sum(l, "lctt", "nam_nay", "ct30", children,
                      "LCTT_02", "LC tien thuan HD dau tu = sum(ct21..ct25)")

        # ct40 = sum(ct31..ct35)
        children = [f"ct3{i}" for i in range(1, 6)]
        self._fix_sum(l, "lctt", "nam_nay", "ct40", children,
                      "LCTT_03", "LC tien thuan HD tai chinh = sum(ct31..ct35)")

        # ct50 = ct20 + ct30 + ct40
        self._fix_sum(l, "lctt", "nam_nay", "ct50",
                      ["ct20", "ct30", "ct40"],
                      "LCTT_04", "Tang giam tien thuan = ct20 + ct30 + ct40")

        # ct70 = ct50 + ct60 + ct61
        self._fix_sum(l, "lctt", "nam_nay", "ct70",
                      ["ct50", "ct60", "ct61"],
                      "LCTT_05", "Tien cuoi ky = ct50 + ct60 + ct61")

    # ─── Giai đoạn 2: Cross-report ───────────────────────

    def _correct_cross_01(self) -> None:
        """CROSS_01: cdkt.ct517_cuoi = cdkt.ct517_dau + kqhdkd.ct60 → sửa ct517."""
        cdkt = self.data.get("cdkt", {})
        cn = cdkt.get("so_cuoi_nam", {})
        dn = cdkt.get("so_dau_nam", {})
        kqhdkd = self.data.get("kqhdkd", {})
        k = kqhdkd.get("nam_nay", {})
        if not cn or not k:
            return

        ct517_dau = self._g(dn, "ct517")
        ct60 = self._g(k, "ct60")
        expected = ct517_dau + ct60
        actual = self._g(cn, "ct517")

        if actual != expected:
            self._record(cn, "cdkt", "so_cuoi_nam", "ct517", actual, expected,
                         "CROSS_01", f"ct517 cuoi = ct517 dau ({ct517_dau:,.0f}) + ct60 ({ct60:,.0f})")

    def _correct_cross_02(self) -> None:
        """CROSS_02: lctt.ct70 = cdkt.ct110 → sửa lctt.ct70."""
        lctt = self.data.get("lctt", {})
        l = lctt.get("nam_nay", {})
        cdkt = self.data.get("cdkt", {})
        cn = cdkt.get("so_cuoi_nam", {})
        if not l or not cn:
            return

        tien_cdkt = self._g(cn, "ct110")
        tien_lctt = self._g(l, "ct70")

        if tien_lctt != tien_cdkt:
            self._record(l, "lctt", "nam_nay", "ct70", tien_lctt, tien_cdkt,
                         "CROSS_02", f"Tien cuoi ky LCTT = CDKT ct110 ({tien_cdkt:,.0f})")

    def _correct_cross_03(self) -> None:
        """CROSS_03: lctt.ct60 = cdkt_dau.ct110 → sửa lctt.ct60."""
        lctt = self.data.get("lctt", {})
        l = lctt.get("nam_nay", {})
        cdkt = self.data.get("cdkt", {})
        dn = cdkt.get("so_dau_nam", {})
        if not l or not dn:
            return

        tien_dau_cdkt = self._g(dn, "ct110")
        tien_dau_lctt = self._g(l, "ct60")

        if tien_dau_lctt != tien_dau_cdkt:
            self._record(l, "lctt", "nam_nay", "ct60", tien_dau_lctt, tien_dau_cdkt,
                         "CROSS_03", f"Tien dau ky LCTT = CDKT dau ct110 ({tien_dau_cdkt:,.0f})")

    # ─── Helpers ──────────────────────────────────────────

    def _fix_sum(self, data: dict, report: str, section: str,
                 total_key: str, child_keys: list,
                 rule_id: str, reason: str) -> None:
        """Sửa total = sum(children). Nếu khớp rồi thì bỏ qua."""
        children_sum = sum(self._g(data, k) for k in child_keys)
        actual = self._g(data, total_key)
        if actual != children_sum:
            self._record(data, report, section, total_key,
                         actual, children_sum, rule_id, reason)

    def _fix_formula(self, data: dict, report: str, section: str,
                     key: str, expected: float,
                     rule_id: str, reason: str) -> None:
        """Sửa key = expected. Nếu khớp rồi thì bỏ qua."""
        actual = self._g(data, key)
        if actual != expected:
            self._record(data, report, section, key,
                         actual, expected, rule_id, reason)

    def _record(self, data: dict, report: str, section: str,
                code: str, old_value: float, new_value: float,
                rule_id: str, reason: str) -> None:
        """Ghi nhận correction và cập nhật data."""
        # Chuyển về int nếu không có phần thập phân
        new_int = int(new_value) if new_value == int(new_value) else new_value
        data[code] = new_int

        self.corrections.append(CorrectionItem(
            report=report,
            section=section,
            code=code,
            old_value=old_value,
            new_value=new_value,
            rule_id=rule_id,
            reason=reason,
        ))

    @staticmethod
    def _g(data: dict, key: str) -> float:
        """Get value, default 0."""
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
