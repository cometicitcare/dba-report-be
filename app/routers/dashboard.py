"""
Buddhist Affairs MIS Dashboard - Main Dashboard Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.filters import DashboardFilters

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", summary="Get Full Dashboard Data")
async def get_full_dashboard(
    type_filter: str = None,
    nikaya_code: str = None,
    grade: str = None,
    province_code: str = None,
    district_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get complete dashboard data for all sections.
    This endpoint is used for initial page load.
    
    **Filters:**
    - type_filter: Filter by type (bikku, silmatha, vihara, etc.)
    - nikaya_code: Filter by Nikaya
    - grade: Filter by Vihara grade (A, B, C, D)
    - province_code: Filter by Province
    - district_code: Filter by District
    """
    filters = DashboardFilters(
        type_filter=type_filter,
        nikaya_code=nikaya_code,
        grade=grade,
        province_code=province_code,
        district_code=district_code
    )
    
    service = DashboardService(db)
    return await service.get_full_dashboard(filters)


@router.get("/stats", summary="Get Quick Dashboard Statistics")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """
    Get quick dashboard statistics summary.
    Returns counts for all main categories.
    """
    service = DashboardService(db)
    return await service.get_dashboard_stats()


@router.post("/refresh-views", summary="Refresh Materialized Views")
async def refresh_views(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually refresh all dashboard materialized views.
    This updates the cached aggregated data.
    
    **Note:** Should be called periodically or after significant data changes.
    """
    service = DashboardService(db)
    success = await service.refresh_dashboard_views()
    
    if success:
        return {"status": "success", "message": "Dashboard views refreshed successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh dashboard views. Views may not exist yet."
        )


@router.get("/health", summary="Health Check")
async def health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Check if the dashboard API is healthy and database is connected.
    """
    from app.database import check_database_connection
    
    db_connected = await check_database_connection()
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected"
    }
