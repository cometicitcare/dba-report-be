"""
Buddhist Affairs MIS Dashboard - Persons Router
Bhikku & Silmatha combined list endpoint
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.persons_service import PersonsService
from app.schemas.dashboard import PersonListItem

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.get("", response_model=List[PersonListItem], summary="Get Persons List (Bhikku + Silmatha)")
async def get_persons(
    person_type:   str = None,   # BHIKKU | SILMATHA | None (all)
    province_code: str = None,
    district_code: str = None,
    nikaya_code:   str = None,
    parshawa_code: str = None,
    search:        str = None,
    date_from:     str = None,
    date_to:       str = None,
    limit:         int = 200,
    db: AsyncSession = Depends(get_db),
) -> List[PersonListItem]:
    """
    Get combined list of Bhikku (monks) and Silmatha (nuns).

    Filters:
    - **person_type**: BHIKKU or SILMATHA (omit for both)
    - **province_code / district_code**: geographic filter
    - **nikaya_code / parshawa_code**: ecclesiastical filter (Bhikku only)
    - **search**: free-text search on name / reg_no
    - **date_from / date_to**: filter by last updated date (YYYY-MM-DD)
    - **limit**: max rows returned (default 200)
    """
    service = PersonsService(db)
    return await service.get_persons_list(
        person_type=person_type,
        province_code=province_code,
        district_code=district_code,
        nikaya_code=nikaya_code,
        parshawa_code=parshawa_code,
        search=search,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
