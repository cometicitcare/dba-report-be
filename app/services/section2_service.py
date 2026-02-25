"""
Buddhist Affairs MIS Dashboard - Section 2 Service (Detail Reports)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from app.schemas.dashboard import (
    BikkuTypeItem,
    DahampasalItem,
    TeacherItem,
    StudentItem,
    Section2Response,
    GeographicItem,
    GeographicResponse,
)
from app.schemas.filters import DashboardFilters


class Section2Service:
    """Service for Section 2 - Detail Reports"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_detail_reports(self, filters: DashboardFilters = None) -> Section2Response:
        """Get all detail report data for Section 2"""
        bikku_types = await self.get_bikku_type_breakdown(filters)
        dahampasal = await self.get_dahampasal_breakdown(filters)
        teachers = await self.get_teachers_breakdown(filters)
        students = await self.get_students_breakdown(filters)
        
        return Section2Response(
            bikku_type=bikku_types,
            dahampasal=dahampasal,
            dahampasal_teachers=teachers,
            dahampasal_students=students
        )
    
    async def get_bikku_type_breakdown(self, filters: DashboardFilters = None) -> List[BikkuTypeItem]:
        """Get Bikku Type breakdown (Samanera / Upasampada / Upavidi) using direct queries"""
        params = {}
        extra_b = ""
        if filters:
            if filters.nikaya_code:
                extra_b += " AND b.br_nikaya = :nikaya"
                params["nikaya"] = filters.nikaya_code
            if filters.province_code:
                extra_b += " AND b.br_province = :province"
                params["province"] = filters.province_code
            if filters.district_code:
                extra_b += " AND b.br_district = :district"
                params["district"] = filters.district_code
            if filters.parshawa_code:
                extra_b += " AND b.br_parshawaya = :parshawa"
                params["parshawa"] = filters.parshawa_code
            if filters.ds_code:
                extra_b += " AND b.br_division = :ds_code"
                params["ds_code"] = filters.ds_code
            if filters.gn_code:
                extra_b += " AND b.br_gndiv = :gn_code"
                params["gn_code"] = filters.gn_code

        try:
            result = await self.db.execute(text(f"""
                SELECT
                  (SELECT COUNT(*) FROM bhikku_regist b
                   WHERE (b.br_is_deleted = false OR b.br_is_deleted IS NULL) {extra_b}
                     AND NOT EXISTS (
                         SELECT 1 FROM bhikku_high_regist bh
                         WHERE bh.bhr_samanera_serial_no = b.br_regn
                           AND (bh.bhr_is_deleted = false OR bh.bhr_is_deleted IS NULL)
                     )) AS samanera,
                  (SELECT COUNT(*) FROM bhikku_high_regist
                   WHERE bhr_is_deleted = false OR bhr_is_deleted IS NULL) AS upasampada
            """), params)
            row = result.fetchone()
            return [
                BikkuTypeItem(type_key="samanera",   type_name="සාමණේර",   total=row[0] or 0),
                BikkuTypeItem(type_key="upasampada", type_name="උපසම්පදා", total=row[1] or 0),
                BikkuTypeItem(type_key="upavidi",    type_name="උපවිදි",    total=0),
            ]
        except Exception:
            # bhikku_high_regist table may not exist - just count all bhikku
            result2 = await self.db.execute(text(f"""
                SELECT COUNT(*) FROM bhikku_regist b
                WHERE (b.br_is_deleted = false OR b.br_is_deleted IS NULL) {extra_b}
            """), params)
            total = result2.scalar() or 0
            return [
                BikkuTypeItem(type_key="samanera",   type_name="සාමණේර",   total=total),
                BikkuTypeItem(type_key="upasampada", type_name="උපසම්පදා", total=0),
                BikkuTypeItem(type_key="upavidi",    type_name="උපවිදි",    total=0),
            ]
    
    async def get_dahampasal_breakdown(self, filters: DashboardFilters = None) -> List[DahampasalItem]:
        """
        Get Dahampasal location breakdown (In Temple, Out of Temple)
        Note: This table doesn't exist yet, returning placeholder data
        """
        # Placeholder data since dahampasal table doesn't exist
        return [
            DahampasalItem(location="In Temple", location_key="in_temple", total=0),
            DahampasalItem(location="Out of the Temple", location_key="out_of_temple", total=0),
        ]
    
    async def get_teachers_breakdown(self, filters: DashboardFilters = None) -> List[TeacherItem]:
        """
        Get Dahampasal Teachers breakdown
        Note: This table doesn't exist yet, returning placeholder data
        """
        return [
            TeacherItem(teacher_type="Bikku Dahampasal Teachers", teacher_key="bikku_teachers", total=0),
            TeacherItem(teacher_type="Silmatha Dahampasal Teachers", teacher_key="silmatha_teachers", total=0),
            TeacherItem(teacher_type="Teachers (Male)", teacher_key="male_teachers", total=0),
            TeacherItem(teacher_type="Teachers (Female)", teacher_key="female_teachers", total=0),
        ]
    
    async def get_students_breakdown(self, filters: DashboardFilters = None) -> List[StudentItem]:
        """
        Get Dahampasal Students breakdown
        Note: This table doesn't exist yet, returning placeholder data
        """
        return [
            StudentItem(gender="Student Male", gender_key="male", total=0),
            StudentItem(gender="Student Female", gender_key="female", total=0),
        ]
    
    async def get_province_data(self, filters: DashboardFilters = None) -> GeographicResponse:
        """
        Get Province-wise breakdown of all metrics using direct queries (no materialized views)
        so that province totals always reconcile with district totals.
        """
        return await self._get_province_fallback(filters)

    async def _get_province_data_mv(self, filters: DashboardFilters = None) -> GeographicResponse:
        """UNUSED — kept for reference only. Uses materialized view (may be stale)."""
        try:
            result = await self.db.execute(text(f"""
                SELECT 
                    province_code,
                    province_name,
                    ssbm_count,
                    bikku_count,
                    silmatha_count,
                    dahampasal_teachers_count,
                    dahampasal_students_count,
                    vihara_count,
                    arama_count,
                    dahampasal_count
                FROM mv_dashboard_province_summary
                ORDER BY province_name
            """))
            rows = result.fetchall()
            
            items = [
                GeographicItem(
                    code=row[0],
                    name=row[1] or row[0],
                    ssbm_count=row[2],
                    bikku_count=row[3],
                    silmatha_count=row[4],
                    dahampasal_teachers_count=row[5],
                    dahampasal_students_count=row[6],
                    vihara_count=row[7],
                    arama_count=row[8],
                    dahampasal_count=row[9]
                )
                for row in rows
            ]
            
            return GeographicResponse(
                data=items,
                total_count=len(items)
            )
        except Exception:
            return await self._get_province_fallback(filters)
    
    async def _get_province_fallback(self, filters: DashboardFilters = None) -> GeographicResponse:
        """
        Province data aggregated via district join so that province totals always equal
        the sum of their district totals. Uses vh_district/br_district (reliably populated)
        rather than vh_province/br_province (often NULL in DB).
        """
        result = await self.db.execute(text("""
            SELECT 
                p.cp_code,
                p.cp_name,
                COALESCE((
                    SELECT COUNT(*) FROM vihaddata v
                    WHERE (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
                      AND EXISTS (
                          SELECT 1 FROM cmm_districtdata d
                          WHERE d.dd_dcode = v.vh_district AND d.dd_prcode = p.cp_code
                            AND (d.dd_is_deleted = false OR d.dd_is_deleted IS NULL)
                      )
                ), 0) as vihara_count,
                COALESCE((
                    SELECT COUNT(*) FROM bhikku_regist b
                    WHERE (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
                      AND EXISTS (
                          SELECT 1 FROM cmm_districtdata d
                          WHERE d.dd_dcode = b.br_district AND d.dd_prcode = p.cp_code
                            AND (d.dd_is_deleted = false OR d.dd_is_deleted IS NULL)
                      )
                ), 0) as bikku_count,
                COALESCE((
                    SELECT COUNT(*) FROM silmatha_regist s
                    WHERE (s.sil_is_deleted = false OR s.sil_is_deleted IS NULL)
                      AND EXISTS (
                          SELECT 1 FROM cmm_districtdata d
                          WHERE d.dd_dcode = s.sil_district AND d.dd_prcode = p.cp_code
                            AND (d.dd_is_deleted = false OR d.dd_is_deleted IS NULL)
                      )
                ), 0) as silmatha_count,
                COALESCE((
                    SELECT COUNT(*) FROM aramadata a
                    WHERE (a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)
                      AND EXISTS (
                          SELECT 1 FROM cmm_districtdata d
                          WHERE d.dd_dcode = a.ar_district AND d.dd_prcode = p.cp_code
                            AND (d.dd_is_deleted = false OR d.dd_is_deleted IS NULL)
                      )
                ), 0) as arama_count,
                0 as dahampasal_teachers_count,
                0 as dahampasal_students_count,
                0 as ssbm_count,
                0 as dahampasal_count
            FROM cmm_province p
            WHERE p.cp_is_deleted = false OR p.cp_is_deleted IS NULL
            ORDER BY p.cp_name
        """))
        rows = result.fetchall()
        
        items = [
            GeographicItem(
                code=row[0],
                name=row[1] or row[0],
                vihara_count=row[2],
                bikku_count=row[3],
                silmatha_count=row[4],
                arama_count=row[5],
                dahampasal_teachers_count=row[6],
                dahampasal_students_count=row[7],
                ssbm_count=row[8],
                dahampasal_count=row[9]
            )
            for row in rows
        ]
        
        return GeographicResponse(data=items, total_count=len(items))

    async def get_district_data(self, filters: DashboardFilters = None) -> GeographicResponse:
        """
        Get District-wise breakdown using direct queries (no materialized views)
        so that district totals always reconcile with province totals.
        """
        return await self._get_district_fallback(filters)

    async def _get_district_fallback(self, filters: DashboardFilters = None) -> GeographicResponse:
        """District data using direct queries — no materialized views, results match province aggregates."""
        where_clause = ""
        bikku_extra = ""
        silmatha_extra = ""
        vihara_extra = ""
        arama_extra = ""

        if filters and filters.province_code:
            where_clause = f"AND d.dd_prcode = '{filters.province_code}'"
        if filters and filters.district_code:
            where_clause += f" AND d.dd_dcode = '{filters.district_code}'"
        if filters and filters.nikaya_code:
            bikku_extra   += f" AND br_nikaya = '{filters.nikaya_code}'"
            vihara_extra  += f" AND vh_nikaya = '{filters.nikaya_code}'"
            arama_extra   += f" AND ar_nikaya = '{filters.nikaya_code}'"
        if filters and filters.parshawa_code:
            bikku_extra   += f" AND br_parshawaya = '{filters.parshawa_code}'"
            vihara_extra  += f" AND vh_parshawa = '{filters.parshawa_code}'"
            arama_extra   += f" AND ar_parshawa = '{filters.parshawa_code}'"
        if filters and getattr(filters, 'grade', None):
            vihara_extra  += f" AND vh_typ = '{filters.grade}'"
        if filters and filters.ds_code:
            bikku_extra   += f" AND br_division = '{filters.ds_code}'"
            vihara_extra  += f" AND vh_divisional_secretariat = '{filters.ds_code}'"
            where_clause  += f" AND EXISTS (SELECT 1 FROM cmm_dvsec dv WHERE dv.dv_dvcode = '{filters.ds_code}' AND dv.dv_distrcd = d.dd_dcode)"
        if filters and filters.gn_code:
            bikku_extra   += f" AND br_gndiv = '{filters.gn_code}'"
            silmatha_extra += f" AND sil_gndiv = '{filters.gn_code}'"
            vihara_extra  += f" AND vh_gndiv = '{filters.gn_code}'"
            arama_extra   += f" AND ar_gndiv = '{filters.gn_code}'"
        
        result = await self.db.execute(text(f"""
            SELECT 
                d.dd_dcode,
                d.dd_dname,
                COALESCE((SELECT COUNT(*) FROM sasanarakshana_regist sar 
                         JOIN vihaddata v ON sar.sar_temple_trn = v.vh_trn 
                         WHERE v.vh_district = d.dd_dcode), 0) as ssbm_count,
                COALESCE((SELECT COUNT(*) FROM bhikku_regist WHERE br_district = d.dd_dcode 
                         AND (br_is_deleted = false OR br_is_deleted IS NULL) {bikku_extra}), 0) as bikku_count,
                COALESCE((SELECT COUNT(*) FROM silmatha_regist WHERE sil_district = d.dd_dcode 
                         AND (sil_is_deleted = false OR sil_is_deleted IS NULL) {silmatha_extra}), 0) as silmatha_count,
                0 as dahampasal_teachers_count,
                0 as dahampasal_students_count,
                COALESCE((SELECT COUNT(*) FROM vihaddata WHERE vh_district = d.dd_dcode 
                         AND (vh_is_deleted = false OR vh_is_deleted IS NULL) {vihara_extra}), 0) as vihara_count,
                COALESCE((SELECT COUNT(*) FROM aramadata WHERE ar_district = d.dd_dcode 
                         AND (ar_is_deleted = false OR ar_is_deleted IS NULL) {arama_extra}), 0) as arama_count,
                0 as dahampasal_count
            FROM cmm_districtdata d
            WHERE (d.dd_is_deleted = false OR d.dd_is_deleted IS NULL)
            {where_clause}
            ORDER BY d.dd_dname
        """))
        rows = result.fetchall()
        
        items = [
            GeographicItem(
                code=row[0],
                name=row[1] or row[0],
                ssbm_count=row[2],
                bikku_count=row[3],
                silmatha_count=row[4],
                dahampasal_teachers_count=row[5],
                dahampasal_students_count=row[6],
                vihara_count=row[7],
                arama_count=row[8],
                dahampasal_count=row[9]
            )
            for row in rows
        ]
        
        return GeographicResponse(data=items, total_count=len(items))
