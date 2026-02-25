"""
Buddhist Affairs MIS Dashboard - Section 3 Router (Selection Reports)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.section3_service import Section3Service
from app.schemas.dashboard import (
    Section3Response,
    ParshawaItem,
    SSBMItem,
    DivisionalSecItem,
    GNItem,
    TempleListItem,
)
from app.schemas.filters import DashboardFilters

router = APIRouter(prefix="/section3", tags=["Section 3 - Selection Reports"])


@router.get("/", response_model=Section3Response, summary="Get Section 3 Data")
async def get_section3(
    province_code: str = None,
    district_code: str = None,
    ds_code: str = None,
    gn_code: str = None,
    nikaya_code: str = None,
    parshawa_code: str = None,
    ssbm_code: str = None,
    grade: str = None,
    db: AsyncSession = Depends(get_db)
) -> Section3Response:
    """
    Get all Section 3 selection reports.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code,
        ds_code=ds_code,
        gn_code=gn_code,
        nikaya_code=nikaya_code,
        parshawa_code=parshawa_code,
        ssbm_code=ssbm_code,
        grade=grade
    )

    service = Section3Service(db)
    return await service.get_selection_reports(filters)


@router.get("/parshawa", response_model=List[ParshawaItem], summary="Get Parshawa Breakdown")
async def get_parshawa(
    province_code: str = None,
    district_code: str = None,
    nikaya_code: str = None,
    parshawa_code: str = None,
    ds_code: str = None,
    gn_code: str = None,
    ssbm_code: str = None,
    grade: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[ParshawaItem]:
    """
    Get Parshawa (Buddhist sub-section) breakdown with counts.
    Filtered by province, district, nikaya, ds, gn etc.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code,
        nikaya_code=nikaya_code,
        parshawa_code=parshawa_code,
        ds_code=ds_code,
        gn_code=gn_code,
        ssbm_code=ssbm_code,
        grade=grade,
    )
    
    service = Section3Service(db)
    return await service.get_parshawa_breakdown(filters)


@router.get("/ssbm-org", summary="Get SSBM Organisations with Counts")
async def get_ssbm_org_list(
    province_code: str = None,
    district_code: str = None,
    ds_code: str = None,
    ssbm_code: str = None,
    nikaya_code: str = None,
    grade: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get SSBM organisations from cmm_sasanarbm with vihara, bhikku,
    silmatha and arama counts.  Filter by district_code and/or ds_code.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code,
        ds_code=ds_code,
        ssbm_code=ssbm_code,
        nikaya_code=nikaya_code,
        grade=grade,
    )
    service = Section3Service(db)
    return await service.get_ssbm_org_list(filters)


@router.get("/ssbm", response_model=List[SSBMItem], summary="Get SSBM by Nikaya")
async def get_ssbm_by_nikaya(
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[SSBMItem]:
    """
    Get Sasana Rakshaka Bala Mandala (SSBM) breakdown by Nikaya.
    
    Shows how many SSBM organizations exist for each Nikaya.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code
    )
    
    service = Section3Service(db)
    return await service.get_ssbm_by_nikaya(filters)


@router.get("/divisional-secretariat", response_model=List[DivisionalSecItem], summary="Get DS Breakdown")
async def get_divisional_secretariat(
    district_code: str = None,
    province_code: str = None,
    nikaya_code: str = None,
    parshawa_code: str = None,
    grade: str = None,
    ds_code: str = None,
    ssbm_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[DivisionalSecItem]:
    """
    Get Divisional Secretariat breakdown.
    Shows temple counts per Divisional Secretariat.
    """
    filters = DashboardFilters(
        district_code=district_code,
        province_code=province_code,
        nikaya_code=nikaya_code,
        parshawa_code=parshawa_code,
        grade=grade,
        ds_code=ds_code,
        ssbm_code=ssbm_code,
    )
    
    service = Section3Service(db)
    return await service.get_divisional_secretariat(filters)


@router.get("/gn", response_model=List[GNItem], summary="Get GN Division Breakdown")
async def get_gn_divisions(
    ds_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[GNItem]:
    """
    Get Grama Niladhari (GN) Division breakdown.
    
    Shows temple counts per GN Division.
    
    **Note:** ds_code (Divisional Secretariat code) is required.
    Returns empty list if no DS is selected.
    """
    if not ds_code:
        return []
    
    filters = DashboardFilters(ds_code=ds_code)
    
    service = Section3Service(db)
    return await service.get_gn_divisions(filters)


@router.get("/temples", response_model=List[TempleListItem], summary="Get Temple List")
async def get_temple_list(
    province_code: str = None,
    district_code: str = None,
    ds_code: str = None,
    gn_code: str = None,
    nikaya_code: str = None,
    parshawa_code: str = None,
    ssbm_code: str = None,
    grade: str = None,
    search: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 200,
    db: AsyncSession = Depends(get_db)
) -> List[TempleListItem]:
    """
    Get list of temples based on filters.
    Supports a free-text 'search' param (matched against temple name).
    Supports 'date_from' and 'date_to' (YYYY-MM-DD) to filter by vh_updated_at.
    """
    filters = DashboardFilters(
        province_code=province_code,
        district_code=district_code,
        ds_code=ds_code,
        gn_code=gn_code,
        nikaya_code=nikaya_code,
        parshawa_code=parshawa_code,
        ssbm_code=ssbm_code,
        grade=grade
    )

    service = Section3Service(db)
    return await service.get_temple_list(
        filters, limit=limit, search=search, date_from=date_from, date_to=date_to
    )
