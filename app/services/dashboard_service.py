"""
Buddhist Affairs MIS Dashboard - Main Dashboard Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any

from app.services.section1_service import Section1Service
from app.services.section2_service import Section2Service
from app.services.section3_service import Section3Service
from app.schemas.filters import DashboardFilters


class DashboardService:
    """Main dashboard service that coordinates all sections"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.section1 = Section1Service(db)
        self.section2 = Section2Service(db)
        self.section3 = Section3Service(db)
    
    async def get_full_dashboard(self, filters: DashboardFilters = None) -> Dict[str, Any]:
        """
        Get complete dashboard data for all sections.
        This is used for initial load.
        """
        filters = filters or DashboardFilters()
        
        # Get data for all sections
        section1_data = await self.section1.get_overall_summary(filters)
        section2_data = await self.section2.get_detail_reports(filters)
        section3_data = await self.section3.get_selection_reports(filters)
        
        return {
            "section1": section1_data,
            "section2": section2_data,
            "section3": section3_data,
            "filters": {
                "type_filter": filters.type_filter,
                "nikaya_code": filters.nikaya_code,
                "grade": filters.grade,
                "province_code": filters.province_code,
                "district_code": filters.district_code,
            }
        }
    
    async def get_dashboard_stats(self) -> Dict[str, int]:
        """
        Get quick dashboard statistics.
        Uses materialized views for fast performance.
        """
        try:
            result = await self.db.execute(text("""
                SELECT type_key, total 
                FROM mv_dashboard_type_summary
            """))
            rows = result.fetchall()
            return {row[0]: row[1] for row in rows}
        except Exception:
            # Fallback to direct queries if views don't exist
            return await self._get_stats_fallback()
    
    async def _get_stats_fallback(self) -> Dict[str, int]:
        """Fallback method when materialized views don't exist"""
        stats = {}
        
        # Bikku count
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM bhikku_regist 
            WHERE br_is_deleted = false OR br_is_deleted IS NULL
        """))
        stats["bikku"] = result.scalar() or 0
        
        # Silmatha count
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM silmatha_regist 
            WHERE sil_is_deleted = false OR sil_is_deleted IS NULL
        """))
        stats["silmatha"] = result.scalar() or 0
        
        # Vihara count
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM vihaddata 
            WHERE vh_is_deleted = false OR vh_is_deleted IS NULL
        """))
        stats["vihara"] = result.scalar() or 0
        
        # Arama count
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM aramadata 
            WHERE ar_is_deleted = false OR ar_is_deleted IS NULL
        """))
        stats["arama"] = result.scalar() or 0
        
        # SSBM count
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM sasanarakshana_regist 
            WHERE sar_is_deleted = false OR sar_is_deleted IS NULL
        """))
        stats["ssbm"] = result.scalar() or 0
        
        # Placeholders for tables not yet created
        stats["dahampasal_teachers"] = 0
        stats["dahampasal_students"] = 0
        stats["dahampasal"] = 0
        
        return stats
    
    async def refresh_dashboard_views(self) -> bool:
        """
        Manually refresh all materialized views.
        Returns True if successful.
        """
        try:
            await self.db.execute(text("SELECT refresh_dashboard_views()"))
            await self.db.commit()
            return True
        except Exception as e:
            print(f"Error refreshing views: {e}")
            return False
