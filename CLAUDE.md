# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BCTC Analyzer is a local-only tool that parses HTKK-exported XML files (Vietnamese tax software) to analyze financial statements. It cross-checks 4 reports (CĐKT, KQHĐKD, LCTT, CĐTK), detects anomalies, reconstructs journal entries, and computes financial ratios. Supports both Thông tư 133 (SMEs, mã tờ khai 684) and Thông tư 200 (large enterprises, mã tờ khai 405).

The full technical specification is in `BCTC_ANALYZER_SPEC.md`.

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI, Pydantic v2, lxml + defusedxml, openpyxl, reportlab
- **Frontend:** React + Vite + Tailwind CSS + Recharts
- **Database:** SQLite (optional, for history)

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                     # dev server at localhost:5173
```

### Testing
```bash
cd backend
pytest                          # all tests
pytest tests/test_parser.py     # single module
pytest tests/test_parser.py::test_function_name  # single test
```

## Architecture

```
POST /api/upload (XML file)
  → Parser → Validator → Analyzer → JSON response
```

### Backend Modules (`backend/`)

- **parser/** — Reads HTKK XML into structured Python dicts. `xml_parser.py` is the core; `tt133_mapper.py` and `tt200_mapper.py` map `ct` codes to Vietnamese financial line item names; `detector.py` auto-detects TT133 vs TT200.
- **validator/** — Cross-checks between the 4 reports. `cross_check.py` runs ~15 rules (CDKT_01–07, KQHDKD_01–06, LCTT_01–05, CROSS_01–05). Returns `CheckResult` with severity levels (ok/warning/error/critical).
- **analyzer/** — `journal_reconstructor.py` rebuilds accounting entries from CĐTK debit/credit movements using common account pairs. `anomaly_detector.py` flags red flags (cash-heavy, negative equity, dormant company, VAT anomalies, etc.). `ratio_analyzer.py` computes liquidity/profitability/leverage/efficiency ratios.
- **reporter/** — PDF and Excel export via reportlab and openpyxl.
- **models/** — Pydantic v2 models for each report type (CĐKT, KQHĐKD, LCTT, CĐTK).
- **api/** — FastAPI routes. Main endpoint is `POST /api/upload` (all-in-one parse+validate+analyze).

### Frontend Pages (`frontend/src/`)

Upload → Dashboard (health score, company info) → Tabs: CrossCheck, JournalView, Anomalies, Ratios.

## Key Technical Details

- **XML Namespace:** All XPath queries must use `NS = {"ns": "http://kekhaithue.gdt.gov.vn/TKhaiThue"}`. Bare XPath without namespace prefix will silently return nothing.
- **Encoding:** HTKK XML uses UTF-8 with BOM (`\xEF\xBB\xBF`) and Windows line endings. Strip BOM before parsing.
- **Negative numbers:** Losses, depreciation, deductions are negative integers in XML (e.g., `-4042814`). Parser must handle negative `int()`.
- **`ct` code convention:** XML tags like `ct100`, `ct110`, `ct01` map to Vietnamese financial statement line items (mã số). The mapper dicts in `tt133_mapper.py` / `tt200_mapper.py` translate these to human-readable names.
- **TT133 vs TT200 differences:** TT133 merges selling & admin expenses into TK 642; TT200 splits them into TK 641 + 642. TT133 primarily uses direct cash flow method.

## Language

All user-facing text (labels, messages, suggestions) is in Vietnamese. Code comments and docstrings are also in Vietnamese. Variable names use Vietnamese abbreviations (e.g., `cdkt` = Cân đối kế toán, `kqhdkd` = Kết quả hoạt động kinh doanh, `lctt` = Lưu chuyển tiền tệ, `cdtk` = Cân đối tài khoản).
