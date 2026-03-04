"""
Sửa XML HTKK gốc theo danh sách corrections rồi xuất ra bytes.

Giữ nguyên BOM, namespace, encoding, cấu trúc gốc.
Chỉ cập nhật text content của các element ct.
"""

from lxml import etree
from typing import Dict, List, Any

try:
    from ..config import NS, BOM_BYTES, HTKK_NAMESPACE
except ImportError:
    from config import NS, BOM_BYTES, HTKK_NAMESPACE


# Mapping section -> XPath parent element
_SECTION_XPATH = {
    # CĐKT
    "cdkt.so_cuoi_nam": ".//ns:CTieuTKhaiChinh/ns:SoCuoiNam",
    "cdkt.so_dau_nam": ".//ns:CTieuTKhaiChinh/ns:SoDauNam",
    # KQHĐKD
    "kqhdkd.nam_nay": ".//ns:PL_KQHDSXKD/ns:NamNay",
    "kqhdkd.nam_truoc": ".//ns:PL_KQHDSXKD/ns:NamTruoc",
    # LCTT trực tiếp
    "lctt.nam_nay": ".//ns:PL_LCTTTT/ns:NamNay",
    "lctt.nam_truoc": ".//ns:PL_LCTTTT/ns:NamTruoc",
}

# LCTT gián tiếp (fallback)
_LCTT_GT_XPATH = {
    "lctt.nam_nay": ".//ns:PL_LCTTGT/ns:NamNay",
    "lctt.nam_truoc": ".//ns:PL_LCTTGT/ns:NamTruoc",
}


class HtkkXmlWriter:
    """
    Sửa XML HTKK gốc theo dict corrections.

    Usage:
        writer = HtkkXmlWriter(xml_bytes)
        writer.apply_corrections(corrections)
        output = writer.to_bytes()
    """

    def __init__(self, xml_bytes: bytes):
        self.had_bom = xml_bytes.startswith(BOM_BYTES)
        raw = xml_bytes[3:] if self.had_bom else xml_bytes
        self.root = etree.fromstring(raw)
        self.ns = NS

    def apply_corrections(self, corrections: List[Dict[str, Any]]) -> int:
        """
        Áp dụng danh sách corrections vào XML tree.

        Args:
            corrections: list of dicts with keys: report, section, code, new_value

        Returns:
            Số lượng corrections đã áp dụng thành công.
        """
        applied = 0
        for corr in corrections:
            report = corr["report"]
            section = corr["section"]
            code = corr["code"]
            new_value = corr["new_value"]

            section_key = f"{report}.{section}"
            parent = self._find_section(section_key)
            if parent is None:
                continue

            # Tìm element ct trong parent
            el = parent.find(f"ns:{code}", self.ns)
            if el is not None:
                el.text = self._format_value(new_value)
                applied += 1
            else:
                # Tạo element mới nếu chưa tồn tại
                new_el = etree.SubElement(
                    parent,
                    f"{{{HTKK_NAMESPACE}}}{code}"
                )
                new_el.text = self._format_value(new_value)
                applied += 1

        return applied

    def to_bytes(self) -> bytes:
        """Xuất XML đã sửa ra bytes, giữ BOM nếu file gốc có."""
        xml_bytes = etree.tostring(
            self.root,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=False,
        )
        if self.had_bom:
            xml_bytes = BOM_BYTES + xml_bytes
        return xml_bytes

    def _find_section(self, section_key: str):
        """Tìm parent element cho section."""
        # Thử XPath chính
        xpath = _SECTION_XPATH.get(section_key)
        if xpath:
            el = self.root.find(xpath, self.ns)
            if el is not None:
                return el

        # Fallback cho LCTT gián tiếp
        xpath_gt = _LCTT_GT_XPATH.get(section_key)
        if xpath_gt:
            return self.root.find(xpath_gt, self.ns)

        return None

    @staticmethod
    def _format_value(value) -> str:
        """Format giá trị cho XML text."""
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)
