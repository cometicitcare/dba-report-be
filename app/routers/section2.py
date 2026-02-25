"""
Buddhist Affairs MIS Dashboard - Section 2 Router (Detail Reports)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.section2_service import Section2Service
from app.schemas.dashboard import (
    Section2Response,
    BikkuTypeItem,
    DahampasalItem,
    TeacherItem,
    StudentItem,
    GeographicResponse,
)
from app.schemas.filters import DashboardFilters

router = APIRouter(prefix="/section2", tags=["Section 2 - Detail Reports"])


@router.get("/", response_model=Section2Response, summary="Get Section 2 Data")
async def get_section2(
    type_filter: str = None,
    nikaya_code: str = None,
    grade: str = None,
    province_code: str = None,
    district_code: str = None,
    ds_code: str = None,
    gn_code: str = None,
    ssbm_code: str = None,
    parshawa_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> Section2Response:
    """
    Get all Section 2 detail reports.
    """
    filters = DashboardFilters(
        type_filter=type_filter,
        nikaya_code=nikaya_code,
        grade=grade,
        province_code=province_code,
        district_code=district_code,
        ds_code=ds_code,
        gn_code=gn_code,
        ssbm_code=ssbm_code,
        parshawa_code=parshawa_code,
    )
    
    service = Section2Service(db)
    return await service.get_detail_reports(filters)


@router.get("/bikku-types", response_model=List[BikkuTypeItem], summary="Get Bikku Type Breakdown")
async def get_bikku_types(
    nikaya_code: str = None,
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[BikkuTypeItem]:
    """
    Get Bikku Type breakdown.
    
    Returns:
    - Samanera: Novice monks
    - Upasampada: Fully ordained monks
    - Upavidi: (Other categories)
    """
    filters = DashboardFilters(
        nikaya_code=nikaya_code,
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section2Service(db)
    return await service.get_bikku_type_breakdown(filters)


@router.get("/dahampasal", response_model=List[DahampasalItem], summary="Get Dahampasal Breakdown")
async def get_dahampasal(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[DahampasalItem]:
    """
    Get Dahampasal (Sunday School) location breakdown.
    
    Returns:
    - In Temple: Schools within temple premises
    - Out of Temple: Schools outside temple premises
    
    **Note:** Dahampasal table not yet created - placeholder data returned.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section2Service(db)
    return await service.get_dahampasal_breakdown(filters)


@router.get("/teachers", response_model=List[TeacherItem], summary="Get Teachers Breakdown")
async def get_teachers(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[TeacherItem]:
    """
    Get Dahampasal Teachers breakdown.
    
    Returns:
    - Bikku Dahampasal Teachers
    - Silmatha Dahampasal Teachers
    - Teachers (Male)
    - Teachers (Female)
    
    **Note:** Teachers table not yet created - placeholder data returned.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section2Service(db)
    return await service.get_teachers_breakdown(filters)


@router.get("/students", response_model=List[StudentItem], summary="Get Students Breakdown")
async def get_students(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[StudentItem]:
    """
    Get Dahampasal Students breakdown.
    
    Returns:
    - Student Male
    - Student Female
    
    **Note:** Students table not yet created - placeholder data returned.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section2Service(db)
    return await service.get_students_breakdown(filters)


@router.get("/provinces", response_model=GeographicResponse, summary="Get Province Data")
async def get_province_data(
    type_filter: str = None,
    nikaya_code: str = None,
    grade: str = None,
    parshawa_code: str = None,
    ds_code: str = None,
    gn_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> GeographicResponse:
    """
    Get Province-wise breakdown of all metrics.
    """
    filters = DashboardFilters(
        type_filter=type_filter,
        nikaya_code=nikaya_code,
        grade=grade,
        parshawa_code=parshawa_code,
        ds_code=ds_code,
        gn_code=gn_code,
    )
    
    service = Section2Service(db)
    return await service.get_province_data(filters)


@router.get("/districts", response_model=GeographicResponse, summary="Get District Data")
async def get_district_data(
    province_code: str = None,
    type_filter: str = None,
    nikaya_code: str = None,
    grade: str = None,
    parshawa_code: str = None,
    ds_code: str = None,
    gn_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> GeographicResponse:
    """
    Get District-wise breakdown of all metrics.
    """
    filters = DashboardFilters(
        province_code=province_code,
        type_filter=type_filter,
        nikaya_code=nikaya_code,
        grade=grade,
        parshawa_code=parshawa_code,
        ds_code=ds_code,
        gn_code=gn_code,
    )
    
    service = Section2Service(db)
    return await service.get_district_data(filters)
