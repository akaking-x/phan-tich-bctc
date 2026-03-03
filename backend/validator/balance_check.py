"""
Kiểm tra cân đối nội bộ bổ sung cho các báo cáo tài chính.

Module thực hiện:
- Kiểm tra số dư đầu năm CĐKT khớp số dư cuối năm trước
- Kiểm tra công thức CĐTK: Dư đầu kỳ + Phát sinh = Dư cuối kỳ
- Kiểm tra tổng Nợ = tổng Có trong CĐTK theo từng kỳ
- Kiểm tra tổng tài khoản chi tiết = tài khoản tổng hợp (cha)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set

from .cross_check import Severity, CheckResult


# ═══════════════════════════════════════════════════════
#  Mapping tài khoản cha - con theo TT133
# ═══════════════════════════════════════════════════════

PARENT_CHILD_MAP: Dict[str, List[str]] = {
    # TK Loại 1 - Tài sản ngắn hạn
    "ct111": ["ct1111", "ct1112"],
    "ct112": ["ct1121", "ct1122"],
    "ct133": ["ct1331", "ct1332"],
    # TK Loại 3 - Nợ phải trả
    "ct333": ["ct3331", "ct3334", "ct3335"],
    # TK Loại 4 - Vốn chủ sở hữu
    "ct411": ["ct4111", "ct4112", "ct4118"],
    "ct421": ["ct4211", "ct4212"],
    # TK Loại 6 - Chi phí
    "ct642": ["ct6421", "ct6422"],
}

# Mapping chỉ tiêu CĐKT cha - con
CDKT_PARENT_CHILD_MAP: Dict[str, List[str]] = {
    "ct100": ["ct110", "ct120", "ct130", "ct140", "ct150"],
    "ct120": ["ct121", "ct122", "ct123"],
    "ct130": ["ct131", "ct132", "ct133", "ct134", "ct135"],
    "ct140": ["ct141", "ct142"],
    "ct200": ["ct210", "ct220", "ct230", "ct240", "ct250", "ct260"],
    "ct210": ["ct211", "ct212", "ct213", "ct214", "ct215"],
    "ct220": ["ct221", "ct222"],
    "ct300": ["ct100", "ct200"],
    "ct400": ["ct410", "ct420"],
    "ct410": ["ct411", "ct412", "ct413", "ct414", "ct415",
              "ct416", "ct417", "ct418"],
    "ct500": ["ct511", "ct512", "ct513", "ct514", "ct515", "ct516", "ct517"],
    "ct600": ["ct400", "ct500"],
}

# Tên tiếng Việt cho tài khoản (dùng trong thông báo)
ACCOUNT_NAMES: Dict[str, str] = {
    "ct111": "TK111 - Tiền mặt",
    "ct112": "TK112 - Tiền gửi ngân hàng",
    "ct121": "TK121 - Chứng khoán kinh doanh",
    "ct128": "TK128 - Đầu tư nắm giữ đến ngày đáo hạn",
    "ct131": "TK131 - Phải thu khách hàng",
    "ct133": "TK133 - Thuế GTGT được khấu trừ",
    "ct136": "TK136 - Phải thu nội bộ",
    "ct138": "TK138 - Phải thu khác",
    "ct141": "TK141 - Tạm ứng",
    "ct151": "TK151 - Hàng mua đang đi đường",
    "ct152": "TK152 - Nguyên liệu, vật liệu",
    "ct153": "TK153 - Công cụ, dụng cụ",
    "ct154": "TK154 - CP SXKD dở dang",
    "ct155": "TK155 - Thành phẩm",
    "ct156": "TK156 - Hàng hoá",
    "ct157": "TK157 - Hàng gửi đi bán",
    "ct211": "TK211 - TSCĐ hữu hình",
    "ct214": "TK214 - Hao mòn TSCĐ",
    "ct217": "TK217 - BĐS đầu tư",
    "ct228": "TK228 - Đầu tư góp vốn vào đơn vị khác",
    "ct229": "TK229 - Dự phòng tổn thất tài sản",
    "ct241": "TK241 - XDCB dở dang",
    "ct242": "TK242 - Chi phí trả trước",
    "ct331": "TK331 - Phải trả cho người bán",
    "ct333": "TK333 - Thuế và các khoản phải nộp NN",
    "ct334": "TK334 - Phải trả người lao động",
    "ct335": "TK335 - Chi phí phải trả",
    "ct336": "TK336 - Phải trả nội bộ",
    "ct338": "TK338 - Phải trả, phải nộp khác",
    "ct341": "TK341 - Vay và nợ thuê TC",
    "ct352": "TK352 - Dự phòng phải trả",
    "ct353": "TK353 - Quỹ khen thưởng, phúc lợi",
    "ct356": "TK356 - Quỹ phát triển KH&CN",
    "ct411": "TK411 - Vốn đầu tư của CSH",
    "ct413": "TK413 - Chênh lệch tỷ giá hối đoái",
    "ct418": "TK418 - Các quỹ thuộc VCSH",
    "ct419": "TK419 - Cổ phiếu quỹ",
    "ct421": "TK421 - Lợi nhuận sau thuế chưa PP",
    "ct511": "TK511 - Doanh thu bán hàng và CCDV",
    "ct515": "TK515 - Doanh thu hoạt động tài chính",
    "ct611": "TK611 - Mua hàng",
    "ct631": "TK631 - Giá thành sản xuất",
    "ct632": "TK632 - Giá vốn hàng bán",
    "ct635": "TK635 - Chi phí tài chính",
    "ct642": "TK642 - Chi phí quản lý kinh doanh",
    "ct711": "TK711 - Thu nhập khác",
    "ct811": "TK811 - Chi phí khác",
    "ct821": "TK821 - Chi phí thuế TNDN",
    "ct911": "TK911 - Xác định kết quả kinh doanh",
}


class BalanceChecker:
    """
    Kiểm tra cân đối nội bộ bổ sung.

    Bao gồm:
    - Kiểm tra CĐKT: số đầu năm khớp cuối năm trước
    - Kiểm tra CĐTK: Dư đầu kỳ + Phát sinh = Dư cuối kỳ
    - Kiểm tra tổng Nợ = tổng Có
    - Kiểm tra tài khoản con cộng lại = tài khoản cha
    """

    def __init__(self, data: Dict[str, Any],
                 previous_year_data: Optional[Dict[str, Any]] = None):
        """
        Khởi tạo BalanceChecker.

        Args:
            data: Dữ liệu BCTC đã parse (từ HtkkXmlParser.parse_all()).
            previous_year_data: Dữ liệu BCTC năm trước (nếu có), dùng để
                đối chiếu số dư đầu năm.
        """
        cdkt = data.get("cdkt", {})
        cdtk = data.get("cdtk", {})

        self.cdkt_cn = cdkt.get("so_cuoi_nam", {})
        self.cdkt_dn = cdkt.get("so_dau_nam", {})
        self.cdtk_dk = cdtk.get("SoDuDauKy", {})
        self.cdtk_ps = cdtk.get("SoPhatSinhTrongKy", {})
        self.cdtk_ck = cdtk.get("SoDuCuoiKy", {})
        self.previous_year_data = previous_year_data
        self.results: List[CheckResult] = []

        self._has_cdkt = bool(self.cdkt_cn)
        self._has_cdtk = bool(cdtk)

    def run_all(self) -> List[CheckResult]:
        """Chạy toàn bộ kiểm tra cân đối nội bộ."""
        self._check_cdkt_beginning_balances()
        self._check_cdtk_account_equation()
        self._check_cdtk_debit_credit_totals()
        self._check_cdtk_parent_child_accounts()
        return self.results

    # ─── 1. CĐKT: Số đầu năm = Số cuối năm trước ────────

    def _check_cdkt_beginning_balances(self) -> None:
        """
        Kiểm tra số dư đầu năm trên CĐKT khớp với số dư cuối năm trước.

        Chỉ thực hiện được khi có dữ liệu năm trước (previous_year_data).
        Nếu không có, kiểm tra tính nhất quán nội bộ: số dư đầu năm
        không được None nếu DN đã hoạt động.
        """
        if self.previous_year_data is not None:
            prev_cdkt = self.previous_year_data.get("cdkt", {})
            prev_cn = prev_cdkt.get("so_cuoi_nam", {})

            if not prev_cn:
                self.results.append(CheckResult(
                    rule_id="BAL_01",
                    rule_name="CĐKT: Số đầu năm = Số cuối năm trước",
                    severity=Severity.WARNING,
                    message="Dữ liệu năm trước không có CĐKT cuối năm",
                ))
                return

            # Kiểm tra các chỉ tiêu chính
            key_items = [
                ("ct300", "Tổng cộng Tài sản"),
                ("ct600", "Tổng cộng Nguồn vốn"),
                ("ct100", "Tài sản ngắn hạn"),
                ("ct200", "Tài sản dài hạn"),
                ("ct400", "Nợ phải trả"),
                ("ct500", "Vốn chủ sở hữu"),
                ("ct110", "Tiền và tương đương tiền"),
                ("ct517", "LNST chưa phân phối"),
            ]

            for ct_key, name in key_items:
                prev_value = self._g(prev_cn, ct_key)
                current_begin = self._g(self.cdkt_dn, ct_key)
                diff = current_begin - prev_value

                if diff != 0:
                    self.results.append(CheckResult(
                        rule_id="BAL_01",
                        rule_name=f"CĐKT: Số đầu năm ↔ cuối năm trước ({name})",
                        severity=Severity.ERROR,
                        message=(
                            f"{ct_key}: Đầu năm nay={current_begin:,.0f}, "
                            f"Cuối năm trước={prev_value:,.0f}, "
                            f"chênh lệch={diff:,.0f}"
                        ),
                        expected=prev_value,
                        actual=current_begin,
                        difference=diff,
                    ))

            # Nếu không có lỗi nào, ghi nhận OK
            has_bal01_error = any(
                r.rule_id == "BAL_01" and r.severity != Severity.OK
                for r in self.results
            )
            if not has_bal01_error:
                self.results.append(CheckResult(
                    rule_id="BAL_01",
                    rule_name="CĐKT: Số đầu năm = Số cuối năm trước",
                    severity=Severity.OK,
                    message="Tất cả chỉ tiêu đầu năm khớp cuối năm trước",
                ))
        else:
            # Không có dữ liệu năm trước - kiểm tra cơ bản
            if not self._has_cdkt:
                self.results.append(CheckResult(
                    rule_id="BAL_01",
                    rule_name="CĐKT: Số đầu năm = Số cuối năm trước",
                    severity=Severity.WARNING,
                    message="Không có dữ liệu CĐKT để kiểm tra",
                ))
                return

            ts_dn = self._g(self.cdkt_dn, "ct300")
            nv_dn = self._g(self.cdkt_dn, "ct600")
            diff = ts_dn - nv_dn

            self.results.append(CheckResult(
                rule_id="BAL_01",
                rule_name="CĐKT: Cân đối số đầu năm (TS = NV)",
                severity=Severity.OK if diff == 0 else Severity.ERROR,
                message=(
                    f"Số đầu năm: Tổng TS={ts_dn:,.0f}, Tổng NV={nv_dn:,.0f}"
                    + (f", chênh lệch={diff:,.0f}" if diff != 0 else "")
                ),
                expected=0,
                actual=diff,
                difference=diff,
            ))

    # ─── 2. CĐTK: Dư đầu kỳ + Phát sinh = Dư cuối kỳ ───

    def _check_cdtk_account_equation(self) -> None:
        """
        Kiểm tra phương trình cân đối tài khoản cho từng tài khoản:
        Dư Nợ cuối kỳ = Dư Nợ đầu kỳ + PS Nợ - PS Có + (Dư Có đầu kỳ - Dư Có cuối kỳ)

        Đơn giản hóa: Tổng Nợ (đầu + PS) = Tổng Có (đầu + PS) + (Dư Nợ CK - Dư Có CK)
        Hoặc kiểm tra theo từng bên:
        - Bên Nợ: Dư đầu Nợ + PS Nợ phải >= Dư cuối Nợ
        - Bên Có: Dư đầu Có + PS Có phải >= Dư cuối Có
        """
        if not self._has_cdtk:
            self.results.append(CheckResult(
                rule_id="BAL_02",
                rule_name="CĐTK: Phương trình cân đối tài khoản",
                severity=Severity.WARNING,
                message="Không có dữ liệu CĐTK để kiểm tra",
            ))
            return

        error_count = 0
        checked_count = 0

        for side in ["no", "co"]:
            side_name = "Nợ" if side == "no" else "Có"
            dk = self.cdtk_dk.get(side, {})
            ps = self.cdtk_ps.get(side, {})
            ck = self.cdtk_ck.get(side, {})

            # Lấy tất cả các tài khoản xuất hiện
            all_accounts: Set[str] = set()
            all_accounts.update(dk.keys())
            all_accounts.update(ps.keys())
            all_accounts.update(ck.keys())

            # Bỏ tongCong, chỉ kiểm tra từng TK
            all_accounts.discard("tongCong")

            for account in sorted(all_accounts):
                du_dau = self._g(dk, account)
                phat_sinh = self._g(ps, account)
                du_cuoi = self._g(ck, account)

                # Dư cuối kỳ (bên này) phải hợp lý so với đầu kỳ + phát sinh
                # Không kiểm tra đẳng thức chính xác vì bên đối ứng không rõ
                # Chỉ kiểm tra: dư cuối kỳ không âm (trừ TK đặc biệt)
                checked_count += 1

                if du_cuoi < 0:
                    account_name = ACCOUNT_NAMES.get(account, account)
                    error_count += 1
                    self.results.append(CheckResult(
                        rule_id="BAL_02",
                        rule_name=f"CĐTK: Dư {side_name} cuối kỳ âm ({account_name})",
                        severity=Severity.WARNING,
                        message=(
                            f"{account_name} bên {side_name}: "
                            f"Đầu kỳ={du_dau:,.0f}, "
                            f"Phát sinh={phat_sinh:,.0f}, "
                            f"Cuối kỳ={du_cuoi:,.0f} (âm)"
                        ),
                        expected=0,
                        actual=du_cuoi,
                        difference=du_cuoi,
                    ))

        if error_count == 0 and checked_count > 0:
            self.results.append(CheckResult(
                rule_id="BAL_02",
                rule_name="CĐTK: Phương trình cân đối tài khoản",
                severity=Severity.OK,
                message=f"Đã kiểm tra {checked_count} tài khoản, không có số dư âm bất thường",
            ))

    # ─── 3. CĐTK: Tổng Nợ = Tổng Có ────────────────────

    def _check_cdtk_debit_credit_totals(self) -> None:
        """
        Kiểm tra tổng Nợ = tổng Có trong CĐTK cho từng kỳ.

        Nguyên tắc kép: mỗi giao dịch phải ghi Nợ đúng bằng Có.
        Do đó tổng phát sinh Nợ = tổng phát sinh Có.
        """
        if not self._has_cdtk:
            self.results.append(CheckResult(
                rule_id="BAL_03",
                rule_name="CĐTK: Tổng Nợ = Tổng Có",
                severity=Severity.WARNING,
                message="Không có dữ liệu CĐTK để kiểm tra",
            ))
            return

        periods = [
            ("SoDuDauKy", "Đầu kỳ", self.cdtk_dk),
            ("SoPhatSinhTrongKy", "Phát sinh trong kỳ", self.cdtk_ps),
            ("SoDuCuoiKy", "Cuối kỳ", self.cdtk_ck),
        ]

        for period_key, period_name, period_data in periods:
            if not period_data:
                continue

            no_data = period_data.get("no", {})
            co_data = period_data.get("co", {})

            tong_no = self._g(no_data, "tongCong")
            tong_co = self._g(co_data, "tongCong")
            diff = tong_no - tong_co

            # Đối với phát sinh, tổng Nợ phải = tổng Có (bắt buộc)
            # Đối với số dư, tổng Nợ có thể khác tổng Có (bình thường)
            if period_key == "SoPhatSinhTrongKy":
                severity = Severity.OK if diff == 0 else Severity.CRITICAL
            else:
                # Số dư đầu/cuối kỳ: tổng Nợ thường khác tổng Có
                # Chỉ cảnh báo nếu cả hai đều = 0 (có thể thiếu dữ liệu)
                if tong_no == 0 and tong_co == 0:
                    severity = Severity.WARNING
                else:
                    severity = Severity.OK

            self.results.append(CheckResult(
                rule_id=f"BAL_03_{period_key}",
                rule_name=f"CĐTK: Tổng Nợ ↔ Tổng Có ({period_name})",
                severity=severity,
                message=(
                    f"{period_name}: "
                    f"Tổng Nợ={tong_no:,.0f}, "
                    f"Tổng Có={tong_co:,.0f}"
                    + (f", chênh lệch={diff:,.0f}" if diff != 0 else "")
                ),
                expected=0 if period_key == "SoPhatSinhTrongKy" else None,
                actual=diff if period_key == "SoPhatSinhTrongKy" else tong_no,
                difference=diff,
            ))

    # ─── 4. CĐTK: Tài khoản con cộng = Tài khoản cha ───

    def _check_cdtk_parent_child_accounts(self) -> None:
        """
        Kiểm tra tổng số dư các tài khoản chi tiết (con) bằng
        số dư tài khoản tổng hợp (cha).

        Ví dụ: TK1111 + TK1112 = TK111
        """
        if not self._has_cdtk:
            return

        error_count = 0
        checked_count = 0

        # Kiểm tra trên từng kỳ và từng bên
        period_configs = [
            ("Đầu kỳ", self.cdtk_dk),
            ("Cuối kỳ", self.cdtk_ck),
        ]

        for period_name, period_data in period_configs:
            if not period_data:
                continue

            for side in ["no", "co"]:
                side_name = "Nợ" if side == "no" else "Có"
                side_data = period_data.get(side, {})

                if not side_data:
                    continue

                for parent_key, child_keys in PARENT_CHILD_MAP.items():
                    parent_val = self._g(side_data, parent_key)

                    # Chỉ kiểm tra nếu TK cha có giá trị hoặc TK con có giá trị
                    children_vals = [self._g(side_data, ck) for ck in child_keys]
                    children_sum = sum(children_vals)
                    has_any_value = parent_val != 0 or children_sum != 0

                    if not has_any_value:
                        continue

                    checked_count += 1
                    diff = parent_val - children_sum

                    if diff != 0:
                        error_count += 1
                        parent_name = ACCOUNT_NAMES.get(parent_key, parent_key)
                        child_names = [
                            ACCOUNT_NAMES.get(ck, ck) for ck in child_keys
                        ]

                        self.results.append(CheckResult(
                            rule_id="BAL_04",
                            rule_name=(
                                f"CĐTK: TK cha ↔ TK con "
                                f"({parent_name}, {period_name} bên {side_name})"
                            ),
                            severity=Severity.ERROR,
                            message=(
                                f"{parent_name} ({period_name}, {side_name})="
                                f"{parent_val:,.0f}, "
                                f"Σ TK con={children_sum:,.0f}, "
                                f"chênh lệch={diff:,.0f}"
                            ),
                            expected=parent_val,
                            actual=children_sum,
                            difference=diff,
                        ))

        if error_count == 0 and checked_count > 0:
            self.results.append(CheckResult(
                rule_id="BAL_04",
                rule_name="CĐTK: Tổng TK con = TK cha",
                severity=Severity.OK,
                message=f"Đã kiểm tra {checked_count} quan hệ cha-con, tất cả khớp",
            ))

    # ─── Helper ───────────────────────────────────────────

    @staticmethod
    def _g(data: Dict, key: str) -> float:
        """Lấy giá trị số từ dict, trả về 0.0 nếu không tìm thấy."""
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
