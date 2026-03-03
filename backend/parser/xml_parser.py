"""
Core XML Parser cho file BCTC xuất từ HTKK.
Hỗ trợ Thông tư 133/2016 (mã tờ khai 684) và Thông tư 200/2014 (mã tờ khai 405).

Xử lý:
- UTF-8 BOM (\\xEF\\xBB\\xBF)
- Namespace HTKK: http://kekhaithue.gdt.gov.vn/TKhaiThue
- Số âm (lỗ, hao mòn, giảm trừ)
- Dữ liệu thiếu / None
"""

from lxml import etree
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from ..config import NS, BOM_BYTES
except ImportError:
    from config import NS, BOM_BYTES

# Namespace trong XML HTKK
_NS = NS


class HtkkXmlParser:
    """
    Parse file XML BCTC xuất từ HTKK.
    Hỗ trợ TT133 (mã tờ khai 684) và TT200 (mã tờ khai 405).
    """

    def __init__(self, file_path: str):
        """
        Khởi tạo parser với đường dẫn file XML.

        Args:
            file_path: Đường dẫn tới file XML HTKK.

        Raises:
            FileNotFoundError: Nếu file không tồn tại.
            etree.XMLSyntaxError: Nếu XML không hợp lệ.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file XML: {self.file_path}"
            )

        self.ns = _NS
        self._parse_file()

    def _parse_file(self):
        """Đọc và parse file XML, xử lý BOM nếu có."""
        with open(self.file_path, "rb") as f:
            content = f.read()

        # Bỏ UTF-8 BOM nếu có
        if content.startswith(BOM_BYTES):
            content = content[3:]

        try:
            self.root = etree.fromstring(content)
        except etree.XMLSyntaxError as e:
            raise etree.XMLSyntaxError(
                f"File XML không hợp lệ: {e}"
            )

    # ─── Thông tin chung ──────────────────────────────────

    def get_company_info(self) -> Dict[str, str]:
        """
        Trích xuất thông tin doanh nghiệp từ phần TTinChung.

        Returns:
            Dict chứa MST, tên DN, địa chỉ, kỳ báo cáo, v.v.
        """
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
        """
        Nhận diện Thông tư: TT133 hay TT200 dựa trên mã tờ khai.

        Returns:
            "TT133" hoặc "TT200"

        Raises:
            ValueError: Nếu mã tờ khai không nhận diện được.
        """
        tkhai = self.root.find(".//ns:TKhaiThue", self.ns)
        ma = self._text(tkhai, "ns:maTKhai")

        if ma == "684":
            return "TT133"
        elif ma == "405":
            return "TT200"
        else:
            raise ValueError(
                f"Mã tờ khai không nhận diện được: '{ma}'. "
                f"Chỉ hỗ trợ 684 (TT133) và 405 (TT200)."
            )

    # ─── Bảng Cân đối Kế toán ────────────────────────────

    def parse_cdkt(self) -> Dict[str, Any]:
        """
        Parse Bảng Cân đối kế toán (nằm trong CTieuTKhaiChinh).

        Returns:
            Dict chứa thuyet_minh, so_cuoi_nam, so_dau_nam.
            Trả về dict rỗng nếu không tìm thấy.
        """
        main = self.root.find(".//ns:CTieuTKhaiChinh", self.ns)
        if main is None:
            return {
                "thuyet_minh": {},
                "so_cuoi_nam": {},
                "so_dau_nam": {},
            }

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
        """
        Parse Báo cáo Kết quả hoạt động kinh doanh.

        Returns:
            Dict chứa thuyet_minh, nam_nay, nam_truoc.
            Trả về dict rỗng nếu không tìm thấy phụ lục.
        """
        pl = self.root.find(".//ns:PL_KQHDSXKD", self.ns)
        if pl is None:
            return {
                "thuyet_minh": {},
                "nam_nay": {},
                "nam_truoc": {},
            }

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
        """
        Parse Báo cáo Lưu chuyển tiền tệ.
        Ưu tiên phương pháp trực tiếp (PL_LCTTTT),
        nếu không có thì thử gián tiếp (PL_LCTTGT).

        Returns:
            Dict chứa thuyet_minh, nam_nay, nam_truoc.
            Trả về dict rỗng nếu không tìm thấy phụ lục.
        """
        # Thử phương pháp trực tiếp trước
        pl = self.root.find(".//ns:PL_LCTTTT", self.ns)
        if pl is None:
            # Thử phương pháp gián tiếp
            pl = self.root.find(".//ns:PL_LCTTGT", self.ns)
        if pl is None:
            return {
                "thuyet_minh": {},
                "nam_nay": {},
                "nam_truoc": {},
            }

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
        """
        Parse Bảng Cân đối tài khoản (Nợ/Có cho từng TK).

        Returns:
            Dict chứa SoDuDauKy, SoPhatSinhTrongKy, SoDuCuoiKy.
            Mỗi phần có dict "no" và "co".
            Trả về dict rỗng nếu không tìm thấy phụ lục.
        """
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

    # ─── All-in-one ───────────────────────────────────────

    def parse_all(self) -> Dict[str, Any]:
        """
        Parse toàn bộ BCTC thành 1 dict lớn.

        Returns:
            Dict chứa company, circular, cdkt, kqhdkd, lctt, cdtk.
        """
        return {
            "company": self.get_company_info(),
            "circular": self.detect_circular(),
            "cdkt": self.parse_cdkt(),
            "kqhdkd": self.parse_kqhdkd(),
            "lctt": self.parse_lctt(),
            "cdtk": self.parse_cdtk(),
        }

    # ─── Helpers ──────────────────────────────────────────

    def _text(self, parent, tag: str) -> str:
        """
        Lấy text content của một child element.

        Args:
            parent: Element cha.
            tag: Tag name với namespace prefix (vd: "ns:mst").

        Returns:
            Text content đã strip, hoặc chuỗi rỗng nếu không tìm thấy.
        """
        if parent is None:
            return ""
        el = parent.find(tag, self.ns)
        return (el.text or "").strip() if el is not None else ""

    def _parse_ct_block(self, parent) -> Dict[str, Any]:
        """
        Parse block chứa các tag ct000, ct001, ...
        Trả về dict: {"ct100": 14995957186, "ct110": 14995708386, ...}

        Giá trị số (bao gồm số âm) được convert sang int/float.
        Text giữ nguyên str. Tag rỗng trả về None.

        Args:
            parent: Element cha chứa các tag ct.

        Returns:
            Dict mapping tag name -> giá trị đã parse.
        """
        if parent is None:
            return {}

        result = {}
        for child in parent:
            # Bỏ namespace prefix để lấy local name
            tag = etree.QName(child).localname
            text = (child.text or "").strip()

            if not text:
                result[tag] = None
                continue

            # Thử parse số (bao gồm số âm)
            try:
                if "." in text:
                    result[tag] = float(text)
                else:
                    result[tag] = int(text)
            except ValueError:
                result[tag] = text

        return result
