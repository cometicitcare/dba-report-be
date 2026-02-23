"""
Buddhist Affairs MIS Dashboard - Section 1 Router (Overall Summary)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.section1_service import Section1Service
from app.schemas.dashboard import (
    Section1Response,
    SummaryTypeItem,
    SummaryNikayaItem,
    SummaryGradeItem,
)
from app.schemas.filters import DashboardFilters

router = APIRouter(prefix="/section1", tags=["Section 1 - Overall Summary"])


@router.get("/", response_model=Section1Response, summary="Get Section 1 Data")
async def get_section1(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> Section1Response:
    """
    Get all Section 1 data (Summary A, B, C).
    
    Section 1 shows overall system statistics:
    - Summary A: Type breakdown (Bikku, Silmatha, etc.)
    - Summary B: Nikaya breakdown
    - Summary C: Vihara Grading breakdown
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section1Service(db)
    return await service.get_overall_summary(filters)


@router.get("/types", response_model=List[SummaryTypeItem], summary="Get Type Summary")
async def get_type_summary(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[SummaryTypeItem]:
    """
    Get Summary A - Type breakdown (Bikku, Silmatha, etc.)
    
    Returns counts for:
    - Bikku (Buddhist monks)
    - Silmatha (Buddhist nuns)
    - Dahampasal Teachers
    - Dahampasal Students
    - Vihara (Temples)
    - Arama (Hermitages)
    - Dahampasal (Buddhist Sunday Schools)
    - SSBM (Sasana Rakshaka Bala Mandala)
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section1Service(db)
    return await service.get_type_summary(filters)


@router.get("/nikaya", response_model=List[SummaryNikayaItem], summary="Get Nikaya Summary")
async def get_nikaya_summary(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[SummaryNikayaItem]:
    """
    Get Summary B - Nikaya breakdown.
    
    Returns counts by Buddhist order (Nikaya):
    - Ramanya
    - Syomopali (Siam)
    - Amarapura
    - Not assigned
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section1Service(db)
    return await service.get_nikaya_summary(filters)


@router.get("/grades", response_model=List[SummaryGradeItem], summary="Get Grade Summary")
async def get_grade_summary(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[SummaryGradeItem]:
    """
    Get Summary C - Vihara Grading breakdown.
    
    Returns counts by temple grade:
    - Grade A
    - Grade B
    - Grade C
    - Grade D
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section1Service(db)
    return await service.get_grade_summary(filters)
