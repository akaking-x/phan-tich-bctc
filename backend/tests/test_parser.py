"""
Tests cho module Parser.

Kiem tra:
- parse_all tra ve cau truc du lieu dung
- detect_circular nhan dien TT133 va TT200
- _parse_ct_block xu ly so, so am, gia tri rong
- get_company_info trich xuat dung thong tin DN
"""

import os
import sys
import pytest
from pathlib import Path

# Them backend/ vao sys.path de import duoc cac module
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from parser.xml_parser import HtkkXmlParser

# ─── Fixtures ────────────────────────────────────────────

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_XML = FIXTURES_DIR / "sample_tt133.xml"


@pytest.fixture
def parser():
    """Tao parser tu file XML mau."""
    assert SAMPLE_XML.exists(), f"Sample XML khong ton tai: {SAMPLE_XML}"
    return HtkkXmlParser(str(SAMPLE_XML))


@pytest.fixture
def parsed_data(parser):
    """Du lieu da parse."""
    return parser.parse_all()


# ─── Test parse_all ──────────────────────────────────────

class TestParseAll:
    """Test parse_all tra ve cau truc du lieu dung."""

    def test_returns_dict(self, parsed_data):
        """parse_all tra ve dict."""
        assert isinstance(parsed_data, dict)

    def test_has_required_keys(self, parsed_data):
        """parse_all co day du cac key chinh."""
        required_keys = ["company", "circular", "cdkt", "kqhdkd", "lctt", "cdtk"]
        for key in required_keys:
            assert key in parsed_data, f"Thieu key '{key}' trong parse_all()"

    def test_company_is_dict(self, parsed_data):
        """company la dict."""
        assert isinstance(parsed_data["company"], dict)

    def test_circular_is_string(self, parsed_data):
        """circular la string."""
        assert isinstance(parsed_data["circular"], str)

    def test_cdkt_has_periods(self, parsed_data):
        """CDKT co so_cuoi_nam va so_dau_nam."""
        cdkt = parsed_data["cdkt"]
        assert "so_cuoi_nam" in cdkt
        assert "so_dau_nam" in cdkt
        assert "thuyet_minh" in cdkt

    def test_kqhdkd_has_periods(self, parsed_data):
        """KQHDKD co nam_nay va nam_truoc."""
        kqhdkd = parsed_data["kqhdkd"]
        assert "nam_nay" in kqhdkd
        assert "nam_truoc" in kqhdkd

    def test_lctt_has_periods(self, parsed_data):
        """LCTT co nam_nay va nam_truoc."""
        lctt = parsed_data["lctt"]
        assert "nam_nay" in lctt
        assert "nam_truoc" in lctt

    def test_cdtk_has_periods(self, parsed_data):
        """CDTK co 3 ky: dau ky, phat sinh, cuoi ky."""
        cdtk = parsed_data["cdtk"]
        assert "SoDuDauKy" in cdtk
        assert "SoPhatSinhTrongKy" in cdtk
        assert "SoDuCuoiKy" in cdtk


# ─── Test detect_circular ────────────────────────────────

class TestDetectCircular:
    """Test nhan dien Thong tu."""

    def test_tt133_detection(self, parser):
        """Nhan dien dung TT133 (ma to khai 684)."""
        result = parser.detect_circular()
        assert result == "TT133"

    def test_circular_in_parsed_data(self, parsed_data):
        """circular duoc set dung trong parse_all."""
        assert parsed_data["circular"] == "TT133"


class TestDetectCircularTT200:
    """Test nhan dien TT200."""

    def test_tt200_detection(self, tmp_path):
        """Nhan dien dung TT200 (ma to khai 405)."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <HSoThueDTu xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
          <HSoKhaiThue>
            <TTinChung>
              <TTinTKhaiThue>
                <TKhaiThue>
                  <maTKhai>405</maTKhai>
                  <tenTKhai>BCTC TT200</tenTKhai>
                  <ngayLapTKhai>25/03/2024</ngayLapTKhai>
                </TKhaiThue>
                <KyKKhaiThue>
                  <kyKKhai>N</kyKKhai>
                  <kyKKhaiTuNgay>01/01/2023</kyKKhaiTuNgay>
                  <kyKKhaiDenNgay>31/12/2023</kyKKhaiDenNgay>
                </KyKKhaiThue>
                <NNT>
                  <mst>9876543210</mst>
                  <tenNNT>Cong ty CP XYZ</tenNNT>
                  <dchiNNT>456 Le Loi</dchiNNT>
                  <tenTinhNNT>Ha Noi</tenTinhNNT>
                </NNT>
              </TTinTKhaiThue>
            </TTinChung>
            <CTieuTKhaiChinh>
              <ThuyetMinh/>
              <SoCuoiNam><ct100>0</ct100></SoCuoiNam>
              <SoDauNam><ct100>0</ct100></SoDauNam>
            </CTieuTKhaiChinh>
            <PLuc/>
          </HSoKhaiThue>
        </HSoThueDTu>'''

        xml_file = tmp_path / "tt200.xml"
        xml_file.write_text(xml_content, encoding="utf-8")

        parser = HtkkXmlParser(str(xml_file))
        assert parser.detect_circular() == "TT200"

    def test_unknown_circular_raises(self, tmp_path):
        """Ma to khai khong nhan dien duoc -> ValueError."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <HSoThueDTu xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
          <HSoKhaiThue>
            <TTinChung>
              <TTinTKhaiThue>
                <TKhaiThue>
                  <maTKhai>999</maTKhai>
                  <tenTKhai>Unknown</tenTKhai>
                  <ngayLapTKhai>01/01/2024</ngayLapTKhai>
                </TKhaiThue>
                <KyKKhaiThue>
                  <kyKKhai>N</kyKKhai>
                  <kyKKhaiTuNgay>01/01/2023</kyKKhaiTuNgay>
                  <kyKKhaiDenNgay>31/12/2023</kyKKhaiDenNgay>
                </KyKKhaiThue>
                <NNT>
                  <mst>0000000000</mst>
                  <tenNNT>Test</tenNNT>
                  <dchiNNT>Test</dchiNNT>
                  <tenTinhNNT>Test</tenTinhNNT>
                </NNT>
              </TTinTKhaiThue>
            </TTinChung>
            <CTieuTKhaiChinh>
              <ThuyetMinh/>
              <SoCuoiNam><ct100>0</ct100></SoCuoiNam>
              <SoDauNam><ct100>0</ct100></SoDauNam>
            </CTieuTKhaiChinh>
            <PLuc/>
          </HSoKhaiThue>
        </HSoThueDTu>'''

        xml_file = tmp_path / "unknown.xml"
        xml_file.write_text(xml_content, encoding="utf-8")

        parser = HtkkXmlParser(str(xml_file))
        with pytest.raises(ValueError, match="không nhận diện|999"):
            parser.detect_circular()


# ─── Test _parse_ct_block ────────────────────────────────

class TestParseCTBlock:
    """Test _parse_ct_block xu ly cac loai gia tri."""

    def test_positive_integer(self, parser):
        """Parse so nguyen duong."""
        from lxml import etree
        xml = '<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><ct100>10000000</ct100></root>'
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct100"] == 10000000

    def test_negative_integer(self, parser):
        """Parse so am."""
        from lxml import etree
        xml = '<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><ct212>-1500000</ct212></root>'
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct212"] == -1500000

    def test_float_value(self, parser):
        """Parse so thap phan."""
        from lxml import etree
        xml = '<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><ct100>123.45</ct100></root>'
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct100"] == 123.45

    def test_empty_value(self, parser):
        """Gia tri rong -> None."""
        from lxml import etree
        xml = '<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><ct100></ct100></root>'
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct100"] is None

    def test_text_value(self, parser):
        """Gia tri van ban (VD: thuyet minh)."""
        from lxml import etree
        xml = '<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><ct100>V.01</ct100></root>'
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct100"] == "V.01"

    def test_none_parent(self, parser):
        """parent = None -> dict rong."""
        result = parser._parse_ct_block(None)
        assert result == {}

    def test_multiple_values(self, parser):
        """Parse nhieu gia tri cung luc."""
        from lxml import etree
        xml = '''<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
            <ct100>10000</ct100>
            <ct200>20000</ct200>
            <ct300>-5000</ct300>
        </root>'''
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct100"] == 10000
        assert result["ct200"] == 20000
        assert result["ct300"] == -5000

    def test_zero_value(self, parser):
        """Parse gia tri 0."""
        from lxml import etree
        xml = '<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><ct120>0</ct120></root>'
        el = etree.fromstring(xml)
        result = parser._parse_ct_block(el)
        assert result["ct120"] == 0


# ─── Test get_company_info ───────────────────────────────

class TestGetCompanyInfo:
    """Test trich xuat thong tin doanh nghiep."""

    def test_returns_dict(self, parser):
        """get_company_info tra ve dict."""
        info = parser.get_company_info()
        assert isinstance(info, dict)

    def test_has_required_fields(self, parser):
        """Co day du cac truong can thiet."""
        info = parser.get_company_info()
        required_fields = [
            "mst", "ten_dn", "dia_chi", "tinh",
            "ma_to_khai", "ten_to_khai",
            "ky_bao_cao", "tu_ngay", "den_ngay", "ngay_lap",
        ]
        for field in required_fields:
            assert field in info, f"Thieu truong '{field}'"

    def test_mst_value(self, parser):
        """MST duoc trich xuat dung."""
        info = parser.get_company_info()
        assert info["mst"] == "0312345678"

    def test_company_name(self, parser):
        """Ten DN duoc trich xuat dung."""
        info = parser.get_company_info()
        assert info["ten_dn"] == "CONG TY TNHH THUONG MAI VA DICH VU PHUONG NAM"

    def test_address(self, parser):
        """Dia chi duoc trich xuat dung."""
        info = parser.get_company_info()
        assert info["dia_chi"] == "123 Nguyen Van Linh, Phuong Tan Phong, Quan 7"

    def test_province(self, parser):
        """Tinh/TP duoc trich xuat dung."""
        info = parser.get_company_info()
        assert info["tinh"] == "TP. Ho Chi Minh"

    def test_form_code(self, parser):
        """Ma to khai duoc trich xuat dung."""
        info = parser.get_company_info()
        assert info["ma_to_khai"] == "684"

    def test_period(self, parser):
        """Ky bao cao duoc trich xuat dung."""
        info = parser.get_company_info()
        assert info["ky_bao_cao"] == "N"
        assert info["tu_ngay"] == "01/01/2025"
        assert info["den_ngay"] == "31/12/2025"


# ─── Test parse individual reports ───────────────────────

class TestParseCDKT:
    """Test parse Bang Can doi Ke toan."""

    def test_cuoi_nam_values(self, parsed_data):
        """Gia tri cuoi nam duoc parse dung."""
        cn = parsed_data["cdkt"]["so_cuoi_nam"]
        assert cn["ct300"] == 13000000000
        assert cn["ct600"] == 13000000000
        assert cn["ct100"] == 7795000000

    def test_dau_nam_values(self, parsed_data):
        """Gia tri dau nam duoc parse dung."""
        dn = parsed_data["cdkt"]["so_dau_nam"]
        assert dn["ct300"] == 12000000000

    def test_negative_values(self, parsed_data):
        """So am (hao mon) duoc parse dung."""
        cn = parsed_data["cdkt"]["so_cuoi_nam"]
        assert cn["ct212"] == -1300000000


class TestParseKQHDKD:
    """Test parse Ket qua HDKD."""

    def test_nam_nay_values(self, parsed_data):
        """Gia tri nam nay duoc parse dung."""
        nn = parsed_data["kqhdkd"]["nam_nay"]
        assert nn["ct01"] == 12500000000
        assert nn["ct60"] == 772000000

    def test_nam_truoc_values(self, parsed_data):
        """Gia tri nam truoc duoc parse dung."""
        nt = parsed_data["kqhdkd"]["nam_truoc"]
        assert nt["ct01"] == 10200000000


class TestParseCDTK:
    """Test parse Can doi Tai khoan."""

    def test_has_no_co(self, parsed_data):
        """CDTK co ben No va ben Co."""
        for period in ["SoDuDauKy", "SoPhatSinhTrongKy", "SoDuCuoiKy"]:
            data = parsed_data["cdtk"][period]
            assert "no" in data
            assert "co" in data

    def test_cuoi_ky_values(self, parsed_data):
        """Gia tri cuoi ky duoc parse dung."""
        no = parsed_data["cdtk"]["SoDuCuoiKy"]["no"]
        assert no["ct111"] == 1050000000
        assert no["ct112"] == 1800000000
