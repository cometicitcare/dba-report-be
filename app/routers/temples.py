"""
Buddhist Affairs MIS Dashboard - Temples Router (Section 4 - Temple Profile)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.services.temple_service import TempleService
from app.schemas.dashboard import TempleProfileResponse

router = APIRouter(prefix="/temples", tags=["Section 4 - Temple Profile"])


@router.get("/{temple_trn}", response_model=TempleProfileResponse, summary="Get Temple Profile")
async def get_temple_profile(
    temple_trn: str,
    db: AsyncSession = Depends(get_db)
) -> TempleProfileResponse:
    """
    Get complete temple profile by Temple Registration Number (TRN).
    
    Returns:
    - General Information (name, address, contact, registration, leadership)
    - Location Details (province, district, DS, GN)
    - Viharanga (buildings, committees, associations)
    - Dahampasal Information
    - Grade and Workflow Status
    """
    service = TempleService(db)
    profile = await service.get_temple_profile(temple_trn)
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Temple with TRN '{temple_trn}' not found"
        )
    
    return profile


@router.get("/{temple_trn}/statistics", summary="Get Temple Statistics")
async def get_temple_statistics(
    temple_trn: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get statistics for a specific temple.
    
    Returns:
    - Bikku count (monks living in this temple)
    - Silmatha count
    - Dahampasal teachers count
    - Dahampasal students count
    - Has SSBM (whether SSBM exists for this temple)
    """
    service = TempleService(db)
    return await service.get_temple_statistics(temple_trn)


@router.get("/", summary="Search Temples")
async def search_temples(
    search: str = None,
    province_code: str = None,
    district_code: str = None,
    nikaya_code: str = None,
    grade: str = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search and list temples with filters and pagination.
    
    **Parameters:**
    - search: Search term (searches name, address, TRN)
    - province_code: Filter by province
    - district_code: Filter by district
    - nikaya_code: Filter by nikaya
    - grade: Filter by grade (A, B, C, D)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    **Returns:**
    - data: List of temples
    - total: Total matching temples
    - page: Current page
    - page_size: Items per page
    - total_pages: Total number of pages
    """
    service = TempleService(db)
    return await service.search_temples(
        search_term=search,
        province_code=province_code,
        district_code=district_code,
        nikaya_code=nikaya_code,
        grade=grade,
        page=page,
        page_size=min(page_size, 100)  # Cap at 100
    )
