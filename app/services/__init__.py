"""
Buddhist Affairs MIS Dashboard - Services Package
"""
from app.services.dashboard_service import DashboardService
from app.services.section1_service import Section1Service
from app.services.section2_service import Section2Service
from app.services.section3_service import Section3Service
from app.services.temple_service import TempleService

__all__ = [
    "DashboardService",
    "Section1Service",
    "Section2Service",
    "Section3Service",
    "TempleService",
]
