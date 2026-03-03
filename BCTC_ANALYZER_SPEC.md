# BCTC Analyzer — Tài liệu Kỹ thuật Triển khai

## 1. Tổng quan

**Mục tiêu:** Xây dựng phần mềm chạy local, nạp file XML xuất từ HTKK (Thông tư 133/2016 & 200/2014), tự động phân tích - đối chiếu chéo - phát hiện bất thường trong Bộ BCTC doanh nghiệp.

**Đầu vào:** File XML theo chuẩn HTKK (mẫu B01b-DNN cho TT133, B01-DN cho TT200)

**Đầu ra:**
- Dashboard tổng quan sức khỏe BCTC
- Báo cáo đối chiếu chéo 4 báo cáo
- Tái tạo bút toán gốc (journal reconstruction)
- Phát hiện bất thường & cảnh báo rủi ro thuế
- Phân tích chỉ số tài chính
- Xuất báo cáo PDF/Excel

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (UI)                     │
│              React + Tailwind + Recharts             │
│                   localhost:5173                     │
└────────────────────────┬────────────────────────────┘
                         │ REST API / WebSocket
┌────────────────────────┴────────────────────────────┐
│                Backend (FastAPI)                     │
│                  localhost:8000                      │
│                                                     │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌────────┐ │
│  │ Parser  │ │ Validator│ │ Analyzer  │ │Reporter│ │
│  │ Module  │ │ Module   │ │ Module    │ │ Module │ │
│  └─────────┘ └──────────┘ └───────────┘ └────────┘ │
│                      │                              │
│              ┌───────┴───────┐                      │
│              │  Core Models  │                      │
│              │  (Pydantic)   │                      │
│              └───────────────┘                      │
└─────────────────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │   SQLite (optional) │
              │   Lưu lịch sử phân │
              │   tích nếu cần     │
              └─────────────────────┘
```

### Tech Stack

| Layer | Công nghệ | Lý do |
|-------|-----------|-------|
| Backend | Python 3.11+ / FastAPI | Mạnh xử lý XML, tính toán, ecosystem kế toán |
| Frontend | React + Vite + Tailwind | SPA nhanh, chart đẹp |
| Charts | Recharts hoặc Chart.js | Trực quan hóa dữ liệu tài chính |
| Data Models | Pydantic v2 | Validation chặt, serialization tự động |
| XML Parse | lxml + defusedxml | Nhanh, an toàn |
| Export | openpyxl (Excel), reportlab (PDF) | Xuất báo cáo |
| DB (tuỳ chọn) | SQLite | Lưu lịch sử, so sánh qua các năm |

---

## 3. Cấu trúc thư mục dự án

```
bctc-analyzer/
├── backend/
│   ├── main.py                    # FastAPI entrypoint
│   ├── config.py                  # Settings, constants
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base Pydantic models
│   │   ├── cdkt.py                # Bảng Cân đối kế toán
│   │   ├── kqhdkd.py             # Kết quả HĐKD
│   │   ├── lctt.py                # Lưu chuyển tiền tệ
│   │   ├── cdtk.py                # Cân đối tài khoản
│   │   ├── thuyet_minh.py         # Thuyết minh BCTC
│   │   └── journal.py             # Bút toán tái tạo
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── xml_parser.py          # Core XML parser
│   │   ├── tt133_mapper.py        # Mapping mã chỉ tiêu TT133
│   │   ├── tt200_mapper.py        # Mapping mã chỉ tiêu TT200
│   │   └── detector.py            # Tự nhận diện TT133 vs TT200
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── cross_check.py         # Đối chiếu chéo 4 báo cáo
│   │   ├── balance_check.py       # Kiểm tra cân đối nội bộ
│   │   └── rules.py               # Bộ quy tắc kiểm tra
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── journal_reconstructor.py  # Tái tạo bút toán
│   │   ├── anomaly_detector.py       # Phát hiện bất thường
│   │   ├── ratio_analyzer.py         # Phân tích chỉ số TC
│   │   ├── tax_risk.py               # Đánh giá rủi ro thuế
│   │   └── cash_flow_analyzer.py     # Phân tích dòng tiền
│   ├── reporter/
│   │   ├── __init__.py
│   │   ├── pdf_report.py          # Xuất PDF
│   │   ├── excel_report.py        # Xuất Excel
│   │   └── templates/             # Mẫu báo cáo
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # API endpoints
│   │   └── schemas.py             # Request/Response schemas
│   ├── tests/
│   │   ├── test_parser.py
│   │   ├── test_validator.py
│   │   ├── test_analyzer.py
│   │   └── fixtures/              # Sample XML files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Upload.jsx         # Trang upload XML
│   │   │   ├── Dashboard.jsx      # Tổng quan
│   │   │   ├── CrossCheck.jsx     # Đối chiếu chéo
│   │   │   ├── JournalView.jsx    # Xem bút toán tái tạo
│   │   │   ├── Anomalies.jsx      # Cảnh báo bất thường
│   │   │   └── Ratios.jsx         # Chỉ số tài chính
│   │   ├── components/
│   │   │   ├── FileUploader.jsx
│   │   │   ├── BalanceSheet.jsx
│   │   │   ├── IncomeStatement.jsx
│   │   │   ├── CashFlowChart.jsx
│   │   │   ├── AlertCard.jsx
│   │   │   └── ExportButton.jsx
│   │   └── utils/
│   │       └── formatters.js      # Format tiền VND, %
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml             # Tuỳ chọn containerize
├── Makefile                       # Lệnh tắt dev/build
└── README.md
```

---

## 4. Chi tiết từng Module

---

### 4.1 MODULE: Parser (`backend/parser/`)

**Nhiệm vụ:** Đọc XML từ HTKK → chuyển thành Python objects có cấu trúc.

#### 4.1.1 Cấu trúc XML của HTKK

File XML HTKK có cấu trúc cố định:

```
HSoThueDTu
└── HSoKhaiThue
    ├── TTinChung                    # Thông tin chung (MST, tên DN, CQT...)
    │   ├── TTinDVu                  # Phần mềm, phiên bản
    │   ├── TTinTKhaiThue
    │   │   ├── TKhaiThue           # Mã tờ khai, kỳ, loại
    │   │   └── NNT                  # Người nộp thuế
    ├── CTieuTKhaiChinh              # === BẢNG CÂN ĐỐI KẾ TOÁN ===
    │   ├── ThuyetMinh               # Mã thuyết minh cho từng chỉ tiêu
    │   ├── SoCuoiNam                # Số cuối năm (ct100..ct600)
    │   └── SoDauNam                 # Số đầu năm
    └── PLuc                         # === CÁC PHỤ LỤC ===
        ├── PL_KQHDSXKD             # Kết quả HĐKD
        │   ├── ThuyetMinh
        │   ├── NamNay               # (ct01..ct60)
        │   └── NamTruoc
        ├── PL_LCTTTT               # Lưu chuyển tiền tệ (trực tiếp)
        │   ├── ThuyetMinh
        │   ├── NamNay               # (ct01..ct70)
        │   └── NamTruoc
        └── PL_CDTK                 # Cân đối tài khoản
            ├── SoDuDauKy            # Nợ/Có đầu kỳ
            ├── SoPhatSinhTrongKy    # Nợ/Có phát sinh
            └── SoDuCuoiKy           # Nợ/Có cuối kỳ
```

#### 4.1.2 Code mẫu — XML Parser

```python
# backend/parser/xml_parser.py

from lxml import etree
from typing import Dict, Any, Optional
from pathlib import Path
import re

# Namespace trong XML HTKK
NS = {"ns": "http://kekhaithue.gdt.gov.vn/TKhaiThue"}


class HtkkXmlParser:
    """
    Parse file XML BCTC xuất từ HTKK.
    Hỗ trợ TT133 (mã tờ khai 684) và TT200 (mã tờ khai 405).
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.tree = etree.parse(str(self.file_path))
        self.root = self.tree.getroot()
        self.ns = NS

    # ─── Thông tin chung ──────────────────────────────────

    def get_company_info(self) -> Dict[str, str]:
        """Trích xuất thông tin doanh nghiệp."""
        nnt = self.root.find(".//ns:NNT", self.ns)
        tkhai = self.root.find(".//ns:TKhaiThue", self.ns)
        ky = self.root.find(".//ns:KyKKhaiThue", self.ns)

        return {
            "mst": self._text(nnt, "ns:mst"),
            "ten_dn": self._text(nnt, "ns:tenNNT"),
            "dia_chi": self._text(nnt, "ns:dchiNNT"),
            "tinh": self._text(nnt, "ns:tenTinhNNT"),
            "ma_to_khai": self._text(tkhai, "ns:maTKhai"),
            "ten_to_khai": self._text(tkhai, "ns:tenTKhai"),
            "ky_bao_cao": self._text(ky, "ns:kyKKhai"),
            "tu_ngay": self._text(ky, "ns:kyKKhaiTuNgay"),
            "den_ngay": self._text(ky, "ns:kyKKhaiDenNgay"),
            "ngay_lap": self._text(tkhai, "ns:ngayLapTKhai"),
        }

    def detect_circular(self) -> str:
        """Nhận diện Thông tư: 133 hay 200 dựa trên mã tờ khai."""
        ma = self._text(
            self.root.find(".//ns:TKhaiThue", self.ns), "ns:maTKhai"
        )
        if ma == "684":
            return "TT133"
        elif ma == "405":
            return "TT200"
        else:
            raise ValueError(f"Mã tờ khai không nhận diện được: {ma}")

    # ─── Bảng Cân đối Kế toán ────────────────────────────

    def parse_cdkt(self) -> Dict[str, Any]:
        """Parse Bảng CĐKT (nằm trong CTieuTKhaiChinh)."""
        main = self.root.find(".//ns:CTieuTKhaiChinh", self.ns)

        return {
            "thuyet_minh": self._parse_ct_block(
                main.find("ns:ThuyetMinh", self.ns)
            ),
            "so_cuoi_nam": self._parse_ct_block(
                main.find("ns:SoCuoiNam", self.ns)
            ),
            "so_dau_nam": self._parse_ct_block(
                main.find("ns:SoDauNam", self.ns)
            ),
        }

    # ─── Kết quả HĐKD ────────────────────────────────────

    def parse_kqhdkd(self) -> Dict[str, Any]:
        """Parse Báo cáo KQHĐKD."""
        pl = self.root.find(".//ns:PL_KQHDSXKD", self.ns)
        if pl is None:
            return {}

        return {
            "thuyet_minh": self._parse_ct_block(
                pl.find("ns:ThuyetMinh", self.ns)
            ),
            "nam_nay": self._parse_ct_block(
                pl.find("ns:NamNay", self.ns)
            ),
            "nam_truoc": self._parse_ct_block(
                pl.find("ns:NamTruoc", self.ns)
            ),
        }

    # ─── Lưu chuyển tiền tệ ──────────────────────────────

    def parse_lctt(self) -> Dict[str, Any]:
        """Parse Báo cáo LCTT (phương pháp trực tiếp)."""
        pl = self.root.find(".//ns:PL_LCTTTT", self.ns)
        if pl is None:
            # Thử phương pháp gián tiếp
            pl = self.root.find(".//ns:PL_LCTTGT", self.ns)
        if pl is None:
            return {}

        return {
            "thuyet_minh": self._parse_ct_block(
                pl.find("ns:ThuyetMinh", self.ns)
            ),
            "nam_nay": self._parse_ct_block(
                pl.find("ns:NamNay", self.ns)
            ),
            "nam_truoc": self._parse_ct_block(
                pl.find("ns:NamTruoc", self.ns)
            ),
        }

    # ─── Cân đối Tài khoản ───────────────────────────────

    def parse_cdtk(self) -> Dict[str, Any]:
        """Parse Bảng CĐTK (Nợ/Có cho từng TK)."""
        pl = self.root.find(".//ns:PL_CDTK", self.ns)
        if pl is None:
            return {}

        result = {}
        for period_tag in ["SoDuDauKy", "SoPhatSinhTrongKy", "SoDuCuoiKy"]:
            period = pl.find(f"ns:{period_tag}", self.ns)
            if period is not None:
                no = period.find("ns:No", self.ns)
                co = period.find("ns:Co", self.ns)
                result[period_tag] = {
                    "no": self._parse_ct_block(no) if no is not None else {},
                    "co": self._parse_ct_block(co) if co is not None else {},
                }

        return result

    # ─── Helpers ──────────────────────────────────────────

    def _text(self, parent, tag: str) -> str:
        """Lấy text content, trả về '' nếu không tìm thấy."""
        if parent is None:
            return ""
        el = parent.find(tag, self.ns)
        return (el.text or "").strip() if el is not None else ""

    def _parse_ct_block(self, parent) -> Dict[str, Any]:
        """
        Parse block chứa các tag ct000, ct001, ...
        Trả về dict: {"ct100": 14995957186, "ct110": 14995708386, ...}
        Giá trị số được convert sang int/float, text giữ nguyên str.
        """
        if parent is None:
            return {}

        result = {}
        for child in parent:
            # Bỏ namespace prefix
            tag = etree.QName(child).localname
            text = (child.text or "").strip()

            if not text:
                result[tag] = None
                continue

            # Thử parse số
            try:
                if "." in text:
                    result[tag] = float(text)
                else:
                    result[tag] = int(text)
            except ValueError:
                result[tag] = text

        return result

    # ─── All-in-one ───────────────────────────────────────

    def parse_all(self) -> Dict[str, Any]:
        """Parse toàn bộ BCTC thành 1 dict lớn."""
        return {
            "company": self.get_company_info(),
            "circular": self.detect_circular(),
            "cdkt": self.parse_cdkt(),
            "kqhdkd": self.parse_kqhdkd(),
            "lctt": self.parse_lctt(),
            "cdtk": self.parse_cdtk(),
        }
```

#### 4.1.3 Mapping mã chỉ tiêu → Tên tiếng Việt

```python
# backend/parser/tt133_mapper.py

"""
Mapping mã chỉ tiêu XML → tên chỉ tiêu BCTC theo TT133/2016.
Dùng cho hiển thị UI và báo cáo.
"""

# ═══════════════════════════════════════════════════════
#  BẢNG CÂN ĐỐI KẾ TOÁN (B01b-DNN)
# ═══════════════════════════════════════════════════════

CDKT_MAP = {
    # --- TÀI SẢN ---
    "ct100": {"name": "TÀI SẢN NGẮN HẠN", "level": 0, "ms": 100},
    "ct110": {"name": "Tiền và các khoản tương đương tiền", "level": 1, "ms": 110},
    "ct120": {"name": "Đầu tư tài chính ngắn hạn", "level": 1, "ms": 120},
    "ct121": {"name": "Chứng khoán kinh doanh", "level": 2, "ms": 121},
    "ct122": {"name": "Dự phòng giảm giá CKKD", "level": 2, "ms": 122},
    "ct123": {"name": "Đầu tư nắm giữ đến ngày đáo hạn", "level": 2, "ms": 123},
    "ct130": {"name": "Các khoản phải thu ngắn hạn", "level": 1, "ms": 130},
    "ct131": {"name": "Phải thu khách hàng", "level": 2, "ms": 131},
    "ct132": {"name": "Trả trước cho người bán", "level": 2, "ms": 132},
    "ct133": {"name": "Các khoản phải thu khác", "level": 2, "ms": 133},
    "ct134": {"name": "Thuế GTGT được khấu trừ", "level": 2, "ms": 134},
    # (TT133 gộp VAT vào phải thu khác, không tách riêng ct134)
    "ct135": {"name": "Dự phòng phải thu ngắn hạn khó đòi", "level": 2, "ms": 135},
    "ct140": {"name": "Hàng tồn kho", "level": 1, "ms": 140},
    "ct141": {"name": "Hàng tồn kho", "level": 2, "ms": 141},
    "ct142": {"name": "Dự phòng giảm giá HTK", "level": 2, "ms": 142},
    "ct150": {"name": "Tài sản ngắn hạn khác", "level": 1, "ms": 150},
    "ct151": {"name": "Thuế GTGT được khấu trừ", "level": 2, "ms": 151},
    "ct152": {"name": "Thuế và các khoản phải thu Nhà nước", "level": 2, "ms": 152},

    # --- TÀI SẢN DÀI HẠN ---
    "ct200": {"name": "TÀI SẢN DÀI HẠN", "level": 0, "ms": 200},
    "ct210": {"name": "Tài sản cố định", "level": 1, "ms": 210},
    "ct211": {"name": "Nguyên giá TSCĐ hữu hình", "level": 2, "ms": 211},
    "ct212": {"name": "Giá trị hao mòn luỹ kế", "level": 2, "ms": 212},
    "ct213": {"name": "Nguyên giá TSCĐ thuê TC", "level": 2, "ms": 213},
    "ct214": {"name": "Giá trị hao mòn luỹ kế TSCĐ thuê TC", "level": 2, "ms": 214},
    "ct215": {"name": "Nguyên giá TSCĐ vô hình", "level": 2, "ms": 215},
    "ct220": {"name": "Bất động sản đầu tư", "level": 1, "ms": 220},
    "ct221": {"name": "Nguyên giá BĐSĐT", "level": 2, "ms": 221},
    "ct222": {"name": "Giá trị hao mòn luỹ kế BĐSĐT", "level": 2, "ms": 222},
    "ct230": {"name": "Xây dựng cơ bản dở dang", "level": 1, "ms": 230},
    "ct240": {"name": "Đầu tư tài chính dài hạn", "level": 1, "ms": 240},
    "ct250": {"name": "Tài sản dài hạn khác", "level": 1, "ms": 250},
    "ct260": {"name": "Lợi thế thương mại", "level": 1, "ms": 260},
    "ct300": {"name": "TỔNG CỘNG TÀI SẢN", "level": 0, "ms": 300, "bold": True},

    # --- NGUỒN VỐN ---
    "ct400": {"name": "NỢ PHẢI TRẢ", "level": 0, "ms": 400},
    "ct410": {"name": "Nợ ngắn hạn", "level": 1, "ms": 410},
    "ct411": {"name": "Phải trả người bán ngắn hạn", "level": 2, "ms": 411},
    "ct412": {"name": "Người mua trả tiền trước ngắn hạn", "level": 2, "ms": 412},
    "ct413": {"name": "Thuế và các khoản phải nộp Nhà nước", "level": 2, "ms": 413},
    "ct414": {"name": "Phải trả người lao động", "level": 2, "ms": 414},
    "ct415": {"name": "Chi phí phải trả ngắn hạn", "level": 2, "ms": 415},
    "ct416": {"name": "Các khoản phải trả, phải nộp NH khác", "level": 2, "ms": 416},
    "ct417": {"name": "Vay và nợ thuê tài chính ngắn hạn", "level": 2, "ms": 417},
    "ct418": {"name": "Quỹ khen thưởng, phúc lợi", "level": 2, "ms": 418},
    "ct420": {"name": "Nợ dài hạn", "level": 1, "ms": 420},
    "ct421": {"name": "Phải trả người bán dài hạn", "level": 2, "ms": 421},
    "ct500": {"name": "VỐN CHỦ SỞ HỮU", "level": 0, "ms": 500},
    "ct511": {"name": "Vốn góp của chủ sở hữu", "level": 1, "ms": 511},
    "ct512": {"name": "Thặng dư vốn cổ phần", "level": 1, "ms": 512},
    "ct513": {"name": "Vốn khác của chủ sở hữu", "level": 1, "ms": 513},
    "ct514": {"name": "Cổ phiếu quỹ", "level": 1, "ms": 514},
    "ct515": {"name": "Chênh lệch tỷ giá hối đoái", "level": 1, "ms": 515},
    "ct516": {"name": "Các quỹ", "level": 1, "ms": 516},
    "ct517": {"name": "Lợi nhuận sau thuế chưa phân phối", "level": 1, "ms": 517},
    "ct600": {"name": "TỔNG CỘNG NGUỒN VỐN", "level": 0, "ms": 600, "bold": True},
}


# ═══════════════════════════════════════════════════════
#  KẾT QUẢ HOẠT ĐỘNG KINH DOANH (B02-DNN)
# ═══════════════════════════════════════════════════════

KQHDKD_MAP = {
    "ct01": {"name": "Doanh thu bán hàng và cung cấp dịch vụ", "ms": "01"},
    "ct02": {"name": "Các khoản giảm trừ doanh thu", "ms": "02"},
    "ct10": {"name": "Doanh thu thuần", "ms": 10},
    "ct11": {"name": "Giá vốn hàng bán", "ms": 11},
    "ct20": {"name": "Lợi nhuận gộp", "ms": 20},
    "ct21": {"name": "Doanh thu hoạt động tài chính", "ms": 21},
    "ct22": {"name": "Chi phí tài chính", "ms": 22},
    "ct23": {"name": "Chi phí bán hàng", "ms": 23},
    "ct24": {"name": "Chi phí quản lý doanh nghiệp", "ms": 24},
    "ct30": {"name": "Lợi nhuận thuần từ HĐKD", "ms": 30},
    "ct31": {"name": "Thu nhập khác", "ms": 31},
    "ct32": {"name": "Chi phí khác", "ms": 32},
    "ct40": {"name": "Lợi nhuận khác", "ms": 40},
    "ct50": {"name": "Tổng lợi nhuận kế toán trước thuế", "ms": 50},
    "ct51": {"name": "Chi phí thuế TNDN", "ms": 51},
    "ct60": {"name": "Lợi nhuận sau thuế TNDN", "ms": 60},
}


# ═══════════════════════════════════════════════════════
#  LƯU CHUYỂN TIỀN TỆ - TRỰC TIẾP (B03-DNN)
# ═══════════════════════════════════════════════════════

LCTT_TT_MAP = {
    # --- HĐKD ---
    "ct01": {"name": "Tiền thu từ bán hàng, cung cấp DV", "ms": "01", "flow": "operating"},
    "ct02": {"name": "Tiền chi trả cho người cung cấp hàng hoá, DV", "ms": "02", "flow": "operating"},
    "ct03": {"name": "Tiền chi trả cho người lao động", "ms": "03", "flow": "operating"},
    "ct04": {"name": "Tiền chi trả lãi vay", "ms": "04", "flow": "operating"},
    "ct05": {"name": "Tiền chi nộp thuế TNDN", "ms": "05", "flow": "operating"},
    "ct06": {"name": "Tiền thu khác từ HĐKD", "ms": "06", "flow": "operating"},
    "ct07": {"name": "Tiền chi khác cho HĐKD", "ms": "07", "flow": "operating"},
    "ct20": {"name": "Lưu chuyển tiền thuần từ HĐKD", "ms": 20, "flow": "operating", "subtotal": True},

    # --- HĐ Đầu tư ---
    "ct21": {"name": "Tiền chi mua sắm, xây dựng TSCĐ", "ms": 21, "flow": "investing"},
    "ct22": {"name": "Tiền thu từ thanh lý TSCĐ", "ms": 22, "flow": "investing"},
    "ct23": {"name": "Tiền chi cho vay, mua công cụ nợ", "ms": 23, "flow": "investing"},
    "ct24": {"name": "Tiền thu hồi cho vay, bán công cụ nợ", "ms": 24, "flow": "investing"},
    "ct25": {"name": "Tiền thu lãi cho vay, cổ tức, LN được chia", "ms": 25, "flow": "investing"},
    "ct30": {"name": "Lưu chuyển tiền thuần từ HĐ đầu tư", "ms": 30, "flow": "investing", "subtotal": True},

    # --- HĐ Tài chính ---
    "ct31": {"name": "Tiền thu từ phát hành CP, nhận vốn góp", "ms": 31, "flow": "financing"},
    "ct32": {"name": "Tiền chi trả vốn góp cho CSH, mua lại CP", "ms": 32, "flow": "financing"},
    "ct33": {"name": "Tiền thu từ đi vay", "ms": 33, "flow": "financing"},
    "ct34": {"name": "Tiền chi trả nợ gốc vay", "ms": 34, "flow": "financing"},
    "ct35": {"name": "Tiền chi trả nợ gốc thuê TC", "ms": 35, "flow": "financing"},
    "ct40": {"name": "Lưu chuyển tiền thuần từ HĐ tài chính", "ms": 40, "flow": "financing", "subtotal": True},

    # --- Tổng hợp ---
    "ct50": {"name": "Tăng/giảm tiền thuần trong kỳ", "ms": 50, "total": True},
    "ct60": {"name": "Tiền và tương đương tiền đầu kỳ", "ms": 60},
    "ct61": {"name": "Ảnh hưởng thay đổi tỷ giá", "ms": 61},
    "ct70": {"name": "Tiền và tương đương tiền cuối kỳ", "ms": 70, "total": True},
}


# ═══════════════════════════════════════════════════════
#  CÂN ĐỐI TÀI KHOẢN - Mapping TK kế toán
# ═══════════════════════════════════════════════════════

CDTK_ACCOUNT_MAP = {
    # TK Loại 1 - Tài sản
    "ct111":  {"name": "Tiền mặt", "tk": "111", "loai": "TS"},
    "ct1111": {"name": "Tiền Việt Nam", "tk": "1111", "parent": "111"},
    "ct1112": {"name": "Ngoại tệ", "tk": "1112", "parent": "111"},
    "ct112":  {"name": "Tiền gửi ngân hàng", "tk": "112", "loai": "TS"},
    "ct1121": {"name": "Tiền Việt Nam", "tk": "1121", "parent": "112"},
    "ct1122": {"name": "Ngoại tệ", "tk": "1122", "parent": "112"},
    "ct121":  {"name": "Chứng khoán kinh doanh", "tk": "121", "loai": "TS"},
    "ct128":  {"name": "Đầu tư nắm giữ đến ngày đáo hạn", "tk": "128", "loai": "TS"},
    "ct131":  {"name": "Phải thu khách hàng", "tk": "131", "loai": "LK"},
    "ct133":  {"name": "Thuế GTGT được khấu trừ", "tk": "133", "loai": "TS"},
    "ct1331": {"name": "Thuế GTGT đầu vào hàng hoá, DV", "tk": "1331", "parent": "133"},
    "ct1332": {"name": "Thuế GTGT đầu vào TSCĐ", "tk": "1332", "parent": "133"},
    "ct136":  {"name": "Phải thu nội bộ", "tk": "136", "loai": "TS"},
    "ct138":  {"name": "Phải thu khác", "tk": "138", "loai": "TS"},
    "ct141":  {"name": "Tạm ứng", "tk": "141", "loai": "TS"},
    "ct151":  {"name": "Hàng mua đang đi đường", "tk": "151", "loai": "TS"},
    "ct152":  {"name": "Nguyên liệu, vật liệu", "tk": "152", "loai": "TS"},
    "ct153":  {"name": "Công cụ, dụng cụ", "tk": "153", "loai": "TS"},
    "ct154":  {"name": "CP SXKD dở dang", "tk": "154", "loai": "TS"},
    "ct155":  {"name": "Thành phẩm", "tk": "155", "loai": "TS"},
    "ct156":  {"name": "Hàng hoá", "tk": "156", "loai": "TS"},
    "ct157":  {"name": "Hàng gửi đi bán", "tk": "157", "loai": "TS"},

    # TK Loại 2 - Tài sản dài hạn
    "ct211":  {"name": "TSCĐ hữu hình", "tk": "211", "loai": "TS"},
    "ct214":  {"name": "Hao mòn TSCĐ", "tk": "214", "loai": "TS_AM"},  # Dư Có
    "ct217":  {"name": "BĐS đầu tư", "tk": "217", "loai": "TS"},
    "ct228":  {"name": "Đầu tư góp vốn vào đơn vị khác", "tk": "228", "loai": "TS"},
    "ct229":  {"name": "Dự phòng tổn thất tài sản", "tk": "229", "loai": "TS_DP"},
    "ct241":  {"name": "XDCB dở dang", "tk": "241", "loai": "TS"},
    "ct242":  {"name": "Chi phí trả trước", "tk": "242", "loai": "TS"},

    # TK Loại 3 - Nợ phải trả
    "ct331":  {"name": "Phải trả cho người bán", "tk": "331", "loai": "LK"},
    "ct333":  {"name": "Thuế và các khoản phải nộp NN", "tk": "333", "loai": "NV"},
    "ct3331": {"name": "Thuế GTGT phải nộp", "tk": "3331", "parent": "333"},
    "ct3334": {"name": "Thuế TNDN", "tk": "3334", "parent": "333"},
    "ct3335": {"name": "Thuế TNCN", "tk": "3335", "parent": "333"},
    "ct334":  {"name": "Phải trả người lao động", "tk": "334", "loai": "NV"},
    "ct335":  {"name": "Chi phí phải trả", "tk": "335", "loai": "NV"},
    "ct336":  {"name": "Phải trả nội bộ", "tk": "336", "loai": "NV"},
    "ct338":  {"name": "Phải trả, phải nộp khác", "tk": "338", "loai": "NV"},
    "ct341":  {"name": "Vay và nợ thuê TC", "tk": "341", "loai": "NV"},
    "ct352":  {"name": "Dự phòng phải trả", "tk": "352", "loai": "NV"},
    "ct353":  {"name": "Quỹ khen thưởng, phúc lợi", "tk": "353", "loai": "NV"},
    "ct356":  {"name": "Quỹ phát triển KH&CN", "tk": "356", "loai": "NV"},

    # TK Loại 4 - Vốn chủ sở hữu
    "ct411":  {"name": "Vốn đầu tư của CSH", "tk": "411", "loai": "NV"},
    "ct4111": {"name": "Vốn góp của CSH", "tk": "4111", "parent": "411"},
    "ct4112": {"name": "Thặng dư vốn cổ phần", "tk": "4112", "parent": "411"},
    "ct4118": {"name": "Vốn khác", "tk": "4118", "parent": "411"},
    "ct413":  {"name": "Chênh lệch tỷ giá hối đoái", "tk": "413", "loai": "NV"},
    "ct418":  {"name": "Các quỹ thuộc VCSH", "tk": "418", "loai": "NV"},
    "ct419":  {"name": "Cổ phiếu quỹ", "tk": "419", "loai": "NV_AM"},
    "ct421":  {"name": "Lợi nhuận sau thuế chưa PP", "tk": "421", "loai": "LK"},
    "ct4211": {"name": "LNST chưa PP năm trước", "tk": "4211", "parent": "421"},
    "ct4212": {"name": "LNST chưa PP năm nay", "tk": "4212", "parent": "421"},

    # TK Loại 5 - Doanh thu
    "ct511":  {"name": "Doanh thu bán hàng và CCDV", "tk": "511", "loai": "DT"},
    "ct515":  {"name": "Doanh thu hoạt động tài chính", "tk": "515", "loai": "DT"},

    # TK Loại 6 - Chi phí
    "ct611":  {"name": "Mua hàng", "tk": "611", "loai": "CP"},
    "ct631":  {"name": "Giá thành sản xuất", "tk": "631", "loai": "CP"},
    "ct632":  {"name": "Giá vốn hàng bán", "tk": "632", "loai": "CP"},
    "ct635":  {"name": "Chi phí tài chính", "tk": "635", "loai": "CP"},
    "ct642":  {"name": "Chi phí quản lý kinh doanh", "tk": "642", "loai": "CP"},
    "ct6421": {"name": "CP bán hàng", "tk": "6421", "parent": "642"},
    "ct6422": {"name": "CP quản lý doanh nghiệp", "tk": "6422", "parent": "642"},

    # TK Loại 7 - Thu nhập khác
    "ct711":  {"name": "Thu nhập khác", "tk": "711", "loai": "DT"},

    # TK Loại 8 - Chi phí khác
    "ct811":  {"name": "Chi phí khác", "tk": "811", "loai": "CP"},
    "ct821":  {"name": "Chi phí thuế TNDN", "tk": "821", "loai": "CP"},

    # TK Loại 9 - Xác định KQKD
    "ct911":  {"name": "Xác định kết quả kinh doanh", "tk": "911", "loai": "XDKQ"},
}
```

---

### 4.2 MODULE: Validator (`backend/validator/`)

**Nhiệm vụ:** Kiểm tra tính hợp lệ và đối chiếu chéo giữa 4 báo cáo.

```python
# backend/validator/cross_check.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CheckResult:
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
        self.cdkt_cn = data["cdkt"]["so_cuoi_nam"]      # Cuối năm
        self.cdkt_dn = data["cdkt"]["so_dau_nam"]        # Đầu năm
        self.kqhdkd = data["kqhdkd"]["nam_nay"]
        self.lctt = data["lctt"]["nam_nay"]
        self.cdtk_dk = data["cdtk"].get("SoDuDauKy", {})
        self.cdtk_ps = data["cdtk"].get("SoPhatSinhTrongKy", {})
        self.cdtk_ck = data["cdtk"].get("SoDuCuoiKy", {})
        self.results: List[CheckResult] = []

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

    def _check_cdkt_balance(self):
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

    def _check_cdkt_subtotals(self):
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

    def _check_kqhdkd_formulas(self):
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

    def _check_lctt_totals(self):
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

    def _check_cdkt_vs_kqhdkd(self):
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

    def _check_cdkt_vs_lctt(self):
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

    def _check_cdkt_vs_cdtk(self):
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

    def _check_cdtk_balance(self):
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

    def _check_lctt_classification(self):
        """Cảnh báo phân loại dòng tiền có thể sai."""
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
```

---

### 4.3 MODULE: Analyzer (`backend/analyzer/`)

#### 4.3.1 Tái tạo bút toán (Journal Reconstructor)

```python
# backend/analyzer/journal_reconstructor.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class JournalEntry:
    """Một bút toán kế toán được tái tạo."""
    description: str
    debit_account: str
    debit_account_name: str
    credit_account: str
    credit_account_name: str
    amount: float
    category: str           # "operating", "investing", "financing"
    confidence: float       # 0-1, độ tin cậy của suy luận
    notes: Optional[str] = None


class JournalReconstructor:
    """
    Tái tạo bút toán kế toán từ bảng CĐTK.

    Logic: So sánh PS Nợ và PS Có của từng TK,
    kết hợp với quan hệ đối ứng thông dụng để suy ra bút toán.
    """

    # Các cặp đối ứng phổ biến (debit_tk, credit_tk, description)
    COMMON_PAIRS = [
        # Góp vốn
        ("111", "411", "Góp vốn bằng tiền mặt"),
        ("112", "411", "Góp vốn qua ngân hàng"),
        # Gửi/rút tiền NH
        ("112", "111", "Nộp tiền mặt vào ngân hàng"),
        ("111", "112", "Rút tiền mặt từ ngân hàng"),
        # DT tài chính
        ("112", "515", "Lãi tiền gửi ngân hàng"),
        # CP tài chính
        ("635", "112", "Phí dịch vụ ngân hàng"),
        ("635", "111", "Chi phí tài chính (tiền mặt)"),
        # CP QLDN
        ("642", "111", "Chi phí QLDN (tiền mặt)"),
        ("642", "112", "Chi phí QLDN (chuyển khoản)"),
        ("642", "331", "Chi phí QLDN (nợ NCC)"),
        # VAT
        ("133", "111", "Thuế GTGT đầu vào (tiền mặt)"),
        ("133", "112", "Thuế GTGT đầu vào (chuyển khoản)"),
        ("133", "331", "Thuế GTGT đầu vào (nợ NCC)"),
        # Mua hàng
        ("156", "111", "Mua hàng hoá (tiền mặt)"),
        ("156", "112", "Mua hàng hoá (chuyển khoản)"),
        ("156", "331", "Mua hàng hoá (nợ NCC)"),
        # Bán hàng
        ("111", "511", "Bán hàng thu tiền mặt"),
        ("112", "511", "Bán hàng thu chuyển khoản"),
        ("131", "511", "Bán hàng ghi nợ"),
        # Giá vốn
        ("632", "156", "Xuất kho hàng bán"),
        # Kết chuyển
        ("511", "911", "Kết chuyển doanh thu"),
        ("515", "911", "Kết chuyển DT tài chính"),
        ("711", "911", "Kết chuyển thu nhập khác"),
        ("911", "632", "Kết chuyển giá vốn"),
        ("911", "635", "Kết chuyển CP tài chính"),
        ("911", "642", "Kết chuyển CP QLDN"),
        ("911", "811", "Kết chuyển CP khác"),
        ("911", "821", "Kết chuyển CP thuế TNDN"),
        # Kết chuyển lãi/lỗ
        ("911", "421", "Kết chuyển lãi"),
        ("421", "911", "Kết chuyển lỗ"),
        # Lương
        ("642", "334", "Chi phí lương"),
        ("334", "111", "Trả lương tiền mặt"),
        ("334", "112", "Trả lương chuyển khoản"),
        # Thuế
        ("821", "3334", "Thuế TNDN phải nộp"),
        ("3334", "112", "Nộp thuế TNDN"),
        ("3331", "112", "Nộp thuế GTGT"),
    ]

    def __init__(self, cdtk_data: Dict[str, Any], account_map: Dict):
        self.ps = cdtk_data.get("SoPhatSinhTrongKy", {})
        self.account_map = account_map

    def reconstruct(self) -> List[JournalEntry]:
        """
        Tái tạo bút toán từ phát sinh Nợ/Có.

        Thuật toán:
        1. Lấy tất cả TK có phát sinh != 0
        2. Với mỗi cặp đối ứng phổ biến, kiểm tra xem
           PS Nợ bên này có khớp PS Có bên kia không
        3. Phân bổ số tiền theo min(PS Nợ, PS Có)
        4. Số dư còn lại đánh dấu "chưa xác định"
        """
        no_ps = self.ps.get("no", {})
        co_ps = self.ps.get("co", {})

        # Tạo bản sao để trừ dần
        no_remaining = {}
        co_remaining = {}

        for ct_key, val in no_ps.items():
            if ct_key == "tongCong" or not val:
                continue
            tk = self._ct_to_tk(ct_key)
            if tk:
                no_remaining[tk] = no_remaining.get(tk, 0) + float(val)

        for ct_key, val in co_ps.items():
            if ct_key == "tongCong" or not val:
                continue
            tk = self._ct_to_tk(ct_key)
            if tk:
                co_remaining[tk] = co_remaining.get(tk, 0) + float(val)

        entries = []

        # Match theo cặp đối ứng
        for debit_tk, credit_tk, desc in self.COMMON_PAIRS:
            no_amt = no_remaining.get(debit_tk, 0)
            co_amt = co_remaining.get(credit_tk, 0)

            if no_amt > 0 and co_amt > 0:
                amount = min(no_amt, co_amt)
                entries.append(JournalEntry(
                    description=desc,
                    debit_account=debit_tk,
                    debit_account_name=self._tk_name(debit_tk),
                    credit_account=credit_tk,
                    credit_account_name=self._tk_name(credit_tk),
                    amount=amount,
                    category=self._categorize(debit_tk, credit_tk),
                    confidence=0.8,
                ))
                no_remaining[debit_tk] -= amount
                co_remaining[credit_tk] -= amount

        # Báo cáo phần chưa match
        for tk, amt in no_remaining.items():
            if amt > 0.5:  # tolerance
                entries.append(JournalEntry(
                    description=f"PS Nợ chưa xác định đối ứng",
                    debit_account=tk,
                    debit_account_name=self._tk_name(tk),
                    credit_account="???",
                    credit_account_name="Chưa xác định",
                    amount=amt,
                    category="unknown",
                    confidence=0.0,
                    notes="Cần kiểm tra sổ chi tiết",
                ))

        return entries

    def _ct_to_tk(self, ct_key: str) -> Optional[str]:
        """Convert ct111 → '111', ct1121 → '1121', etc."""
        info = self.account_map.get(ct_key)
        return info["tk"] if info else None

    def _tk_name(self, tk: str) -> str:
        for info in self.account_map.values():
            if info.get("tk") == tk:
                return info["name"]
        return tk

    @staticmethod
    def _categorize(debit_tk: str, credit_tk: str) -> str:
        financing_tks = {"411", "341", "419"}
        investing_tks = {"211", "217", "228", "241", "121", "128"}

        if debit_tk in financing_tks or credit_tk in financing_tks:
            return "financing"
        if debit_tk in investing_tks or credit_tk in investing_tks:
            return "investing"
        return "operating"
```

#### 4.3.2 Phát hiện bất thường (Anomaly Detector)

```python
# backend/analyzer/anomaly_detector.py

from dataclasses import dataclass
from typing import List, Dict, Any
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
    data: Dict[str, Any] = None


class AnomalyDetector:
    """
    Phát hiện các bất thường & rủi ro thuế trong BCTC.
    Dựa trên kinh nghiệm kiểm toán và các red flags phổ biến.
    """

    def __init__(self, parsed_data: Dict[str, Any]):
        self.data = parsed_data
        self.cdkt = parsed_data["cdkt"]["so_cuoi_nam"]
        self.cdkt_dn = parsed_data["cdkt"]["so_dau_nam"]
        self.kqhdkd = parsed_data["kqhdkd"]["nam_nay"]
        self.lctt = parsed_data["lctt"]["nam_nay"]
        self.cdtk_ck = parsed_data["cdtk"].get("SoDuCuoiKy", {})
        self.anomalies: List[Anomaly] = []

    def detect_all(self) -> List[Anomaly]:
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
        """Cảnh báo: Tiền mặt tồn quỹ quá lớn."""
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
        """Cảnh báo: VCSH âm hoặc lỗ luỹ kế."""
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
        """Cảnh báo: DT lớn nhưng không thu được tiền."""
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
        """Cảnh báo: Công ty có vốn lớn nhưng không hoạt động."""
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
        """Cảnh báo: Phải thu lớn bất thường."""
        pt = self._g(self.cdkt, "ct130")
        tong_ts = self._g(self.cdkt, "ct300")
        dt = self._g(self.kqhdkd, "ct01")

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
        """Cảnh báo: HTK quá lớn so với DT."""
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
        """Cảnh báo: Chi phí bất thường."""
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
        """Cảnh báo: Dấu hiệu giao dịch liên kết."""
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
        """Cảnh báo: VAT đầu vào tồn đọng lớn."""
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
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0
```

#### 4.3.3 Phân tích chỉ số tài chính

```python
# backend/analyzer/ratio_analyzer.py

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
        self.cn = parsed_data["cdkt"]["so_cuoi_nam"]
        self.dn = parsed_data["cdkt"]["so_dau_nam"]
        self.kq = parsed_data["kqhdkd"]["nam_nay"]

    def analyze(self) -> List[FinancialRatio]:
        ratios = []
        ratios.extend(self._liquidity_ratios())
        ratios.extend(self._profitability_ratios())
        ratios.extend(self._leverage_ratios())
        ratios.extend(self._efficiency_ratios())
        return ratios

    def _liquidity_ratios(self) -> List[FinancialRatio]:
        tsnh = self._g(self.cn, "ct100")
        nnh = self._g(self.cn, "ct410")
        tien = self._g(self.cn, "ct110")
        htk = self._g(self.cn, "ct140")

        results = []

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
        dt = self._g(self.kq, "ct10")
        ln_gop = self._g(self.kq, "ct20")
        ln_thuan = self._g(self.kq, "ct30")
        lnst = self._g(self.kq, "ct60")
        tong_ts = self._g(self.cn, "ct300")
        vcsh = self._g(self.cn, "ct500")

        results = []

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
        no_pt = self._g(self.cn, "ct400")
        tong_ts = self._g(self.cn, "ct300")
        vcsh = self._g(self.cn, "ct500")

        results = []

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
        val = data.get(key, 0)
        return float(val) if val is not None else 0.0

    @staticmethod
    def _interpret_ratio(value, low, good):
        if value is None:
            return "Không tính được (mẫu số = 0)"
        if value >= good:
            return f"{value:.2f} — Tốt"
        elif value >= low:
            return f"{value:.2f} — Chấp nhận được"
        else:
            return f"{value:.2f} — Cần cải thiện"
```

---

### 4.4 MODULE: API (`backend/api/`)

```python
# backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os

from parser.xml_parser import HtkkXmlParser
from parser.tt133_mapper import CDTK_ACCOUNT_MAP
from validator.cross_check import CrossChecker
from analyzer.journal_reconstructor import JournalReconstructor
from analyzer.anomaly_detector import AnomalyDetector
from analyzer.ratio_analyzer import RatioAnalyzer

app = FastAPI(
    title="BCTC Analyzer",
    description="Phân tích Báo cáo Tài chính từ file XML HTKK",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload file XML → parse → validate → analyze → trả JSON.
    Đây là endpoint chính, xử lý all-in-one.
    """
    if not file.filename.endswith(".xml"):
        raise HTTPException(400, "Chỉ chấp nhận file .xml")

    # Lưu file tạm
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".xml"
    ) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 1. Parse
        parser = HtkkXmlParser(tmp_path)
        data = parser.parse_all()

        # 2. Validate (đối chiếu chéo)
        checker = CrossChecker(data)
        check_results = checker.run_all()

        # 3. Tái tạo bút toán
        reconstructor = JournalReconstructor(
            data["cdtk"], CDTK_ACCOUNT_MAP
        )
        journals = reconstructor.reconstruct()

        # 4. Phát hiện bất thường
        detector = AnomalyDetector(data)
        anomalies = detector.detect_all()

        # 5. Chỉ số tài chính
        ratio_analyzer = RatioAnalyzer(data)
        ratios = ratio_analyzer.analyze()

        return JSONResponse({
            "success": True,
            "company": data["company"],
            "circular": data["circular"],
            "reports": {
                "cdkt": data["cdkt"],
                "kqhdkd": data["kqhdkd"],
                "lctt": data["lctt"],
                "cdtk": data["cdtk"],
            },
            "validation": {
                "total_checks": len(check_results),
                "passed": sum(
                    1 for r in check_results if r.severity.value == "ok"
                ),
                "warnings": sum(
                    1 for r in check_results if r.severity.value == "warning"
                ),
                "errors": sum(
                    1 for r in check_results
                    if r.severity.value in ("error", "critical")
                ),
                "details": [
                    {
                        "rule_id": r.rule_id,
                        "rule_name": r.rule_name,
                        "severity": r.severity.value,
                        "message": r.message,
                        "difference": r.difference,
                    }
                    for r in check_results
                ],
            },
            "journals": [
                {
                    "description": j.description,
                    "debit": j.debit_account,
                    "debit_name": j.debit_account_name,
                    "credit": j.credit_account,
                    "credit_name": j.credit_account_name,
                    "amount": j.amount,
                    "category": j.category,
                    "confidence": j.confidence,
                }
                for j in journals
                if j.amount > 0
            ],
            "anomalies": [
                {
                    "code": a.code,
                    "title": a.title,
                    "description": a.description,
                    "risk_level": a.risk_level.value,
                    "category": a.category,
                    "suggestion": a.suggestion,
                }
                for a in anomalies
            ],
            "ratios": [
                {
                    "code": r.code,
                    "name": r.name,
                    "name_en": r.name_en,
                    "value": r.value,
                    "unit": r.unit,
                    "benchmark": r.benchmark,
                    "interpretation": r.interpretation,
                    "category": r.category,
                }
                for r in ratios
            ],
        })

    finally:
        os.unlink(tmp_path)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

---

### 4.5 MODULE: Frontend (React)

#### Cấu trúc trang chính

```
Upload.jsx  →  user chọn file XML
     ↓
Dashboard.jsx  →  tổng quan: thông tin DN, health score, summary
     ↓
Tabs:
  ├── CrossCheck.jsx    →  bảng đối chiếu, ✅❌ cho từng rule
  ├── JournalView.jsx   →  bảng bút toán tái tạo, filter theo loại
  ├── Anomalies.jsx     →  danh sách cảnh báo, severity badges
  └── Ratios.jsx        →  chỉ số tài chính, gauge charts
```

#### Component chính — Dashboard

```jsx
// frontend/src/pages/Dashboard.jsx (minh hoạ)

import { useState } from 'react';

export default function Dashboard({ data }) {
  const { company, validation, anomalies, ratios } = data;

  const healthScore = Math.round(
    (validation.passed / validation.total_checks) * 100
  );

  const riskCount = {
    critical: anomalies.filter(a => a.risk_level === 'critical').length,
    high: anomalies.filter(a => a.risk_level === 'high').length,
    medium: anomalies.filter(a => a.risk_level === 'medium').length,
  };

  return (
    <div className="p-6 space-y-6">
      {/* Company Info */}
      <div className="bg-white rounded-xl shadow p-6">
        <h1 className="text-2xl font-bold">{company.ten_dn}</h1>
        <p className="text-gray-500">MST: {company.mst}</p>
        <p className="text-gray-500">
          Kỳ: {company.tu_ngay} → {company.den_ngay}
        </p>
      </div>

      {/* Health Score */}
      <div className="grid grid-cols-4 gap-4">
        <ScoreCard
          title="Health Score"
          value={`${healthScore}%`}
          color={healthScore > 80 ? 'green' : healthScore > 50 ? 'yellow' : 'red'}
        />
        <ScoreCard
          title="Đối chiếu đúng"
          value={`${validation.passed}/${validation.total_checks}`}
          color="blue"
        />
        <ScoreCard
          title="Cảnh báo"
          value={riskCount.high + riskCount.critical}
          color="red"
        />
        <ScoreCard
          title="Chỉ số TC"
          value={ratios.length}
          color="purple"
        />
      </div>

      {/* Quick Summary panels... */}
    </div>
  );
}
```

---

## 5. Quy trình triển khai (Step by step)

### Phase 1: Core Parser + Validator (1-2 tuần)

```bash
# 1. Khởi tạo project
mkdir bctc-analyzer && cd bctc-analyzer
mkdir -p backend/{parser,validator,analyzer,reporter,api,models,tests/fixtures}

# 2. Setup Python
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install fastapi uvicorn lxml defusedxml pydantic python-multipart

# 3. Code theo thứ tự:
#    a) models/base.py          → Pydantic models
#    b) parser/xml_parser.py    → Parse XML
#    c) parser/tt133_mapper.py  → Mapping chỉ tiêu
#    d) validator/cross_check.py → Đối chiếu chéo
#    e) main.py                 → API endpoint

# 4. Test với file XML mẫu
python -c "
from parser.xml_parser import HtkkXmlParser
p = HtkkXmlParser('tests/fixtures/sample.xml')
data = p.parse_all()
print(data['company'])
"

# 5. Chạy API
uvicorn main:app --reload --port 8000
# Test: curl -X POST http://localhost:8000/api/upload -F file=@sample.xml
```

### Phase 2: Analyzer modules (1-2 tuần)

```bash
# Thêm các analyzer:
#    a) analyzer/journal_reconstructor.py
#    b) analyzer/anomaly_detector.py
#    c) analyzer/ratio_analyzer.py
#    d) Tích hợp vào main.py
```

### Phase 3: Frontend (1-2 tuần)

```bash
# 1. Khởi tạo React
cd .. && npm create vite@latest frontend -- --template react
cd frontend
npm install recharts axios lucide-react
npm install -D tailwindcss @tailwindcss/vite

# 2. Build pages:
#    a) Upload.jsx     → drag & drop file
#    b) Dashboard.jsx  → tổng quan
#    c) CrossCheck.jsx → bảng đối chiếu
#    d) Các tab còn lại

# 3. Chạy dev
npm run dev
```

### Phase 4: Export & Polish (1 tuần)

```bash
pip install openpyxl reportlab
# Build reporter/pdf_report.py
# Build reporter/excel_report.py
# Polish UI, error handling, edge cases
```

---

## 6. Mở rộng tương lai

| Feature | Mô tả | Độ phức tạp |
|---------|--------|-------------|
| So sánh đa năm | Upload nhiều file XML → trend analysis | Trung bình |
| TT200 support | Mở rộng parser cho DN lớn (TT200) | Trung bình |
| So sánh ngành | Benchmark chỉ số TC theo mã ngành | Cao |
| OCR hoá đơn | Đọc hoá đơn → đối chiếu với sổ kế toán | Cao |
| AI Assistant | Tích hợp Claude API để hỏi đáp về BCTC | Thấp |
| MISA import | Đọc file MISA .mdb/.accdb → phân tích | Trung bình |
| Multi-user | Thêm auth, lưu history theo user | Trung bình |
| PP gián tiếp | Hỗ trợ LCTT phương pháp gián tiếp | Thấp |

---

## 7. Lưu ý kỹ thuật

### 7.1 Xử lý encoding

File XML từ HTKK dùng UTF-8 với BOM (`\xEF\xBB\xBF`) và line ending Windows (`\r\n`).
Parser cần handle:

```python
# Đọc file, bỏ BOM nếu có
with open(file_path, 'rb') as f:
    content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
```

### 7.2 Namespace XML

HTKK dùng namespace `http://kekhaithue.gdt.gov.vn/TKhaiThue`.
Tất cả XPath phải dùng prefix:

```python
NS = {"ns": "http://kekhaithue.gdt.gov.vn/TKhaiThue"}
root.find(".//ns:NNT", NS)  # ✅
root.find(".//NNT")          # ❌ Không tìm thấy
```

### 7.3 Số âm trong XML

Lỗ, giảm trừ, hao mòn được ghi dạng số âm trực tiếp: `-4042814`.
Parser cần xử lý `int()` cho cả số âm.

### 7.4 Phân biệt TT133 vs TT200

| Đặc điểm | TT133 | TT200 |
|-----------|-------|-------|
| Mã tờ khai | 684 | 405 |
| Đối tượng | DN nhỏ & vừa | DN lớn |
| Hệ thống TK | Đơn giản hơn | Đầy đủ hơn |
| TK 642 | Gộp CP BH + QLDN | Tách riêng 641, 642 |
| LCTT | Trực tiếp (phổ biến) | Cả 2 phương pháp |

### 7.5 Bảo mật

- Chạy 100% local, không gửi dữ liệu ra ngoài
- Xoá file tạm sau khi xử lý
- Dùng `defusedxml` thay `lxml` khi parse XML không tin cậy
  (phòng XXE attack nếu mở rộng cho nhiều user)

---

## 8. Tổng kết

Phần mềm này hoàn toàn khả thi với kiến trúc module rõ ràng. Mỗi module
có thể phát triển và test độc lập. Bắt đầu từ Parser → Validator →
Analyzer → Frontend theo từng phase. Toàn bộ chạy local, không phụ thuộc
cloud, phù hợp với tính chất bảo mật của dữ liệu tài chính doanh nghiệp.
