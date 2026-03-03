"""
Tự động nhận diện Thông tư áp dụng (TT133 vs TT200) từ file XML HTKK.

Dựa trên mã tờ khai:
- 684 = Thông tư 133/2016/TT-BTC (DN nhỏ và vừa)
- 405 = Thông tư 200/2014/TT-BTC (DN lớn)
"""

from typing import Optional, Tuple
from lxml import etree

try:
    from ..config import NS, BOM_BYTES, CIRCULAR_CODES
except ImportError:
    from config import NS, BOM_BYTES, CIRCULAR_CODES


def detect_circular_from_file(file_path: str) -> str:
    """
    Nhận diện Thông tư từ file XML.

    Args:
        file_path: Đường dẫn tới file XML HTKK.

    Returns:
        "TT133" hoặc "TT200"

    Raises:
        FileNotFoundError: Nếu file không tồn tại.
        ValueError: Nếu mã tờ khai không nhận diện được.
        etree.XMLSyntaxError: Nếu XML không hợp lệ.
    """
    ma_to_khai = _extract_ma_to_khai(file_path)
    return _resolve_circular(ma_to_khai)


def detect_circular_from_content(content: bytes) -> str:
    """
    Nhận diện Thông tư từ nội dung XML (bytes).

    Args:
        content: Nội dung file XML dạng bytes.

    Returns:
        "TT133" hoặc "TT200"

    Raises:
        ValueError: Nếu mã tờ khai không nhận diện được.
        etree.XMLSyntaxError: Nếu XML không hợp lệ.
    """
    # Bỏ BOM nếu có
    if content.startswith(BOM_BYTES):
        content = content[3:]

    root = etree.fromstring(content)
    tkhai = root.find(".//ns:TKhaiThue", NS)
    if tkhai is None:
        raise ValueError(
            "Không tìm thấy phần tử TKhaiThue trong XML. "
            "File có thể không phải định dạng HTKK."
        )

    ma_el = tkhai.find("ns:maTKhai", NS)
    ma = (ma_el.text or "").strip() if ma_el is not None else ""
    return _resolve_circular(ma)


def detect_circular_and_info(file_path: str) -> Tuple[str, dict]:
    """
    Nhận diện Thông tư và trả về thông tin cơ bản.

    Args:
        file_path: Đường dẫn tới file XML HTKK.

    Returns:
        Tuple (circular, info_dict) trong đó:
        - circular: "TT133" hoặc "TT200"
        - info_dict: dict chứa ma_to_khai, ten_to_khai, doi_tuong
    """
    ma_to_khai = _extract_ma_to_khai(file_path)
    circular = _resolve_circular(ma_to_khai)

    info = {
        "ma_to_khai": ma_to_khai,
        "circular": circular,
    }

    if circular == "TT133":
        info.update({
            "ten_to_khai": "Báo cáo tài chính theo Thông tư 133/2016/TT-BTC",
            "doi_tuong": "Doanh nghiệp nhỏ và vừa",
            "mau_cdkt": "B01b-DNN",
            "mau_kqhdkd": "B02-DNN",
            "mau_lctt": "B03-DNN",
            "mau_cdtk": "F01-DNN",
        })
    elif circular == "TT200":
        info.update({
            "ten_to_khai": "Báo cáo tài chính theo Thông tư 200/2014/TT-BTC",
            "doi_tuong": "Doanh nghiệp lớn",
            "mau_cdkt": "B01-DN",
            "mau_kqhdkd": "B02-DN",
            "mau_lctt": "B03-DN",
            "mau_cdtk": "F01-DN",
        })

    return circular, info


def get_mapper_for_circular(circular: str):
    """
    Trả về bộ mapping phù hợp với Thông tư.

    Args:
        circular: "TT133" hoặc "TT200"

    Returns:
        Module mapper tương ứng.

    Raises:
        ValueError: Nếu Thông tư không được hỗ trợ.
    """
    if circular == "TT133":
        try:
            from . import tt133_mapper
        except ImportError:
            from parser import tt133_mapper
        return tt133_mapper
    elif circular == "TT200":
        try:
            from . import tt200_mapper
        except ImportError:
            from parser import tt200_mapper
        return tt200_mapper
    else:
        raise ValueError(
            f"Thông tư không được hỗ trợ: {circular}. "
            f"Chỉ hỗ trợ TT133 và TT200."
        )


# ─── Internal helpers ────────────────────────────────

def _extract_ma_to_khai(file_path: str) -> str:
    """Trích xuất mã tờ khai từ file XML."""
    with open(file_path, "rb") as f:
        content = f.read()

    if content.startswith(BOM_BYTES):
        content = content[3:]

    try:
        root = etree.fromstring(content)
    except etree.XMLSyntaxError as e:
        raise etree.XMLSyntaxError(
            f"File XML không hợp lệ: {e}"
        )

    tkhai = root.find(".//ns:TKhaiThue", NS)
    if tkhai is None:
        raise ValueError(
            "Không tìm thấy phần tử TKhaiThue trong XML. "
            "File có thể không phải định dạng HTKK."
        )

    ma_el = tkhai.find("ns:maTKhai", NS)
    if ma_el is None:
        raise ValueError(
            "Không tìm thấy mã tờ khai (maTKhai) trong XML."
        )

    return (ma_el.text or "").strip()


def _resolve_circular(ma_to_khai: str) -> str:
    """
    Chuyển mã tờ khai sang tên Thông tư.

    Args:
        ma_to_khai: Mã tờ khai (684 hoặc 405).

    Returns:
        "TT133" hoặc "TT200"

    Raises:
        ValueError: Nếu mã không nhận diện được.
    """
    circular = CIRCULAR_CODES.get(ma_to_khai)
    if circular is None:
        supported = ", ".join(
            f"{k} ({v})" for k, v in CIRCULAR_CODES.items()
        )
        raise ValueError(
            f"Mã tờ khai không nhận diện được: '{ma_to_khai}'. "
            f"Các mã được hỗ trợ: {supported}"
        )
    return circular
