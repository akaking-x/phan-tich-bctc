"""
Additional API routes cho BCTC Analyzer.
- Export Excel / PDF
- Compare 2 file XML (year-over-year)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import tempfile
import os
import io
from typing import Optional

from parser.xml_parser import HtkkXmlParser
from parser.tt133_mapper import CDKT_MAP, KQHDKD_MAP, CDTK_ACCOUNT_MAP
from parser.tt200_mapper import CDTK_ACCOUNT_MAP as CDTK_ACCOUNT_MAP_TT200
from validator.cross_check import CrossChecker
from analyzer.journal_reconstructor import JournalReconstructor
from analyzer.anomaly_detector import AnomalyDetector
from analyzer.ratio_analyzer import RatioAnalyzer
from reporter.excel_report import ExcelReporter
from reporter.pdf_report import PdfReporter
from api.schemas import ExportRequest

router = APIRouter()


def _run_full_analysis(data: dict) -> dict:
    """Chay toan bo pipeline phan tich tren du lieu da parse."""
    circular = data.get("circular", "TT133")
    if circular == "TT200":
        account_map = CDTK_ACCOUNT_MAP_TT200
    else:
        account_map = CDTK_ACCOUNT_MAP

    checker = CrossChecker(data)
    check_results = checker.run_all()

    reconstructor = JournalReconstructor(data["cdtk"], account_map)
    journals = reconstructor.reconstruct()

    detector = AnomalyDetector(data)
    anomalies = detector.detect_all()

    ratio_analyzer = RatioAnalyzer(data)
    ratios = ratio_analyzer.analyze()

    return {
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
            "passed": sum(1 for r in check_results if r.severity.value == "ok"),
            "warnings": sum(1 for r in check_results if r.severity.value == "warning"),
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
    }


@router.post("/api/export/excel")
async def export_excel(file: UploadFile = File(...)):
    """
    Upload file XML -> phan tich -> xuat Excel.
    Tra ve file .xlsx download truc tiep.
    """
    if not file.filename.endswith(".xml"):
        raise HTTPException(400, "Chi chap nhan file .xml")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parser = HtkkXmlParser(tmp_path)
        data = parser.parse_all()
        analysis = _run_full_analysis(data)

        reporter = ExcelReporter(analysis)
        output = reporter.generate()

        filename = f"BCTC_{analysis['company'].get('mst', 'export')}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except ValueError as e:
        raise HTTPException(400, f"Loi du lieu: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Loi xuat Excel: {str(e)}")
    finally:
        os.unlink(tmp_path)


@router.post("/api/export/pdf")
async def export_pdf(file: UploadFile = File(...)):
    """
    Upload file XML -> phan tich -> xuat PDF.
    Tra ve file .pdf download truc tiep.
    """
    if not file.filename.endswith(".xml"):
        raise HTTPException(400, "Chi chap nhan file .xml")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parser = HtkkXmlParser(tmp_path)
        data = parser.parse_all()
        analysis = _run_full_analysis(data)

        reporter = PdfReporter(analysis)
        output = reporter.generate()

        filename = f"BCTC_{analysis['company'].get('mst', 'export')}.pdf"
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except ValueError as e:
        raise HTTPException(400, f"Loi du lieu: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Loi xuat PDF: {str(e)}")
    finally:
        os.unlink(tmp_path)


@router.post("/api/compare")
async def compare_files(
    file1: UploadFile = File(..., description="File XML ky truoc"),
    file2: UploadFile = File(..., description="File XML ky sau"),
):
    """
    So sanh 2 file XML (year-over-year).
    Upload 2 file -> parse -> phan tich -> so sanh -> tra JSON.
    """
    for f in [file1, file2]:
        if not f.filename.endswith(".xml"):
            raise HTTPException(400, f"File '{f.filename}' khong phai .xml")

    tmp_paths = []
    try:
        # Luu 2 file tam
        for f in [file1, file2]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
                content = await f.read()
                tmp.write(content)
                tmp_paths.append(tmp.name)

        # Parse ca 2
        parser1 = HtkkXmlParser(tmp_paths[0])
        data1 = parser1.parse_all()
        analysis1 = _run_full_analysis(data1)

        parser2 = HtkkXmlParser(tmp_paths[1])
        data2 = parser2.parse_all()
        analysis2 = _run_full_analysis(data2)

        # So sanh CDKT
        cdkt_comparison = _compare_report(
            data1["cdkt"].get("so_cuoi_nam", {}),
            data2["cdkt"].get("so_cuoi_nam", {}),
            CDKT_MAP,
        )

        # So sanh KQHDKD
        kqhdkd_comparison = _compare_report(
            data1["kqhdkd"].get("nam_nay", {}),
            data2["kqhdkd"].get("nam_nay", {}),
            KQHDKD_MAP,
        )

        # So sanh chi so tai chinh
        ratio_comparison = _compare_ratios(
            analysis1.get("ratios", []),
            analysis2.get("ratios", []),
        )

        return {
            "success": True,
            "company_year1": data1["company"],
            "company_year2": data2["company"],
            "cdkt_comparison": cdkt_comparison,
            "kqhdkd_comparison": kqhdkd_comparison,
            "ratio_comparison": ratio_comparison,
            "analysis_year1": analysis1,
            "analysis_year2": analysis2,
        }

    except ValueError as e:
        raise HTTPException(400, f"Loi du lieu: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Loi so sanh: {str(e)}")
    finally:
        for p in tmp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass


def _compare_report(
    data_year1: dict, data_year2: dict, name_map: dict
) -> list:
    """So sanh tung chi tieu giua 2 ky."""
    all_keys = sorted(
        set(list(data_year1.keys()) + list(data_year2.keys()))
    )
    results = []

    for key in all_keys:
        v1 = data_year1.get(key)
        v2 = data_year2.get(key)

        # Chi so sanh gia tri so
        v1_num = float(v1) if v1 is not None and isinstance(v1, (int, float)) else None
        v2_num = float(v2) if v2 is not None and isinstance(v2, (int, float)) else None

        change = None
        change_pct = None
        if v1_num is not None and v2_num is not None:
            change = v2_num - v1_num
            if v1_num != 0:
                change_pct = round((change / abs(v1_num)) * 100, 2)

        info = name_map.get(key, {})
        results.append({
            "code": key,
            "name": info.get("name", key),
            "value_year1": v1_num,
            "value_year2": v2_num,
            "change": change,
            "change_pct": change_pct,
        })

    return results


def _compare_ratios(ratios_year1: list, ratios_year2: list) -> list:
    """So sanh chi so tai chinh giua 2 ky."""
    r1_map = {r["code"]: r for r in ratios_year1}
    r2_map = {r["code"]: r for r in ratios_year2}

    all_codes = sorted(set(list(r1_map.keys()) + list(r2_map.keys())))
    results = []

    for code in all_codes:
        r1 = r1_map.get(code, {})
        r2 = r2_map.get(code, {})

        v1 = r1.get("value")
        v2 = r2.get("value")
        change = None
        if v1 is not None and v2 is not None:
            change = round(v2 - v1, 4)

        results.append({
            "code": code,
            "name": r1.get("name", r2.get("name", "")),
            "name_en": r1.get("name_en", r2.get("name_en", "")),
            "value_year1": v1,
            "value_year2": v2,
            "change": change,
            "unit": r1.get("unit", r2.get("unit", "")),
            "category": r1.get("category", r2.get("category", "")),
        })

    return results
