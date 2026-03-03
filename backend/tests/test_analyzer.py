"""
Tests cho module Analyzer.

Kiem tra:
- AnomalyDetector: Phat hien bat thuong
- RatioAnalyzer: Tinh chi so tai chinh
- JournalReconstructor: Tai tao but toan
"""

import os
import sys
import pytest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from analyzer.anomaly_detector import AnomalyDetector, Anomaly, RiskLevel
from analyzer.ratio_analyzer import RatioAnalyzer, FinancialRatio
from analyzer.journal_reconstructor import JournalReconstructor, JournalEntry
from parser.tt133_mapper import CDTK_ACCOUNT_MAP


# ─── Fixtures ────────────────────────────────────────────

@pytest.fixture
def normal_data():
    """Du lieu BCTC binh thuong."""
    return {
        "cdkt": {
            "so_cuoi_nam": {
                "ct100": 10000000000,
                "ct110": 2000000000,
                "ct120": 0,
                "ct130": 3000000000,
                "ct131": 2500000000,
                "ct133": 200000000,
                "ct140": 4000000000,
                "ct150": 1000000000,
                "ct151": 50000000,
                "ct200": 5000000000,
                "ct300": 15000000000,
                "ct400": 7000000000,
                "ct410": 6000000000,
                "ct416": 100000000,
                "ct500": 8000000000,
                "ct511": 5000000000,
                "ct517": 2500000000,
                "ct600": 15000000000,
            },
            "so_dau_nam": {
                "ct300": 12000000000,
                "ct500": 7000000000,
                "ct511": 5000000000,
                "ct517": 1500000000,
            },
        },
        "kqhdkd": {
            "nam_nay": {
                "ct01": 20000000000,
                "ct02": 0,
                "ct10": 20000000000,
                "ct11": 14000000000,
                "ct20": 6000000000,
                "ct21": 100000000,
                "ct22": 200000000,
                "ct23": 1000000000,
                "ct24": 2000000000,
                "ct30": 2900000000,
                "ct31": 200000000,
                "ct32": 100000000,
                "ct40": 100000000,
                "ct50": 3000000000,
                "ct51": 600000000,
                "ct60": 2400000000,
            },
        },
        "lctt": {
            "nam_nay": {
                "ct01": 18000000000,
                "ct20": 3000000000,
                "ct30": -1300000000,
                "ct40": 500000000,
            },
        },
        "cdtk": {
            "SoDuCuoiKy": {
                "no": {
                    "ct111": 1000000000,
                    "ct112": 2000000000,
                },
                "co": {},
            },
        },
    }


@pytest.fixture
def cash_heavy_data():
    """Du lieu DN co tien mat ton quy lon (> 50% tong TS)."""
    return {
        "cdkt": {
            "so_cuoi_nam": {
                "ct100": 10000000000,
                "ct110": 8000000000,
                "ct130": 0,
                "ct133": 0,
                "ct140": 0,
                "ct150": 0,
                "ct151": 0,
                "ct200": 2000000000,
                "ct300": 12000000000,
                "ct400": 2000000000,
                "ct410": 2000000000,
                "ct416": 0,
                "ct500": 10000000000,
                "ct511": 10000000000,
                "ct517": 0,
                "ct600": 12000000000,
            },
            "so_dau_nam": {"ct300": 10000000000, "ct500": 10000000000, "ct511": 10000000000},
        },
        "kqhdkd": {
            "nam_nay": {
                "ct01": 5000000000,
                "ct10": 5000000000,
                "ct11": 3000000000,
                "ct20": 2000000000,
                "ct21": 0, "ct22": 0, "ct23": 0,
                "ct24": 500000000,
                "ct30": 1500000000,
                "ct50": 1500000000,
                "ct60": 1200000000,
            },
        },
        "lctt": {
            "nam_nay": {"ct01": 5000000000, "ct20": 3000000000},
        },
        "cdtk": {
            "SoDuCuoiKy": {
                "no": {"ct111": 7000000000, "ct112": 1000000000},
                "co": {},
            },
        },
    }


@pytest.fixture
def negative_equity_data():
    """Du lieu DN co VCSH am."""
    return {
        "cdkt": {
            "so_cuoi_nam": {
                "ct100": 5000000000,
                "ct110": 1000000000,
                "ct130": 0,
                "ct133": 0,
                "ct140": 0,
                "ct150": 0,
                "ct151": 0,
                "ct200": 3000000000,
                "ct300": 8000000000,
                "ct400": 10000000000,
                "ct410": 10000000000,
                "ct416": 0,
                "ct500": -2000000000,  # VCSH am
                "ct511": 5000000000,
                "ct517": -7000000000,  # Lo luy ke lon
                "ct600": 8000000000,
            },
            "so_dau_nam": {"ct300": 6000000000, "ct500": 1000000000, "ct511": 5000000000},
        },
        "kqhdkd": {
            "nam_nay": {
                "ct01": 1000000000,
                "ct10": 1000000000,
                "ct11": 2000000000,
                "ct20": -1000000000,
                "ct21": 0, "ct22": 0, "ct23": 0,
                "ct24": 2000000000,
                "ct30": -3000000000,
                "ct50": -3000000000,
                "ct60": -3000000000,
            },
        },
        "lctt": {
            "nam_nay": {"ct01": 500000000, "ct20": -1000000000},
        },
        "cdtk": {
            "SoDuCuoiKy": {
                "no": {"ct111": 200000000, "ct112": 800000000},
                "co": {},
            },
        },
    }


@pytest.fixture
def dormant_data():
    """Du lieu DN von lon nhung chua hoat dong."""
    return {
        "cdkt": {
            "so_cuoi_nam": {
                "ct100": 5000000000,
                "ct110": 5000000000,
                "ct130": 0,
                "ct133": 0,
                "ct140": 0,
                "ct150": 0,
                "ct151": 0,
                "ct200": 0,
                "ct300": 5000000000,
                "ct400": 0,
                "ct410": 0,
                "ct416": 0,
                "ct500": 5000000000,
                "ct511": 5000000000,
                "ct517": 0,
                "ct600": 5000000000,
            },
            "so_dau_nam": {"ct300": 5000000000, "ct500": 5000000000, "ct511": 5000000000},
        },
        "kqhdkd": {
            "nam_nay": {
                "ct01": 0,         # Khong co DT
                "ct10": 0,
                "ct11": 0,
                "ct20": 0,
                "ct21": 0, "ct22": 0, "ct23": 0,
                "ct24": 10000000,  # Chi nho
                "ct30": -10000000,
                "ct50": -10000000,
                "ct60": -10000000,
            },
        },
        "lctt": {
            "nam_nay": {"ct01": 0, "ct20": -10000000},
        },
        "cdtk": {
            "SoDuCuoiKy": {
                "no": {"ct111": 100000000, "ct112": 4900000000},
                "co": {},
            },
        },
    }


@pytest.fixture
def journal_cdtk_data():
    """Du lieu CDTK cho test tai tao but toan."""
    return {
        "SoPhatSinhTrongKy": {
            "no": {
                "ct111": 5000000000,   # TK 111 - Tien mat
                "ct112": 15000000000,  # TK 112 - Tien gui NH
                "ct131": 20000000000,  # TK 131 - Phai thu KH
                "ct156": 14000000000,  # TK 156 - Hang hoa
                "ct632": 14000000000,  # TK 632 - Gia von
                "ct642": 3000000000,   # TK 642 - CP QLDN
                "ct511": 20000000000,  # TK 511 - KCH DT
                "ct911": 35000000000,  # TK 911 - XDKQKD
                "tongCong": 126000000000,
            },
            "co": {
                "ct111": 4500000000,
                "ct112": 14000000000,
                "ct131": 19500000000,
                "ct156": 13500000000,
                "ct331": 12500000000,  # TK 331 - NCC
                "ct511": 20000000000,  # TK 511 - DT
                "ct632": 14000000000,
                "ct642": 3000000000,
                "ct911": 35000000000,
                "ct421": 2400000000,   # TK 421 - LNST
                "tongCong": 138400000000,
            },
        },
    }


# ─── Test AnomalyDetector ───────────────────────────────

class TestAnomalyDetector:
    """Test phat hien bat thuong."""

    def test_no_anomalies_normal(self, normal_data):
        """Du lieu binh thuong -> it bat thuong."""
        detector = AnomalyDetector(normal_data)
        anomalies = detector.detect_all()
        # Co the co 1 so bat thuong nhe, nhung khong co CRITICAL
        critical = [a for a in anomalies if a.risk_level == RiskLevel.CRITICAL]
        assert len(critical) == 0

    def test_cash_heavy_detection(self, cash_heavy_data):
        """Tien mat > 50% tong TS -> CASH_01."""
        detector = AnomalyDetector(cash_heavy_data)
        anomalies = detector.detect_all()

        cash_anomaly = [a for a in anomalies if a.code == "CASH_01"]
        assert len(cash_anomaly) == 1
        assert cash_anomaly[0].risk_level == RiskLevel.HIGH
        assert cash_anomaly[0].category == "cash"

    def test_negative_equity(self, negative_equity_data):
        """VCSH am -> EQUITY_01 CRITICAL."""
        detector = AnomalyDetector(negative_equity_data)
        anomalies = detector.detect_all()

        equity_anomaly = [a for a in anomalies if a.code == "EQUITY_01"]
        assert len(equity_anomaly) == 1
        assert equity_anomaly[0].risk_level == RiskLevel.CRITICAL

    def test_loss_ratio(self, negative_equity_data):
        """Lo luy ke lon so voi von gop -> EQUITY_02."""
        detector = AnomalyDetector(negative_equity_data)
        anomalies = detector.detect_all()

        loss_anomaly = [a for a in anomalies if a.code == "EQUITY_02"]
        assert len(loss_anomaly) == 1
        assert loss_anomaly[0].risk_level == RiskLevel.HIGH

    def test_dormant_company(self, dormant_data):
        """Von lon, DT = 0 -> DORMANT_01."""
        detector = AnomalyDetector(dormant_data)
        anomalies = detector.detect_all()

        dormant = [a for a in anomalies if a.code == "DORMANT_01"]
        assert len(dormant) == 1
        assert dormant[0].risk_level == RiskLevel.MEDIUM

    def test_anomaly_structure(self, cash_heavy_data):
        """Moi anomaly co day du truong."""
        detector = AnomalyDetector(cash_heavy_data)
        anomalies = detector.detect_all()

        for a in anomalies:
            assert isinstance(a, Anomaly)
            assert a.code
            assert a.title
            assert a.description
            assert isinstance(a.risk_level, RiskLevel)
            assert a.category in ["cash", "tax", "structure", "activity"]
            assert a.suggestion

    def test_detect_all_returns_list(self, normal_data):
        """detect_all tra ve list."""
        detector = AnomalyDetector(normal_data)
        result = detector.detect_all()
        assert isinstance(result, list)

    def test_expense_over_revenue(self):
        """CP QLDN > DT -> EXP_01."""
        data = {
            "cdkt": {
                "so_cuoi_nam": {
                    "ct100": 1000000000, "ct110": 500000000,
                    "ct130": 0, "ct133": 0, "ct140": 0, "ct150": 0, "ct151": 0,
                    "ct200": 0, "ct300": 1000000000,
                    "ct400": 200000000, "ct410": 200000000, "ct416": 0,
                    "ct500": 800000000, "ct511": 1000000000, "ct517": -200000000,
                    "ct600": 1000000000,
                },
                "so_dau_nam": {"ct300": 1000000000, "ct500": 1000000000, "ct511": 1000000000},
            },
            "kqhdkd": {
                "nam_nay": {
                    "ct01": 100000000,  # DT = 100 trieu
                    "ct10": 100000000,
                    "ct11": 50000000,
                    "ct20": 50000000,
                    "ct21": 0, "ct22": 0, "ct23": 0,
                    "ct24": 200000000,  # CP QLDN = 200 trieu > DT
                    "ct30": -150000000,
                    "ct50": -150000000,
                    "ct60": -150000000,
                },
            },
            "lctt": {"nam_nay": {"ct01": 80000000, "ct20": 50000000}},
            "cdtk": {"SoDuCuoiKy": {"no": {"ct111": 100000000}, "co": {}}},
        }
        detector = AnomalyDetector(data)
        anomalies = detector.detect_all()
        exp = [a for a in anomalies if a.code == "EXP_01"]
        assert len(exp) == 1


# ─── Test RatioAnalyzer ─────────────────────────────────

class TestRatioAnalyzer:
    """Test tinh chi so tai chinh."""

    def test_analyze_returns_list(self, normal_data):
        """analyze tra ve list."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()
        assert isinstance(ratios, list)
        assert len(ratios) > 0

    def test_ratio_structure(self, normal_data):
        """Moi ratio co day du truong."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        for r in ratios:
            assert isinstance(r, FinancialRatio)
            assert r.code
            assert r.name
            assert r.name_en
            assert r.unit
            assert r.category in ["liquidity", "profitability", "leverage", "efficiency"]

    def test_current_ratio(self, normal_data):
        """He so thanh toan ngan han = TSNH / NNH."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        cr = next(r for r in ratios if r.code == "LIQ_01")
        # TSNH = 10ty, NNH = 6ty -> CR = 10/6 = 1.667
        expected = 10000000000 / 6000000000
        assert cr.value is not None
        assert abs(cr.value - expected) < 0.001

    def test_quick_ratio(self, normal_data):
        """He so thanh toan nhanh = (TSNH - HTK) / NNH."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        qr = next(r for r in ratios if r.code == "LIQ_02")
        # (10ty - 4ty) / 6ty = 1.0
        expected = (10000000000 - 4000000000) / 6000000000
        assert qr.value is not None
        assert abs(qr.value - expected) < 0.001

    def test_gross_margin(self, normal_data):
        """Bien LN gop = LN gop / DT thuan * 100."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        gm = next(r for r in ratios if r.code == "PROF_01")
        # LN gop = 6ty, DT thuan = 20ty -> GM = 30%
        expected = 6000000000 / 20000000000 * 100
        assert gm.value is not None
        assert abs(gm.value - expected) < 0.01

    def test_net_margin(self, normal_data):
        """Bien LN rong = LNST / DT thuan * 100."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        nm = next(r for r in ratios if r.code == "PROF_02")
        # LNST = 2.4ty, DT = 20ty -> NM = 12%
        expected = 2400000000 / 20000000000 * 100
        assert nm.value is not None
        assert abs(nm.value - expected) < 0.01

    def test_roa(self, normal_data):
        """ROA = LNST / Tong TS * 100."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        roa = next(r for r in ratios if r.code == "PROF_03")
        expected = 2400000000 / 15000000000 * 100
        assert roa.value is not None
        assert abs(roa.value - expected) < 0.01

    def test_roe(self, normal_data):
        """ROE = LNST / VCSH * 100."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        roe = next(r for r in ratios if r.code == "PROF_04")
        expected = 2400000000 / 8000000000 * 100
        assert roe.value is not None
        assert abs(roe.value - expected) < 0.01

    def test_debt_to_assets(self, normal_data):
        """He so no / Tong TS."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        da = next(r for r in ratios if r.code == "LEV_01")
        expected = 7000000000 / 15000000000 * 100
        assert da.value is not None
        assert abs(da.value - expected) < 0.01

    def test_debt_to_equity(self, normal_data):
        """He so no / VCSH."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        de = next(r for r in ratios if r.code == "LEV_02")
        expected = 7000000000 / 8000000000
        assert de.value is not None
        assert abs(de.value - expected) < 0.001

    def test_asset_turnover(self, normal_data):
        """Vong quay tong TS = DT / Tong TS."""
        analyzer = RatioAnalyzer(normal_data)
        ratios = analyzer.analyze()

        at = next(r for r in ratios if r.code == "EFF_01")
        expected = 20000000000 / 15000000000
        assert at.value is not None
        assert abs(at.value - expected) < 0.001

    def test_zero_denominator(self):
        """Mau so = 0 -> value = None."""
        data = {
            "cdkt": {
                "so_cuoi_nam": {
                    "ct100": 0, "ct110": 0, "ct140": 0,
                    "ct300": 0, "ct400": 0, "ct410": 0, "ct500": 0,
                },
                "so_dau_nam": {"ct300": 0, "ct500": 0},
            },
            "kqhdkd": {
                "nam_nay": {
                    "ct10": 0, "ct20": 0, "ct30": 0, "ct60": 0,
                },
            },
        }
        analyzer = RatioAnalyzer(data)
        ratios = analyzer.analyze()

        cr = next(r for r in ratios if r.code == "LIQ_01")
        assert cr.value is None


# ─── Test JournalReconstructor ───────────────────────────

class TestJournalReconstructor:
    """Test tai tao but toan."""

    def test_reconstruct_returns_list(self, journal_cdtk_data):
        """reconstruct tra ve list."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()
        assert isinstance(entries, list)

    def test_entries_have_structure(self, journal_cdtk_data):
        """Moi entry co day du truong."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        for e in entries:
            assert isinstance(e, JournalEntry)
            assert e.description
            assert e.debit_account
            assert e.debit_account_name
            assert e.credit_account
            assert e.credit_account_name
            assert e.category in ["operating", "investing", "financing", "unknown"]
            assert 0 <= e.confidence <= 1

    def test_matched_entries_have_amount(self, journal_cdtk_data):
        """But toan khop co so tien > 0."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        matched = [e for e in entries if e.confidence > 0]
        for e in matched:
            assert e.amount > 0

    def test_revenue_entry(self, journal_cdtk_data):
        """Nhan dien but toan doanh thu."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        # Tim but toan No 131 / Co 511 (ban hang ghi no)
        revenue_entries = [
            e for e in entries
            if e.debit_account == "131" and e.credit_account == "511"
        ]
        # Hoac No 112 / Co 511 (ban hang thu CK)
        revenue_entries += [
            e for e in entries
            if e.debit_account == "112" and e.credit_account == "511"
        ]
        # Phai co it nhat 1 but toan doanh thu
        assert len(revenue_entries) > 0

    def test_cogs_entry(self, journal_cdtk_data):
        """Nhan dien but toan gia von."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        # No 632 / Co 156 (xuat kho hang ban)
        cogs = [
            e for e in entries
            if e.debit_account == "632" and e.credit_account == "156"
        ]
        assert len(cogs) > 0

    def test_kc_entries(self, journal_cdtk_data):
        """Nhan dien but toan ket chuyen."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        # No 511 / Co 911 (ket chuyen DT)
        kc_dt = [
            e for e in entries
            if e.debit_account == "511" and e.credit_account == "911"
        ]
        assert len(kc_dt) > 0

    def test_empty_cdtk(self):
        """CDTK rong -> list rong."""
        reconstructor = JournalReconstructor({}, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()
        assert entries == []

    def test_categorization(self, journal_cdtk_data):
        """But toan duoc phan loai dung."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        # But toan hoat dong kinh doanh
        operating = [e for e in entries if e.category == "operating"]
        assert len(operating) > 0

    def test_unmatched_entries(self, journal_cdtk_data):
        """PS chua khop duoc danh dau unknown."""
        reconstructor = JournalReconstructor(journal_cdtk_data, CDTK_ACCOUNT_MAP)
        entries = reconstructor.reconstruct()

        unknown = [e for e in entries if e.category == "unknown"]
        # Co the co hoac khong, nhung neu co thi confidence = 0
        for e in unknown:
            assert e.confidence == 0.0


# ─── Test RiskLevel Enum ────────────────────────────────

class TestRiskLevel:
    """Test RiskLevel enum."""

    def test_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_is_string(self):
        assert isinstance(RiskLevel.LOW, str)
