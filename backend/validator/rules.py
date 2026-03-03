"""
Bộ quy tắc kiểm tra (Rule Definitions) cho Validator module.

Mỗi rule có:
- id: Mã định danh duy nhất
- name: Tên quy tắc (tiếng Việt)
- description: Mô tả chi tiết (tiếng Việt)
- severity_default: Mức độ nghiêm trọng mặc định
- category: Phân loại quy tắc
- applicable_reports: Các báo cáo liên quan
- applicable_circulars: Áp dụng cho TT133, TT200, hoặc cả hai
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class RuleCategory(str, Enum):
    """Phân loại quy tắc kiểm tra."""
    INTERNAL_CONSISTENCY = "internal_consistency"    # Nhất quán nội bộ
    CROSS_REPORT = "cross_report"                    # Đối chiếu chéo
    ACCOUNTING_EQUATION = "accounting_equation"      # Phương trình kế toán


class SeverityDefault(str, Enum):
    """Mức độ nghiêm trọng mặc định."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Rule:
    """Định nghĩa một quy tắc kiểm tra."""
    id: str
    name: str
    description: str
    severity_default: SeverityDefault
    category: RuleCategory
    applicable_reports: List[str]
    applicable_circulars: List[str] = field(default_factory=lambda: ["TT133", "TT200"])
    formula: Optional[str] = None
    notes: Optional[str] = None


class RuleSet:
    """
    Catalog toàn bộ quy tắc kiểm tra.

    Sử dụng:
        ruleset = RuleSet()
        rule = ruleset.get("CDKT_01")
        cdkt_rules = ruleset.by_report("CDKT")
        cross_rules = ruleset.by_category(RuleCategory.CROSS_REPORT)
    """

    def __init__(self) -> None:
        self._rules: Dict[str, Rule] = {}
        self._build_rules()

    def _build_rules(self) -> None:
        """Khởi tạo toàn bộ bộ quy tắc."""
        all_rules = (
            self._cdkt_rules()
            + self._kqhdkd_rules()
            + self._lctt_rules()
            + self._cdtk_rules()
            + self._cross_report_rules()
            + self._classification_rules()
            + self._balance_rules()
        )
        for rule in all_rules:
            self._rules[rule.id] = rule

    # ═══════════════════════════════════════════════════════
    #  Truy xuất quy tắc
    # ═══════════════════════════════════════════════════════

    def get(self, rule_id: str) -> Optional[Rule]:
        """Lấy quy tắc theo mã ID."""
        return self._rules.get(rule_id)

    def all_rules(self) -> List[Rule]:
        """Trả về toàn bộ danh sách quy tắc."""
        return list(self._rules.values())

    def by_category(self, category: RuleCategory) -> List[Rule]:
        """Lọc quy tắc theo phân loại."""
        return [r for r in self._rules.values() if r.category == category]

    def by_report(self, report: str) -> List[Rule]:
        """Lọc quy tắc theo báo cáo áp dụng (CDKT, KQHDKD, LCTT, CDTK)."""
        return [
            r for r in self._rules.values()
            if report in r.applicable_reports
        ]

    def by_circular(self, circular: str) -> List[Rule]:
        """Lọc quy tắc theo thông tư (TT133, TT200)."""
        return [
            r for r in self._rules.values()
            if circular in r.applicable_circulars
        ]

    def by_severity(self, severity: SeverityDefault) -> List[Rule]:
        """Lọc quy tắc theo mức độ nghiêm trọng mặc định."""
        return [
            r for r in self._rules.values()
            if r.severity_default == severity
        ]

    @property
    def count(self) -> int:
        """Tổng số quy tắc."""
        return len(self._rules)

    def summary(self) -> Dict[str, int]:
        """Thống kê số lượng quy tắc theo phân loại."""
        result: Dict[str, int] = {}
        for cat in RuleCategory:
            result[cat.value] = len(self.by_category(cat))
        return result

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — CĐKT
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _cdkt_rules() -> List[Rule]:
        return [
            Rule(
                id="CDKT_01",
                name="Tổng Tài sản = Tổng Nguồn vốn",
                description=(
                    "Kiểm tra phương trình kế toán cơ bản: "
                    "ct300 (Tổng cộng Tài sản) phải bằng ct600 (Tổng cộng Nguồn vốn). "
                    "Đây là nguyên tắc nền tảng, nếu vi phạm thì BCTC có sai sót nghiêm trọng."
                ),
                severity_default=SeverityDefault.CRITICAL,
                category=RuleCategory.ACCOUNTING_EQUATION,
                applicable_reports=["CDKT"],
                formula="ct300 = ct600",
            ),
            Rule(
                id="CDKT_02",
                name="CĐKT: Tổng TS ngắn hạn",
                description=(
                    "Kiểm tra ct100 (TSNH) = ct110 + ct120 + ct130 + ct140 + ct150. "
                    "Tổng các chỉ tiêu con phải bằng chỉ tiêu tổng hợp cha."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                formula="ct100 = ct110 + ct120 + ct130 + ct140 + ct150",
            ),
            Rule(
                id="CDKT_03",
                name="CĐKT: Tổng TS dài hạn",
                description=(
                    "Kiểm tra ct200 (TSDH) = ct210 + ct220 + ct230 + ct240 + ct250 + ct260. "
                    "Tổng các chỉ tiêu con phải bằng chỉ tiêu tổng hợp cha."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                formula="ct200 = ct210 + ct220 + ct230 + ct240 + ct250 + ct260",
            ),
            Rule(
                id="CDKT_04",
                name="CĐKT: Tổng TS = TSNH + TSDH",
                description=(
                    "Kiểm tra ct300 = ct100 + ct200. "
                    "Tổng cộng tài sản phải bằng tài sản ngắn hạn cộng tài sản dài hạn."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                formula="ct300 = ct100 + ct200",
            ),
            Rule(
                id="CDKT_05",
                name="CĐKT: Nợ phải trả",
                description=(
                    "Kiểm tra ct400 (Nợ phải trả) = ct410 (Nợ NH) + ct420 (Nợ DH). "
                    "Tổng nợ phải trả phải bằng nợ ngắn hạn cộng nợ dài hạn."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                formula="ct400 = ct410 + ct420",
            ),
            Rule(
                id="CDKT_06",
                name="CĐKT: Vốn chủ sở hữu",
                description=(
                    "Kiểm tra ct500 (VCSH) = ct511 + ct512 + ct513 + ct514 + ct515 + ct516 + ct517. "
                    "Tổng vốn chủ sở hữu phải bằng tổng các thành phần."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                formula="ct500 = ct511 + ct512 + ct513 + ct514 + ct515 + ct516 + ct517",
                notes=(
                    "TT200 có thể có thêm chỉ tiêu con: ct518 (Lợi ích cổ đông không kiểm soát). "
                    "Công thức sẽ điều chỉnh tùy thông tư."
                ),
            ),
            Rule(
                id="CDKT_07",
                name="CĐKT: Tổng NV = Nợ + VCSH",
                description=(
                    "Kiểm tra ct600 = ct400 + ct500. "
                    "Tổng nguồn vốn phải bằng nợ phải trả cộng vốn chủ sở hữu."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                formula="ct600 = ct400 + ct500",
            ),
        ]

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — KQHĐKD
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _kqhdkd_rules() -> List[Rule]:
        return [
            Rule(
                id="KQHDKD_01",
                name="KQHĐKD: DT thuần = DT - Giảm trừ",
                description=(
                    "Kiểm tra ct10 = ct01 - ct02. "
                    "Doanh thu thuần bằng doanh thu bán hàng trừ các khoản giảm trừ doanh thu."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["KQHDKD"],
                formula="ct10 = ct01 - ct02",
            ),
            Rule(
                id="KQHDKD_02",
                name="KQHĐKD: LN gộp = DT thuần - Giá vốn",
                description=(
                    "Kiểm tra ct20 = ct10 - ct11. "
                    "Lợi nhuận gộp bằng doanh thu thuần trừ giá vốn hàng bán."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["KQHDKD"],
                formula="ct20 = ct10 - ct11",
            ),
            Rule(
                id="KQHDKD_03",
                name="KQHĐKD: LN thuần từ HĐKD",
                description=(
                    "Kiểm tra ct30 = ct20 + ct21 - ct22 - ct23 - ct24. "
                    "Lợi nhuận thuần từ HĐKD = LN gộp + DT tài chính "
                    "- CP tài chính - CP bán hàng - CP QLDN."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["KQHDKD"],
                formula="ct30 = ct20 + ct21 - ct22 - ct23 - ct24",
                notes=(
                    "TT200 tách riêng ct25 (lãi/lỗ từ công ty liên kết). "
                    "Công thức TT200: ct30 = ct20 + ct21 - ct22 + ct24 - ct25 - ct26."
                ),
            ),
            Rule(
                id="KQHDKD_04",
                name="KQHĐKD: LN khác",
                description=(
                    "Kiểm tra ct40 = ct31 - ct32. "
                    "Lợi nhuận khác = Thu nhập khác - Chi phí khác."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["KQHDKD"],
                formula="ct40 = ct31 - ct32",
            ),
            Rule(
                id="KQHDKD_05",
                name="KQHĐKD: Tổng LN trước thuế",
                description=(
                    "Kiểm tra ct50 = ct30 + ct40. "
                    "Tổng lợi nhuận trước thuế = LN thuần HĐKD + LN khác."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["KQHDKD"],
                formula="ct50 = ct30 + ct40",
            ),
            Rule(
                id="KQHDKD_06",
                name="KQHĐKD: LN sau thuế",
                description=(
                    "Kiểm tra ct60 = ct50 - ct51. "
                    "Lợi nhuận sau thuế = LN trước thuế - Chi phí thuế TNDN."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["KQHDKD"],
                formula="ct60 = ct50 - ct51",
                notes=(
                    "TT200 tách ct51 thành ct51a (thuế TNDN hiện hành) "
                    "và ct51b (thuế TNDN hoãn lại)."
                ),
            ),
        ]

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — LCTT
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _lctt_rules() -> List[Rule]:
        return [
            Rule(
                id="LCTT_01",
                name="LCTT: Lưu chuyển tiền thuần từ HĐKD",
                description=(
                    "Kiểm tra ct20 = ct01 + ct02 + ct03 + ct04 + ct05 + ct06 + ct07. "
                    "Lưu chuyển tiền thuần từ hoạt động kinh doanh phải bằng "
                    "tổng các dòng tiền thu/chi HĐKD. "
                    "Lưu ý: ct02-ct07 thường là số âm (tiền chi ra)."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["LCTT"],
                formula="ct20 = Σ(ct01..ct07)",
            ),
            Rule(
                id="LCTT_02",
                name="LCTT: Lưu chuyển tiền thuần từ HĐ đầu tư",
                description=(
                    "Kiểm tra ct30 = ct21 + ct22 + ct23 + ct24 + ct25. "
                    "Lưu chuyển tiền thuần từ hoạt động đầu tư phải bằng "
                    "tổng các dòng tiền thu/chi đầu tư."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["LCTT"],
                formula="ct30 = Σ(ct21..ct25)",
            ),
            Rule(
                id="LCTT_03",
                name="LCTT: Lưu chuyển tiền thuần từ HĐ tài chính",
                description=(
                    "Kiểm tra ct40 = ct31 + ct32 + ct33 + ct34 + ct35. "
                    "Lưu chuyển tiền thuần từ hoạt động tài chính phải bằng "
                    "tổng các dòng tiền thu/chi tài chính."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["LCTT"],
                formula="ct40 = Σ(ct31..ct35)",
            ),
            Rule(
                id="LCTT_04",
                name="LCTT: Tăng giảm tiền thuần trong kỳ",
                description=(
                    "Kiểm tra ct50 = ct20 + ct30 + ct40. "
                    "Tăng giảm tiền thuần = HĐKD + HĐĐT + HĐTC."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["LCTT"],
                formula="ct50 = ct20 + ct30 + ct40",
            ),
            Rule(
                id="LCTT_05",
                name="LCTT: Tiền cuối kỳ",
                description=(
                    "Kiểm tra ct70 = ct50 + ct60 + ct61. "
                    "Tiền cuối kỳ = Tăng giảm thuần + Tiền đầu kỳ + Ảnh hưởng tỷ giá."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["LCTT"],
                formula="ct70 = ct50 + ct60 + ct61",
            ),
        ]

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — CĐTK
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _cdtk_rules() -> List[Rule]:
        return [
            Rule(
                id="CDTK_NO_01",
                name="CĐTK bên Nợ: Tổng cộng hợp lệ",
                description=(
                    "Kiểm tra tổng cộng bên Nợ trên bảng CĐTK có hợp lệ. "
                    "Tổng cộng cuối kỳ bên Nợ phải >= 0."
                ),
                severity_default=SeverityDefault.WARNING,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDTK"],
            ),
            Rule(
                id="CDTK_CO_01",
                name="CĐTK bên Có: Tổng cộng hợp lệ",
                description=(
                    "Kiểm tra tổng cộng bên Có trên bảng CĐTK có hợp lệ. "
                    "Tổng cộng cuối kỳ bên Có phải >= 0."
                ),
                severity_default=SeverityDefault.WARNING,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDTK"],
            ),
        ]

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — Đối chiếu chéo
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _cross_report_rules() -> List[Rule]:
        return [
            Rule(
                id="CROSS_01",
                name="CĐKT.ct517 = CĐKT.ct517(đầu) + KQHĐKD.ct60",
                description=(
                    "Đối chiếu LNST chưa phân phối trên CĐKT với KQHĐKD. "
                    "Số cuối kỳ ct517 = Số đầu kỳ ct517 + LNST năm nay (ct60). "
                    "Giả định DN không chia cổ tức / trích quỹ trong kỳ. "
                    "Nếu có chia cổ tức, chênh lệch sẽ bằng khoản đã chia."
                ),
                severity_default=SeverityDefault.CRITICAL,
                category=RuleCategory.CROSS_REPORT,
                applicable_reports=["CDKT", "KQHDKD"],
                formula="CĐKT.ct517(cuối) = CĐKT.ct517(đầu) + KQHĐKD.ct60",
                notes=(
                    "Nếu DN có chia cổ tức hoặc trích quỹ, chênh lệch "
                    "sẽ bằng số đã chia/trích. Cần kiểm tra thêm TK4211, TK4212 "
                    "trên CĐTK để xác nhận."
                ),
            ),
            Rule(
                id="CROSS_02",
                name="LCTT.ct70 = CĐKT.ct110 (tiền cuối kỳ)",
                description=(
                    "Đối chiếu tiền cuối kỳ trên LCTT với CĐKT. "
                    "ct70 trên LCTT phải bằng ct110 (Tiền và tương đương tiền) "
                    "trên CĐKT cuối năm."
                ),
                severity_default=SeverityDefault.CRITICAL,
                category=RuleCategory.CROSS_REPORT,
                applicable_reports=["CDKT", "LCTT"],
                formula="LCTT.ct70 = CĐKT.ct110",
            ),
            Rule(
                id="CROSS_03",
                name="LCTT.ct60 = CĐKT_đầu.ct110 (tiền đầu kỳ)",
                description=(
                    "Đối chiếu tiền đầu kỳ trên LCTT với CĐKT. "
                    "ct60 trên LCTT phải bằng ct110 (Tiền và tương đương tiền) "
                    "trên CĐKT đầu năm."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.CROSS_REPORT,
                applicable_reports=["CDKT", "LCTT"],
                formula="LCTT.ct60 = CĐKT_đầu.ct110",
            ),
            Rule(
                id="CROSS_04",
                name="CĐTK(TK111+112) = CĐKT.ct110",
                description=(
                    "Đối chiếu số dư tiền trên CĐTK với CĐKT. "
                    "TK111 (Tiền mặt) + TK112 (TGNH) cuối kỳ trên CĐTK "
                    "phải bằng ct110 trên CĐKT."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.CROSS_REPORT,
                applicable_reports=["CDKT", "CDTK"],
                formula="CĐTK.TK111 + CĐTK.TK112 = CĐKT.ct110",
            ),
            Rule(
                id="CROSS_05",
                name="CĐTK: Tổng Nợ = Tổng Có (cuối kỳ)",
                description=(
                    "Kiểm tra tổng dư Nợ cuối kỳ = tổng dư Có cuối kỳ trên CĐTK. "
                    "Đây là nguyên tắc ghi sổ kép cơ bản."
                ),
                severity_default=SeverityDefault.CRITICAL,
                category=RuleCategory.ACCOUNTING_EQUATION,
                applicable_reports=["CDTK"],
                formula="CĐTK.TổngNợ = CĐTK.TổngCó",
            ),
        ]

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — Phân loại dòng tiền
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _classification_rules() -> List[Rule]:
        return [
            Rule(
                id="CLASS_01",
                name="LCTT: ct04 (lãi vay) nhưng không có dư nợ vay",
                description=(
                    "Cảnh báo khi LCTT ghi tiền chi trả lãi vay (ct04) "
                    "nhưng trên CĐTK không có dư nợ TK341 (Vay và nợ thuê TC). "
                    "Có thể DN ghi phí ngân hàng nhầm vào ct04, "
                    "đáng lẽ phải ghi vào ct07 (tiền chi khác cho HĐKD)."
                ),
                severity_default=SeverityDefault.WARNING,
                category=RuleCategory.CROSS_REPORT,
                applicable_reports=["LCTT", "CDTK", "KQHDKD"],
                notes=(
                    "Phí dịch vụ ngân hàng (phí chuyển tiền, phí duy trì TK) "
                    "không phải lãi vay. Cần phân loại đúng để LCTT chính xác."
                ),
            ),
        ]

    # ═══════════════════════════════════════════════════════
    #  Định nghĩa quy tắc — Cân đối bổ sung (BalanceChecker)
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _balance_rules() -> List[Rule]:
        return [
            Rule(
                id="BAL_01",
                name="CĐKT: Số đầu năm = Số cuối năm trước",
                description=(
                    "Kiểm tra tính liên tục giữa các kỳ: "
                    "Số dư đầu năm hiện tại phải bằng số dư cuối năm trước "
                    "cho tất cả các chỉ tiêu trên CĐKT. "
                    "Vi phạm có thể do điều chỉnh hồi tố, thay đổi chính sách kế toán, "
                    "hoặc sai sót."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDKT"],
                notes=(
                    "Cần dữ liệu BCTC năm trước để thực hiện kiểm tra này. "
                    "Nếu không có, chỉ kiểm tra cân đối nội bộ số đầu năm."
                ),
            ),
            Rule(
                id="BAL_02",
                name="CĐTK: Phương trình cân đối tài khoản",
                description=(
                    "Kiểm tra từng tài khoản trên CĐTK: "
                    "số dư cuối kỳ phải hợp lý so với đầu kỳ và phát sinh. "
                    "Cụ thể, số dư cuối kỳ không được âm (trừ TK đặc biệt)."
                ),
                severity_default=SeverityDefault.WARNING,
                category=RuleCategory.ACCOUNTING_EQUATION,
                applicable_reports=["CDTK"],
            ),
            Rule(
                id="BAL_03",
                name="CĐTK: Tổng phát sinh Nợ = Tổng phát sinh Có",
                description=(
                    "Kiểm tra nguyên tắc ghi sổ kép: "
                    "tổng phát sinh Nợ trong kỳ phải bằng tổng phát sinh Có trong kỳ. "
                    "Áp dụng cho cột phát sinh. "
                    "Cột số dư có thể khác nhau giữa Nợ và Có."
                ),
                severity_default=SeverityDefault.CRITICAL,
                category=RuleCategory.ACCOUNTING_EQUATION,
                applicable_reports=["CDTK"],
                formula="CĐTK.TổngPSNợ = CĐTK.TổngPSCó",
            ),
            Rule(
                id="BAL_04",
                name="CĐTK: Tổng TK con = TK cha",
                description=(
                    "Kiểm tra quan hệ tổng hợp - chi tiết trên CĐTK: "
                    "số dư các tài khoản chi tiết (con) phải cộng lại bằng "
                    "số dư tài khoản tổng hợp (cha). "
                    "Ví dụ: TK1111 + TK1112 = TK111."
                ),
                severity_default=SeverityDefault.ERROR,
                category=RuleCategory.INTERNAL_CONSISTENCY,
                applicable_reports=["CDTK"],
                notes=(
                    "Một số DN không kê khai chi tiết TK con trên HTKK, "
                    "trong trường hợp đó chỉ cảnh báo nếu có TK con nhưng tổng không khớp."
                ),
            ),
        ]


# ═══════════════════════════════════════════════════════
#  Tiện ích tra cứu nhanh
# ═══════════════════════════════════════════════════════

# Singleton instance cho sử dụng nhanh
DEFAULT_RULESET = RuleSet()


def get_rule(rule_id: str) -> Optional[Rule]:
    """Tra cứu nhanh một quy tắc theo mã ID."""
    return DEFAULT_RULESET.get(rule_id)


def get_all_rules() -> List[Rule]:
    """Lấy toàn bộ danh sách quy tắc."""
    return DEFAULT_RULESET.all_rules()


def get_rules_by_category(category: RuleCategory) -> List[Rule]:
    """Lọc quy tắc theo phân loại."""
    return DEFAULT_RULESET.by_category(category)


def get_rules_by_report(report: str) -> List[Rule]:
    """Lọc quy tắc theo báo cáo."""
    return DEFAULT_RULESET.by_report(report)
