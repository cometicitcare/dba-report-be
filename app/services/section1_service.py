"""
Buddhist Affairs MIS Dashboard - Section 1 Service (Overall Summary)
Uses direct queries for reliability - no materialized view dependency.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from app.schemas.dashboard import (
    SummaryTypeItem,
    SummaryNikayaItem,
    SummaryGradeItem,
    Section1Response,
)
from app.schemas.filters import DashboardFilters


class Section1Service:
    """Service for Section 1 - Overall Summary data"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overall_summary(self, filters: DashboardFilters = None) -> Section1Response:
        """Get all Summary A, B, C data"""
        summary_a = await self.get_type_summary(filters)
        summary_b = await self.get_nikaya_summary(filters)
        summary_c = await self.get_grade_summary(filters)
        
        return Section1Response(
            summary_a=summary_a,
            summary_b=summary_b,
            summary_c=summary_c
        )
    
    async def get_type_summary(self, filters: DashboardFilters = None) -> List[SummaryTypeItem]:
        """Get Summary A - Type breakdown using a single direct query (no materialized view)"""
        params = {}
        bikku_where = "(br_is_deleted = false OR br_is_deleted IS NULL)"
        sil_where   = "(sil_is_deleted = false OR sil_is_deleted IS NULL)"
        vh_where    = "(vh_is_deleted = false OR vh_is_deleted IS NULL)"
        ar_where    = "(ar_is_deleted = false OR ar_is_deleted IS NULL)"

        if filters and filters.province_code:
            bikku_where += " AND br_province = :province"
            sil_where   += " AND sil_province = :province"
            vh_where    += " AND vh_province = :province"
            ar_where    += " AND ar_province = :province"
            params["province"] = filters.province_code

        if filters and filters.district_code:
            bikku_where += " AND br_district = :district"
            sil_where   += " AND sil_district = :district"
            vh_where    += " AND vh_district = :district"
            ar_where    += " AND ar_district = :district"
            params["district"] = filters.district_code

        if filters and filters.nikaya_code:
            bikku_where += " AND br_nikaya = :nikaya"
            vh_where    += " AND vh_nikaya = :nikaya"
            ar_where    += " AND ar_nikaya = :nikaya"
            params["nikaya"] = filters.nikaya_code

        if filters and filters.parshawa_code:
            bikku_where += " AND br_parshawaya = :parshawa"
            vh_where    += " AND vh_parshawa = :parshawa"
            ar_where    += " AND ar_parshawa = :parshawa"
            params["parshawa"] = filters.parshawa_code

        if filters and filters.grade:
            vh_where += " AND vh_typ = :grade"
            params["grade"] = filters.grade

        if filters and filters.ds_code:
            bikku_where += " AND br_division = :ds_code"
            vh_where    += " AND vh_divisional_secretariat = :ds_code"
            params["ds_code"] = filters.ds_code

        if filters and filters.gn_code:
            bikku_where += " AND br_gndiv = :gn_code"
            sil_where   += " AND sil_gndiv = :gn_code"
            vh_where    += " AND vh_gndiv = :gn_code"
            ar_where    += " AND ar_gndiv = :gn_code"
            params["gn_code"] = filters.gn_code

        result = await self.db.execute(text(f"""
            SELECT
                (SELECT COUNT(*) FROM bhikku_regist        WHERE {bikku_where}) AS bikku_count,
                (SELECT COUNT(*) FROM silmatha_regist      WHERE {sil_where})   AS sil_count,
                (SELECT COUNT(*) FROM vihaddata            WHERE {vh_where})    AS vh_count,
                (SELECT COUNT(*) FROM aramadata            WHERE {ar_where})    AS ar_count,
                (SELECT COUNT(*) FROM sasanarakshana_regist
                    WHERE sar_is_deleted = false OR sar_is_deleted IS NULL)     AS ssbm_count
        """), params)
        row = result.fetchone()

        return [
            SummaryTypeItem(type_key="bikku",               type_name="Bikku",               icon="bhikku",   total=row[0] or 0),
            SummaryTypeItem(type_key="silmatha",            type_name="Silmatha",            icon="silmatha", total=row[1] or 0),
            SummaryTypeItem(type_key="dahampasal_teachers", type_name="Dahampasal Teachers", icon="teacher",  total=0),
            SummaryTypeItem(type_key="dahampasal_students", type_name="Dahampasal Students", icon="student",  total=0),
            SummaryTypeItem(type_key="vihara",              type_name="Vihara",              icon="temple",   total=row[2] or 0),
            SummaryTypeItem(type_key="arama",               type_name="Arama",               icon="arama",    total=row[3] or 0),
            SummaryTypeItem(type_key="dahampasal",          type_name="Dahampasal",          icon="school",   total=0),
            SummaryTypeItem(type_key="ssbm",                type_name="SSBM",                icon="ssbm",     total=row[4] or 0),
        ]
    
    async def get_nikaya_summary(self, filters: DashboardFilters = None) -> List[SummaryNikayaItem]:
        """Get Summary B - Nikaya breakdown with vihara, bhikku and arama counts"""
        params = {}
        b_where = "(b.br_is_deleted = false OR b.br_is_deleted IS NULL)"
        v_where = "(v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)"
        a_where = "(a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)"

        if filters and filters.nikaya_code:
            b_where += " AND b.br_nikaya = :nikaya"
            v_where += " AND v.vh_nikaya = :nikaya"
            a_where += " AND a.ar_nikaya = :nikaya"
            params["nikaya"] = filters.nikaya_code

        if filters and filters.province_code:
            b_where += " AND b.br_province = :province"
            v_where += " AND v.vh_province = :province"
            a_where += " AND a.ar_province = :province"
            params["province"] = filters.province_code

        if filters and filters.district_code:
            b_where += " AND b.br_district = :district"
            v_where += " AND v.vh_district = :district"
            a_where += " AND a.ar_district = :district"
            params["district"] = filters.district_code

        if filters and filters.parshawa_code:
            b_where += " AND b.br_parshawaya = :parshawa"
            v_where += " AND v.vh_parshawa = :parshawa"
            a_where += " AND a.ar_parshawa = :parshawa"
            params["parshawa"] = filters.parshawa_code

        if filters and filters.grade:
            v_where += " AND v.vh_typ = :grade"
            params["grade"] = filters.grade

        if filters and filters.ds_code:
            b_where += " AND b.br_division = :ds_code"
            v_where += " AND v.vh_divisional_secretariat = :ds_code"
            params["ds_code"] = filters.ds_code

        if filters and filters.gn_code:
            b_where += " AND b.br_gndiv = :gn_code"
            v_where += " AND v.vh_gndiv = :gn_code"
            a_where += " AND a.ar_gndiv = :gn_code"
            params["gn_code"] = filters.gn_code

        result = await self.db.execute(text(f"""
            SELECT
                n.nk_nkn                    AS nikaya_code,
                n.nk_nname                  AS nikaya_name,
                COUNT(DISTINCT b.br_id)     AS bhikku_count,
                COUNT(DISTINCT v.vh_trn)    AS vihara_count,
                COUNT(DISTINCT a.ar_id)     AS arama_count
            FROM cmm_nikayadata n
            LEFT JOIN bhikku_regist b
                ON b.br_nikaya = n.nk_nkn AND {b_where}
            LEFT JOIN vihaddata v
                ON v.vh_nikaya = n.nk_nkn AND {v_where}
            LEFT JOIN aramadata a
                ON a.ar_nikaya = n.nk_nkn AND {a_where}
            WHERE (n.nk_is_deleted = false OR n.nk_is_deleted IS NULL)
            GROUP BY n.nk_nkn, n.nk_nname
            HAVING COUNT(DISTINCT b.br_id) + COUNT(DISTINCT v.vh_trn) + COUNT(DISTINCT a.ar_id) > 0
            ORDER BY bhikku_count DESC
        """), params)
        rows = result.fetchall()

        return [
            SummaryNikayaItem(
                nikaya_code=row[0],
                nikaya_name=row[1],
                total=row[2],           # bhikku_count (backward compat)
                bhikku_count=row[2],
                vihara_count=row[3],
                silmatha_count=0,       # no direct nikaya field on silmatha_regist
                arama_count=row[4],
            )
            for row in rows
        ]
    
    async def get_grade_summary(self, filters: DashboardFilters = None) -> List[SummaryGradeItem]:
        """Get Summary C - Vihara grade breakdown using direct query"""
        params = {}
        extra_where = ""

        if filters and filters.province_code:
            extra_where += " AND vh_province = :province"
            params["province"] = filters.province_code
        if filters and filters.district_code:
            extra_where += " AND vh_district = :district"
            params["district"] = filters.district_code

        if filters and filters.nikaya_code:
            extra_where += " AND vh_nikaya = :nikaya"
            params["nikaya"] = filters.nikaya_code

        if filters and filters.parshawa_code:
            extra_where += " AND vh_parshawa = :parshawa"
            params["parshawa"] = filters.parshawa_code

        if filters and filters.ds_code:
            extra_where += " AND vh_divisional_secretariat = :ds_code"
            params["ds_code"] = filters.ds_code

        if filters and filters.gn_code:
            extra_where += " AND vh_gndiv = :gn_code"
            params["gn_code"] = filters.gn_code

        result = await self.db.execute(text(f"""
            SELECT
                COALESCE(vh_typ, 'N/A') AS grade,
                CASE vh_typ
                    WHEN 'VH'        THEN 'Vihara'
                    WHEN 'MAIN'      THEN 'Main Vihara'
                    WHEN 'BRANCH'    THEN 'Branch Vihara'
                    WHEN 'VIHARA'    THEN 'Vihara (Other)'
                    WHEN 'VIKASITHA' THEN 'Vikasitha'
                    WHEN 'A'         THEN 'Grade A'
                    WHEN 'B'         THEN 'Grade B'
                    WHEN 'C'         THEN 'Grade C'
                    WHEN 'D'         THEN 'Grade D'
                    ELSE COALESCE(vh_typ, 'Not Graded')
                END AS grade_name,
                COUNT(*) AS total
            FROM vihaddata
            WHERE (vh_is_deleted = false OR vh_is_deleted IS NULL)
              {extra_where}
            GROUP BY vh_typ
            ORDER BY total DESC
        """), params)
        rows = result.fetchall()

        return [
            SummaryGradeItem(grade=row[0], grade_name=row[1], total=row[2])
            for row in rows
        ]
