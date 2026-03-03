"""
BCTC Analyzer — Parser Module.
Parse file XML BCTC từ HTKK, hỗ trợ TT133 và TT200.
"""

from .xml_parser import HtkkXmlParser
from .detector import (
    detect_circular_from_file,
    detect_circular_from_content,
    detect_circular_and_info,
    get_mapper_for_circular,
)
from .tt133_mapper import (
    CDKT_MAP as TT133_CDKT_MAP,
    KQHDKD_MAP as TT133_KQHDKD_MAP,
    LCTT_TT_MAP as TT133_LCTT_TT_MAP,
    CDTK_ACCOUNT_MAP as TT133_CDTK_ACCOUNT_MAP,
)
from .tt200_mapper import (
    CDKT_MAP as TT200_CDKT_MAP,
    KQHDKD_MAP as TT200_KQHDKD_MAP,
    LCTT_TT_MAP as TT200_LCTT_TT_MAP,
    CDTK_ACCOUNT_MAP as TT200_CDTK_ACCOUNT_MAP,
)

__all__ = [
    # Parser
    "HtkkXmlParser",
    # Detector
    "detect_circular_from_file",
    "detect_circular_from_content",
    "detect_circular_and_info",
    "get_mapper_for_circular",
    # TT133 Mappers
    "TT133_CDKT_MAP",
    "TT133_KQHDKD_MAP",
    "TT133_LCTT_TT_MAP",
    "TT133_CDTK_ACCOUNT_MAP",
    # TT200 Mappers
    "TT200_CDKT_MAP",
    "TT200_KQHDKD_MAP",
    "TT200_LCTT_TT_MAP",
    "TT200_CDTK_ACCOUNT_MAP",
]
