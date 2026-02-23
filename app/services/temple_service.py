"""
Buddhist Affairs MIS Dashboard - Temple Service (Section 4 - Temple Profile)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.schemas.dashboard import (
    TempleGeneralInfo,
    TempleLocation,
    TempleViharanga,
    TempleDahampasal,
    TempleProfileResponse,
)


class TempleService:
    """Service for Section 4 - Temple Profile"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_temple_profile(self, temple_trn: str) -> Optional[TempleProfileResponse]:
        """
        Get complete temple profile by TRN
        """
        result = await self.db.execute(text("""
            SELECT 
                v.vh_trn,
                v.vh_vname,
                v.vh_addrs,
                v.vh_mobile,
                v.vh_email,
                v.vh_viharadhipathi_name,
                v.vh_viharadhipathi_regn,
                v.vh_nikaya,
                n.nk_nname as nikaya_name,
                v.vh_parshawa,
                p.pr_pname as parshawa_name,
                v.vh_bgndate,
                v.vh_period_established,
                v.vh_province,
                prov.cp_name as province_name,
                v.vh_district,
                dist.dd_dname as district_name,
                v.vh_divisional_secretariat,
                v.vh_pradeshya_sabha,
                v.vh_gndiv,
                gn.gn_gnname as gn_name,
                v.vh_buildings_description,
                v.vh_dayaka_families_count,
                v.vh_kulangana_committee,
                v.vh_dayaka_sabha,
                v.vh_temple_working_committee,
                v.vh_other_associations,
                v.vh_typ,
                v.vh_workflow_status
            FROM vihaddata v
            LEFT JOIN cmm_nikayadata n ON v.vh_nikaya = n.nk_nkn
            LEFT JOIN cmm_parshawadata p ON v.vh_parshawa = p.pr_prn
            LEFT JOIN cmm_province prov ON v.vh_province = prov.cp_code
            LEFT JOIN cmm_districtdata dist ON v.vh_district = dist.dd_dcode
            LEFT JOIN cmm_gndata gn ON v.vh_gndiv = gn.gn_gnc
            WHERE v.vh_trn = :temple_trn
              AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
        """), {"temple_trn": temple_trn})
        
        row = result.fetchone()
        
        if not row:
            return None
        
        # Build general info
        general_info = TempleGeneralInfo(
            temple_trn=row[0],
            name=row[1] or "Unknown",
            address=row[2],
            mobile=row[3],
            email=row[4],
            registration_no=row[0],
            viharadhipathi_name=row[5],
            viharadhipathi_regn=row[6],
            nikaya=row[8] or row[7],  # Use name if available
            parshawa=row[10] or row[9],  # Use name if available
            establishment_date=row[11],
            period_established=row[12]
        )
        
        # Build location info
        location = TempleLocation(
            province=row[13],
            province_name=row[14],
            district=row[15],
            district_name=row[16],
            divisional_secretariat=row[17],
            pradeshya_sabha=row[18],
            gn_division=row[20] or row[19]  # Use name if available
        )
        
        # Build viharanga info
        viharanga = TempleViharanga(
            buildings_description=row[21],
            dayaka_families_count=row[22],
            kulangana_committee=row[23],
            dayaka_sabha=row[24],
            temple_working_committee=row[25],
            other_associations=row[26]
        )
        
        # Build dahampasal info (placeholder - table doesn't exist)
        dahampasal = TempleDahampasal(
            dahampasal_name=None,
            teachers_count=0,
            students_count=0
        )
        
        return TempleProfileResponse(
            general_info=general_info,
            location=location,
            viharanga=viharanga,
            dahampasal=dahampasal,
            grade=row[27],
            workflow_status=row[28]
        )
    
    async def search_temples(
        self, 
        search_term: str = None,
        province_code: str = None,
        district_code: str = None,
        nikaya_code: str = None,
        grade: str = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        Search temples with filters and pagination
        """
        where_clauses = ["(vh_is_deleted = false OR vh_is_deleted IS NULL)"]
        params = {}
        
        if search_term:
            where_clauses.append("(vh_vname ILIKE :search OR vh_addrs ILIKE :search OR vh_trn ILIKE :search)")
            params["search"] = f"%{search_term}%"
        
        if province_code:
            where_clauses.append("vh_province = :province")
            params["province"] = province_code
        
        if district_code:
            where_clauses.append("vh_district = :district")
            params["district"] = district_code
        
        if nikaya_code:
            where_clauses.append("vh_nikaya = :nikaya")
            params["nikaya"] = nikaya_code
        
        if grade:
            where_clauses.append("vh_typ = :grade")
            params["grade"] = grade
        
        where_sql = " AND ".join(where_clauses)
        offset = (page - 1) * page_size
        
        # Get total count
        count_result = await self.db.execute(
            text(f"SELECT COUNT(*) FROM vihaddata WHERE {where_sql}"),
            params
        )
        total = count_result.scalar() or 0
        
        # Get data
        result = await self.db.execute(text(f"""
            SELECT 
                vh_trn,
                vh_vname,
                vh_addrs,
                vh_gndiv,
                vh_viharadhipathi_name,
                vh_mobile,
                vh_typ,
                vh_nikaya
            FROM vihaddata
            WHERE {where_sql}
            ORDER BY vh_vname
            LIMIT :limit OFFSET :offset
        """), {**params, "limit": page_size, "offset": offset})
        
        rows = result.fetchall()
        
        temples = [
            {
                "temple_trn": row[0],
                "temple_name": row[1] or "Unknown",
                "address": row[2],
                "gn_division": row[3],
                "chief_of_temple": row[4],
                "mobile": row[5],
                "grade": row[6],
                "nikaya": row[7]
            }
            for row in rows
        ]
        
        return {
            "data": temples,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def get_temple_statistics(self, temple_trn: str) -> dict:
        """
        Get statistics for a specific temple
        """
        stats = {
            "bikku_count": 0,
            "silmatha_count": 0,
            "dahampasal_teachers_count": 0,
            "dahampasal_students_count": 0,
            "has_ssbm": False
        }
        
        # Count Bikkus living in this temple
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM bhikku_regist 
            WHERE br_livtemple = :temple_trn
              AND (br_is_deleted = false OR br_is_deleted IS NULL)
        """), {"temple_trn": temple_trn})
        stats["bikku_count"] = result.scalar() or 0
        
        # Check if SSBM exists
        result = await self.db.execute(text("""
            SELECT COUNT(*) FROM sasanarakshana_regist 
            WHERE sar_temple_trn = :temple_trn
              AND (sar_is_deleted = false OR sar_is_deleted IS NULL)
        """), {"temple_trn": temple_trn})
        stats["has_ssbm"] = (result.scalar() or 0) > 0
        
        return stats
