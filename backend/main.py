"""
FastAPI entrypoint cho BCTC Analyzer.
All-in-one: upload XML -> parse -> validate -> analyze -> return JSON.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os

from parser.xml_parser import HtkkXmlParser
from parser.tt133_mapper import CDTK_ACCOUNT_MAP
from parser.tt200_mapper import CDTK_ACCOUNT_MAP as CDTK_ACCOUNT_MAP_TT200
from validator.cross_check import CrossChecker
from analyzer.journal_reconstructor import JournalReconstructor
from analyzer.anomaly_detector import AnomalyDetector
from analyzer.ratio_analyzer import RatioAnalyzer

app = FastAPI(
    title="BCTC Analyzer",
    description="Phân tích Báo cáo Tài chính từ file XML HTKK",
    version="1.0.0",
)

_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
_origins += [
    "http://localhost:5173",
    "https://bctc.xn--m-phng-6zb4190dsfa.vn",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include additional routes
from api.routes import router as api_router

app.include_router(api_router)


@app.post("/api/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload file XML -> parse -> validate -> analyze -> tra JSON.
    Day la endpoint chinh, xu ly all-in-one.
    """
    if not file.filename.endswith(".xml"):
        raise HTTPException(400, "Chi chap nhan file .xml")

    # Luu file tam
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

        # Auto-detect TT133/TT200 and use appropriate mapper
        circular = data.get("circular", "TT133")
        if circular == "TT200":
            account_map = CDTK_ACCOUNT_MAP_TT200
        else:
            account_map = CDTK_ACCOUNT_MAP

        # 2. Validate (doi chieu cheo)
        checker = CrossChecker(data)
        check_results = checker.run_all()

        # 3. Tai tao but toan
        reconstructor = JournalReconstructor(
            data["cdtk"], account_map
        )
        journals = reconstructor.reconstruct()

        # 4. Phat hien bat thuong
        detector = AnomalyDetector(data)
        anomalies = detector.detect_all()

        # 5. Chi so tai chinh
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

    except ValueError as e:
        raise HTTPException(400, f"Loi du lieu: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Loi xu ly file: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
