"""
PDF Reporter - Xuat bao cao BCTC ra file PDF chuyen nghiep.

Su dung reportlab de tao PDF voi:
  - Trang bia voi thong tin DN
  - Tong quan (health score)
  - Bang doi chieu cheo
  - Danh sach bat thuong (severity colors)
  - Bang chi so tai chinh
"""

import io
import os
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ─── Font Registration ──────────────────────────────────

_FONT_NAME = "Helvetica"
_FONT_NAME_BOLD = "Helvetica-Bold"

def _register_vietnamese_font():
    """
    Thu dang ky font ho tro tieng Viet.
    Tim cac font pho bien tren he thong.
    Fallback ve Helvetica neu khong tim thay.
    """
    global _FONT_NAME, _FONT_NAME_BOLD

    font_paths = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    # Try DejaVuSans first (best Unicode support)
    dejavu_paths = [p for p in font_paths if "DejaVu" in p]
    for path in dejavu_paths:
        if os.path.exists(path):
            try:
                if "Bold" in path:
                    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", path))
                else:
                    pdfmetrics.registerFont(TTFont("DejaVuSans", path))
            except Exception:
                continue

    # Check if DejaVuSans was registered
    try:
        pdfmetrics.getFont("DejaVuSans")
        _FONT_NAME = "DejaVuSans"
        try:
            pdfmetrics.getFont("DejaVuSans-Bold")
            _FONT_NAME_BOLD = "DejaVuSans-Bold"
        except KeyError:
            _FONT_NAME_BOLD = "DejaVuSans"
        return
    except KeyError:
        pass

    # Try Arial
    arial_paths = [p for p in font_paths if "arial" in p.lower()]
    for path in arial_paths:
        if os.path.exists(path):
            try:
                if "bd" in path.lower():
                    pdfmetrics.registerFont(TTFont("Arial-Bold", path))
                else:
                    pdfmetrics.registerFont(TTFont("Arial", path))
            except Exception:
                continue

    try:
        pdfmetrics.getFont("Arial")
        _FONT_NAME = "Arial"
        try:
            pdfmetrics.getFont("Arial-Bold")
            _FONT_NAME_BOLD = "Arial-Bold"
        except KeyError:
            _FONT_NAME_BOLD = "Arial"
        return
    except KeyError:
        pass

    # Fallback: Helvetica (always available)
    _FONT_NAME = "Helvetica"
    _FONT_NAME_BOLD = "Helvetica-Bold"


# Register fonts on module load
_register_vietnamese_font()


# ─── Color constants ────────────────────────────────────

_COLOR_PRIMARY = colors.HexColor("#2F5496")
_COLOR_SUCCESS = colors.HexColor("#00B050")
_COLOR_WARNING = colors.HexColor("#FFC000")
_COLOR_DANGER = colors.HexColor("#FF0000")
_COLOR_LIGHT_GRAY = colors.HexColor("#F2F2F2")
_COLOR_HEADER_BG = colors.HexColor("#2F5496")
_COLOR_HEADER_TEXT = colors.white

_SEVERITY_COLORS = {
    "ok": colors.HexColor("#C6EFCE"),
    "warning": colors.HexColor("#FFEB9C"),
    "error": colors.HexColor("#FFC7CE"),
    "critical": colors.HexColor("#FF4444"),
}

_RISK_COLORS = {
    "low": colors.HexColor("#C6EFCE"),
    "medium": colors.HexColor("#FFEB9C"),
    "high": colors.HexColor("#FFC7CE"),
    "critical": colors.HexColor("#FF4444"),
}


class PdfReporter:
    """Tao bao cao PDF tu ket qua phan tich BCTC."""

    def __init__(self, analysis_data: Dict[str, Any]):
        self.data = analysis_data
        self.company = analysis_data.get("company", {})
        self.validation = analysis_data.get("validation", {})
        self.anomalies = analysis_data.get("anomalies", [])
        self.ratios = analysis_data.get("ratios", [])
        self.journals = analysis_data.get("journals", [])
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Tao cac style tuy chinh."""
        self.styles.add(ParagraphStyle(
            name="CustomTitle",
            fontName=_FONT_NAME_BOLD,
            fontSize=20,
            textColor=_COLOR_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=6 * mm,
        ))
        self.styles.add(ParagraphStyle(
            name="CustomHeading",
            fontName=_FONT_NAME_BOLD,
            fontSize=14,
            textColor=_COLOR_PRIMARY,
            spaceBefore=8 * mm,
            spaceAfter=4 * mm,
        ))
        self.styles.add(ParagraphStyle(
            name="CustomSubHeading",
            fontName=_FONT_NAME_BOLD,
            fontSize=11,
            textColor=colors.HexColor("#333333"),
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        ))
        self.styles.add(ParagraphStyle(
            name="CustomBody",
            fontName=_FONT_NAME,
            fontSize=9,
            leading=14,
            spaceAfter=2 * mm,
        ))
        self.styles.add(ParagraphStyle(
            name="CustomBodySmall",
            fontName=_FONT_NAME,
            fontSize=8,
            leading=11,
        ))
        self.styles.add(ParagraphStyle(
            name="CustomCenter",
            fontName=_FONT_NAME,
            fontSize=10,
            alignment=TA_CENTER,
        ))

    def generate(self) -> io.BytesIO:
        """Tao PDF va tra ve BytesIO stream."""
        output = io.BytesIO()

        doc = SimpleDocTemplate(
            output,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
        )

        elements = []

        # 1. Trang bia
        elements.extend(self._build_title_page())
        elements.append(PageBreak())

        # 2. Tong quan
        elements.extend(self._build_summary_section())
        elements.append(Spacer(1, 8 * mm))

        # 3. Doi chieu cheo
        elements.extend(self._build_crosscheck_section())
        elements.append(PageBreak())

        # 4. Bat thuong
        elements.extend(self._build_anomaly_section())

        # 5. Chi so tai chinh
        if self.ratios:
            elements.append(PageBreak())
            elements.extend(self._build_ratio_section())

        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        output.seek(0)
        return output

    # ─── Title Page ──────────────────────────────────────

    def _build_title_page(self) -> list:
        elements = []

        elements.append(Spacer(1, 40 * mm))

        elements.append(Paragraph(
            "BAO CAO PHAN TICH", self.styles["CustomTitle"]
        ))
        elements.append(Paragraph(
            "BAO CAO TAI CHINH", self.styles["CustomTitle"]
        ))

        elements.append(Spacer(1, 15 * mm))
        elements.append(HRFlowable(
            width="80%", thickness=2, color=_COLOR_PRIMARY,
            spaceAfter=10 * mm, spaceBefore=5 * mm,
        ))

        # Company info
        company_info = [
            ("Doanh nghiep:", self.company.get("ten_dn", "N/A")),
            ("Ma so thue:", self.company.get("mst", "N/A")),
            ("Dia chi:", self.company.get("dia_chi", "N/A")),
            ("Ky bao cao:", f"{self.company.get('tu_ngay', '')} - {self.company.get('den_ngay', '')}"),
            ("Thong tu:", self.data.get("circular", "N/A")),
        ]

        for label, value in company_info:
            text = f"<b>{label}</b> {value}"
            elements.append(Paragraph(text, self.styles["CustomBody"]))
            elements.append(Spacer(1, 2 * mm))

        elements.append(Spacer(1, 20 * mm))

        # Health Score
        total_checks = self.validation.get("total_checks", 0)
        passed = self.validation.get("passed", 0)
        health = round((passed / total_checks * 100)) if total_checks > 0 else 0

        if health > 80:
            score_color = "#00B050"
            rating = "TOT"
        elif health > 50:
            score_color = "#FFC000"
            rating = "TRUNG BINH"
        else:
            score_color = "#FF0000"
            rating = "CAN CAI THIEN"

        elements.append(Paragraph(
            f'<font color="{score_color}" size="24"><b>Health Score: {health}%</b></font>',
            ParagraphStyle(name="Score", alignment=TA_CENTER, fontName=_FONT_NAME_BOLD)
        ))
        elements.append(Paragraph(
            f'<font color="{score_color}" size="14">{rating}</font>',
            ParagraphStyle(name="Rating", alignment=TA_CENTER, fontName=_FONT_NAME)
        ))

        return elements

    # ─── Summary Section ─────────────────────────────────

    def _build_summary_section(self) -> list:
        elements = []

        elements.append(Paragraph("TONG QUAN", self.styles["CustomHeading"]))

        total = self.validation.get("total_checks", 0)
        passed = self.validation.get("passed", 0)
        warnings = self.validation.get("warnings", 0)
        errors = self.validation.get("errors", 0)

        summary_data = [
            ["Chi tieu", "Gia tri"],
            ["Tong so kiem tra doi chieu", str(total)],
            ["So kiem tra dat", str(passed)],
            ["So canh bao", str(warnings)],
            ["So loi", str(errors)],
            ["So bat thuong phat hien", str(len(self.anomalies))],
            ["So chi so tai chinh", str(len(self.ratios))],
            ["So but toan tai tao", str(len(self.journals))],
        ]

        table = Table(summary_data, colWidths=[120 * mm, 50 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _COLOR_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), _COLOR_HEADER_TEXT),
            ("FONTNAME", (0, 0), (-1, 0), _FONT_NAME_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), _FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _COLOR_LIGHT_GRAY]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        elements.append(table)
        return elements

    # ─── Cross-check Section ─────────────────────────────

    def _build_crosscheck_section(self) -> list:
        elements = []

        elements.append(Paragraph("KET QUA DOI CHIEU CHEO", self.styles["CustomHeading"]))

        details = self.validation.get("details", [])
        if not details:
            elements.append(Paragraph(
                "Khong co du lieu doi chieu.", self.styles["CustomBody"]
            ))
            return elements

        # Build table
        header = ["Ma", "Ten quy tac", "KQ", "Mo ta"]
        data = [header]

        for d in details:
            severity = d.get("severity", "")
            if severity == "ok":
                result = "DAT"
            elif severity == "warning":
                result = "CB"
            else:
                result = "LOI"

            data.append([
                d.get("rule_id", ""),
                Paragraph(d.get("rule_name", ""), self.styles["CustomBodySmall"]),
                result,
                Paragraph(d.get("message", ""), self.styles["CustomBodySmall"]),
            ])

        col_widths = [25 * mm, 55 * mm, 15 * mm, 85 * mm]
        table = Table(data, colWidths=col_widths, repeatRows=1)

        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), _COLOR_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), _COLOR_HEADER_TEXT),
            ("FONTNAME", (0, 0), (-1, 0), _FONT_NAME_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), _FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]

        # Color-code result cells
        for idx, d in enumerate(details, start=1):
            severity = d.get("severity", "")
            bg_color = _SEVERITY_COLORS.get(severity, colors.white)
            style_commands.append(("BACKGROUND", (2, idx), (2, idx), bg_color))

        table.setStyle(TableStyle(style_commands))
        elements.append(table)

        return elements

    # ─── Anomaly Section ─────────────────────────────────

    def _build_anomaly_section(self) -> list:
        elements = []

        elements.append(Paragraph("BAT THUONG VA RUI RO", self.styles["CustomHeading"]))

        if not self.anomalies:
            elements.append(Paragraph(
                "Khong phat hien bat thuong nao. Bao cao tai chinh co ve hop ly.",
                self.styles["CustomBody"],
            ))
            return elements

        elements.append(Paragraph(
            f"Phat hien {len(self.anomalies)} bat thuong:",
            self.styles["CustomBody"],
        ))
        elements.append(Spacer(1, 3 * mm))

        for anomaly in self.anomalies:
            risk_level = anomaly.get("risk_level", "medium")
            risk_color = {
                "critical": "#FF0000",
                "high": "#FF6347",
                "medium": "#FFA500",
                "low": "#32CD32",
            }.get(risk_level, "#FFA500")

            # Title with risk badge
            title_text = (
                f'<font color="{risk_color}"><b>[{risk_level.upper()}]</b></font> '
                f'<b>{anomaly.get("title", "")}</b>'
            )
            elements.append(Paragraph(title_text, self.styles["CustomSubHeading"]))

            # Description
            elements.append(Paragraph(
                anomaly.get("description", ""), self.styles["CustomBody"]
            ))

            # Suggestion
            suggestion = anomaly.get("suggestion", "")
            if suggestion:
                elements.append(Paragraph(
                    f'<i>De xuat: {suggestion}</i>', self.styles["CustomBody"]
                ))

            elements.append(Spacer(1, 3 * mm))
            elements.append(HRFlowable(
                width="100%", thickness=0.5, color=colors.lightgrey,
                spaceAfter=3 * mm,
            ))

        return elements

    # ─── Ratio Section ───────────────────────────────────

    def _build_ratio_section(self) -> list:
        elements = []

        elements.append(Paragraph("CHI SO TAI CHINH", self.styles["CustomHeading"]))

        # Group by category
        categories = {
            "liquidity": "Kha nang thanh toan",
            "profitability": "Kha nang sinh loi",
            "leverage": "Co cau von",
            "efficiency": "Hieu qua hoat dong",
        }

        current_category = None
        header = ["Chi so", "Gia tri", "Don vi", "Nguong", "Nhan xet"]
        data = [header]
        cat_rows = []  # Track category header rows

        for ratio in self.ratios:
            cat = ratio.get("category", "")
            if cat != current_category:
                current_category = cat
                cat_name = categories.get(cat, cat).upper()
                data.append([cat_name, "", "", "", ""])
                cat_rows.append(len(data) - 1)

            value = ratio.get("value")
            value_str = f"{value:.2f}" if value is not None else "N/A"

            data.append([
                Paragraph(
                    f'{ratio.get("name", "")}<br/><font size="7" color="gray">'
                    f'{ratio.get("name_en", "")}</font>',
                    self.styles["CustomBodySmall"],
                ),
                value_str,
                ratio.get("unit", ""),
                Paragraph(ratio.get("benchmark", ""), self.styles["CustomBodySmall"]),
                Paragraph(ratio.get("interpretation", ""), self.styles["CustomBodySmall"]),
            ])

        col_widths = [40 * mm, 18 * mm, 12 * mm, 45 * mm, 55 * mm]
        table = Table(data, colWidths=col_widths, repeatRows=1)

        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), _COLOR_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), _COLOR_HEADER_TEXT),
            ("FONTNAME", (0, 0), (-1, 0), _FONT_NAME_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), _FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (2, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]

        # Style category header rows
        for cat_row in cat_rows:
            style_commands.extend([
                ("BACKGROUND", (0, cat_row), (-1, cat_row), colors.HexColor("#D6E4F0")),
                ("FONTNAME", (0, cat_row), (-1, cat_row), _FONT_NAME_BOLD),
                ("SPAN", (0, cat_row), (-1, cat_row)),
            ])

        table.setStyle(TableStyle(style_commands))
        elements.append(table)

        return elements

    # ─── Footer ──────────────────────────────────────────

    @staticmethod
    def _add_footer(canvas, doc):
        """Them header/footer cho moi trang."""
        canvas.saveState()

        # Footer
        canvas.setFont(_FONT_NAME, 7)
        canvas.setFillColor(colors.gray)
        canvas.drawString(
            15 * mm, 10 * mm,
            f"BCTC Analyzer - Bao cao phan tich tu dong"
        )
        canvas.drawRightString(
            A4[0] - 15 * mm, 10 * mm,
            f"Trang {canvas.getPageNumber()}"
        )

        # Header line
        canvas.setStrokeColor(_COLOR_PRIMARY)
        canvas.setLineWidth(0.5)
        canvas.line(15 * mm, A4[1] - 15 * mm, A4[0] - 15 * mm, A4[1] - 15 * mm)

        canvas.restoreState()
