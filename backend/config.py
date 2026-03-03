"""
Cấu hình và hằng số cho BCTC Analyzer.
"""

from pathlib import Path

# ─── Thư mục gốc ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

# ─── Namespace XML HTKK ───────────────────────────────
HTKK_NAMESPACE = "http://kekhaithue.gdt.gov.vn/TKhaiThue"
NS = {"ns": HTKK_NAMESPACE}

# ─── Giới hạn file upload ─────────────────────────────
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ─── Định dạng file được hỗ trợ ───────────────────────
SUPPORTED_FILE_EXTENSIONS = {".xml"}

# ─── Mã tờ khai để nhận diện Thông tư ─────────────────
CIRCULAR_CODES = {
    "684": "TT133",   # Thông tư 133/2016/TT-BTC — DN nhỏ và vừa
    "405": "TT200",   # Thông tư 200/2014/TT-BTC — DN lớn
}

# ─── Loại thông tư được hỗ trợ ─────────────────────────
SUPPORTED_CIRCULARS = {"TT133", "TT200"}

# ─── Tên mẫu biểu theo thông tư ───────────────────────
REPORT_TEMPLATES = {
    "TT133": {
        "cdkt": "B01b-DNN",
        "kqhdkd": "B02-DNN",
        "lctt": "B03-DNN",
        "cdtk": "F01-DNN",
    },
    "TT200": {
        "cdkt": "B01-DN",
        "kqhdkd": "B02-DN",
        "lctt": "B03-DN",
        "cdtk": "F01-DN",
    },
}

# ─── Cấu hình phương pháp LCTT ────────────────────────
LCTT_METHODS = {
    "TT": "Phương pháp trực tiếp",
    "GT": "Phương pháp gián tiếp",
}

# ─── Ngưỡng cảnh báo phân tích ────────────────────────
THRESHOLDS = {
    "cash_heavy_ratio": 0.5,            # TK111 > 50% tổng TS
    "large_receivables_ratio": 0.7,     # Phải thu > 70% tổng TS
    "inventory_vs_revenue_ratio": 2.0,  # HTK > 2x DT
    "revenue_vs_cash_ratio": 0.5,       # Thu tiền < 50% DT
    "loss_vs_equity_ratio": 0.5,        # Lỗ > 50% vốn góp
    "related_party_threshold": 500_000_000,  # Công nợ khác > 500 triệu
    "vat_no_revenue_threshold": 100_000_000, # VAT đầu vào > 100 triệu mà chưa có DT
    "dormant_capital_threshold": 1_000_000_000,  # Vốn > 1 tỷ
    "dormant_expense_threshold": 50_000_000,     # CP QLDN < 50 triệu
}

# ─── Cấu hình API ─────────────────────────────────────
API_CONFIG = {
    "title": "BCTC Analyzer",
    "description": "Phân tích Báo cáo Tài chính từ file XML HTKK",
    "version": "1.0.0",
    "cors_origins": ["http://localhost:5173"],
}

# ─── Định dạng tiền tệ ────────────────────────────────
CURRENCY = "VNĐ"
CURRENCY_LOCALE = "vi_VN"

# ─── Encoding ─────────────────────────────────────────
DEFAULT_ENCODING = "utf-8"
BOM_BYTES = b"\xef\xbb\xbf"
