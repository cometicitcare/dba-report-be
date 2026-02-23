"""
Buddhist Affairs MIS Dashboard - Models Package
"""
from app.models.bhikku import BhikkuRegist, BhikkuHighRegist
from app.models.silmatha import SilmathaRegist
from app.models.vihara import Vihaddata
from app.models.arama import Aramadata
from app.models.common import (
    CmmProvince,
    CmmDistrictdata,
    CmmNikayadata,
    CmmParshawadata,
    CmmDvsec,
    CmmGndata,
    CmmSasanarbm,
    SasanarakshanaRegist,
)

__all__ = [
    "BhikkuRegist",
    "BhikkuHighRegist",
    "SilmathaRegist",
    "Vihaddata",
    "Aramadata",
    "CmmProvince",
    "CmmDistrictdata",
    "CmmNikayadata",
    "CmmParshawadata",
    "CmmDvsec",
    "CmmGndata",
    "CmmSasanarbm",
    "SasanarakshanaRegist",
]
