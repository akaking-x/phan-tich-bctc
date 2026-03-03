"""
Validator Module — Kiểm tra tính hợp lệ và đối chiếu chéo BCTC.

Module cung cấp:
- CrossChecker: Đối chiếu chéo giữa 4 báo cáo (CĐKT, KQHĐKD, LCTT, CĐTK)
- BalanceChecker: Kiểm tra cân đối nội bộ bổ sung
- RuleSet: Catalog toàn bộ quy tắc kiểm tra
- Severity, CheckResult: Các class hỗ trợ

Sử dụng:
    from backend.validator import CrossChecker, BalanceChecker, RuleSet

    # Đối chiếu chéo
    checker = CrossChecker(parsed_data)
    results = checker.run_all()

    # Kiểm tra cân đối
    balance = BalanceChecker(parsed_data)
    balance_results = balance.run_all()

    # Tra cứu quy tắc
    ruleset = RuleSet()
    rule = ruleset.get("CDKT_01")
"""

from .cross_check import CrossChecker, CheckResult, Severity
from .balance_check import BalanceChecker
from .rules import (
    RuleSet,
    Rule,
    RuleCategory,
    SeverityDefault,
    DEFAULT_RULESET,
    get_rule,
    get_all_rules,
    get_rules_by_category,
    get_rules_by_report,
)

__all__ = [
    # Core classes
    "CrossChecker",
    "BalanceChecker",
    "CheckResult",
    "Severity",
    # Rule system
    "RuleSet",
    "Rule",
    "RuleCategory",
    "SeverityDefault",
    "DEFAULT_RULESET",
    # Convenience functions
    "get_rule",
    "get_all_rules",
    "get_rules_by_category",
    "get_rules_by_report",
]
