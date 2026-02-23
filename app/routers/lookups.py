"""
Buddhist Affairs MIS Dashboard - Lookups Router
Provides reference data for dropdowns and filters
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any

from app.database import get_db

router = APIRouter(prefix="/lookups", tags=["Lookups"])


@router.get("/provinces", summary="Get All Provinces")
async def get_provinces(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of all provinces.
    
    Returns:
    - cp_code: Province code
    - cp_name: Province name (in Sinhala)
    """
    query = text("""
        SELECT cp_code, cp_name
        FROM cmm_province
        WHERE cp_is_deleted = false OR cp_is_deleted IS NULL
        ORDER BY cp_name
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "code": row.cp_code,
            "name": row.cp_name
        }
        for row in rows
    ]


@router.get("/districts", summary="Get Districts")
async def get_districts(
    province_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of districts, optionally filtered by province.
    
    **Parameters:**
    - province_code: Filter by province (optional)
    
    Returns:
    - dd_dcode: District code
    - dd_dname: District name
    - dd_prcode: Province code
    """
    if province_code:
        query = text("""
            SELECT dd_dcode, dd_dname, dd_prcode
            FROM cmm_districtdata
            WHERE (dd_is_deleted = false OR dd_is_deleted IS NULL)
              AND dd_prcode = :province_code
            ORDER BY dd_dname
        """)
        result = await db.execute(query, {"province_code": province_code})
    else:
        query = text("""
            SELECT dd_dcode, dd_dname, dd_prcode
            FROM cmm_districtdata
            WHERE dd_is_deleted = false OR dd_is_deleted IS NULL
            ORDER BY dd_dname
        """)
        result = await db.execute(query)
    
    rows = result.fetchall()
    
    return [
        {
            "code": row.dd_dcode,
            "name": row.dd_dname,
            "province_code": row.dd_prcode
        }
        for row in rows
    ]


@router.get("/nikaya", summary="Get All Nikaya")
async def get_nikaya(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of all Nikaya (Buddhist orders).
    
    Returns:
    - nk_nkn: Nikaya code
    - nk_nname: Nikaya name
    """
    query = text("""
        SELECT nk_nkn, nk_nname
        FROM cmm_nikayadata
        WHERE nk_is_deleted = false OR nk_is_deleted IS NULL
        ORDER BY nk_nname
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "code": row.nk_nkn,
            "name": row.nk_nname
        }
        for row in rows
    ]


@router.get("/parshawa", summary="Get Parshawa by Nikaya")
async def get_parshawa(
    nikaya_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of Parshawa (sub-sections), optionally filtered by Nikaya.
    
    **Parameters:**
    - nikaya_code: Filter by nikaya (optional)
    
    Returns:
    - pr_prn: Parshawa code
    - pr_pname: Parshawa name
    """
    query = text("""
        SELECT pr_prn, pr_pname
        FROM cmm_parshawadata
        WHERE pr_is_deleted = false OR pr_is_deleted IS NULL
        ORDER BY pr_pname
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "code": row.pr_prn,
            "name": row.pr_pname
        }
        for row in rows
    ]


@router.get("/divisional-secretariat", summary="Get Divisional Secretariats")
async def get_divisional_secretariats(
    district_code: str = None,
    ssbm_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of Divisional Secretariats from cmm_dvsec.
    Filtered by district_code, or reverse-cascaded from ssbm_code.

    **Parameters:**
    - district_code: Filter by district (optional)
    - ssbm_code: Return only DS offices belonging to this SSBM (optional, takes priority)
    """
    if ssbm_code:
        # cmm_sasanarbm.sr_dvcd is a direct FK to cmm_dvsec.dv_dvcode
        query = text("""
            SELECT DISTINCT dv.dv_dvcode, dv.dv_dvname, dv.dv_distrcd
            FROM cmm_dvsec dv
            WHERE dv.dv_dvcode IN (
                SELECT sr_dvcd FROM cmm_sasanarbm WHERE sr_ssbmcode = :ssbm_code
            )
            ORDER BY dv.dv_dvname
        """)
        result = await db.execute(query, {"ssbm_code": ssbm_code})
    elif district_code:
        query = text("""
            SELECT dv_dvcode, dv_dvname, dv_distrcd
            FROM cmm_dvsec
            WHERE (dv_is_deleted = false OR dv_is_deleted IS NULL)
              AND dv_distrcd = :district_code
            ORDER BY dv_dvname
        """)
        result = await db.execute(query, {"district_code": district_code})
    else:
        query = text("""
            SELECT dv_dvcode, dv_dvname, dv_distrcd
            FROM cmm_dvsec
            WHERE dv_is_deleted = false OR dv_is_deleted IS NULL
            ORDER BY dv_dvname
        """)
        result = await db.execute(query)

    rows = result.fetchall()

    return [
        {
            "code": row.dv_dvcode,
            "name": row.dv_dvname,
            "district_code": row.dv_distrcd
        }
        for row in rows
    ]


@router.get("/gn", summary="Get GN Divisions")
async def get_gn_divisions(
    ds_code: str = None,
    ssbm_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of Grama Niladhari (GN) Divisions from cmm_gndata.
    Filtered by ds_code (cmm_gndata.gn_dvcode) or by SSBM via temple links.

    **Parameters:**
    - ds_code: Filter by Divisional Secretariat code (optional)
    - ssbm_code: Return GN divisions whose temples belong to this SSBM (optional)
    """
    if ds_code:
        query = text("""
            SELECT gn_gnc, gn_gnname, gn_dvcode
            FROM cmm_gndata
            WHERE (gn_is_deleted = false OR gn_is_deleted IS NULL)
              AND gn_dvcode = :ds_code
            ORDER BY gn_gnname
        """)
        result = await db.execute(query, {"ds_code": ds_code})
    elif ssbm_code:
        # No direct FK from GN to SSBM — join through vihaddata
        query = text("""
            SELECT DISTINCT gn.gn_gnc, gn.gn_gnname, gn.gn_dvcode
            FROM cmm_gndata gn
            JOIN vihaddata v
                ON v.vh_gndiv = gn.gn_gnc
               AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
            WHERE (gn.gn_is_deleted = false OR gn.gn_is_deleted IS NULL)
              AND v.vh_ssbmcode = :ssbm_code
            ORDER BY gn.gn_gnname
        """)
        result = await db.execute(query, {"ssbm_code": ssbm_code})
    else:
        query = text("""
            SELECT gn_gnc, gn_gnname, gn_dvcode
            FROM cmm_gndata
            WHERE gn_is_deleted = false OR gn_is_deleted IS NULL
            ORDER BY gn_gnname
            LIMIT 100
        """)
        result = await db.execute(query)

    rows = result.fetchall()

    return [
        {
            "code": row.gn_gnc,
            "name": row.gn_gnname,
            "ds_code": row.gn_dvcode
        }
        for row in rows
    ]


@router.get("/ssbm", summary="Get SSBM Organizations")
async def get_ssbm_list(
    district_code: str = None,
    ds_code: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of Sasanarakshana Bala Mandala (SSBM) organizations from cmm_sasanarbm.
    Table columns: sr_ssbmcd (PK), sr_dvsCd (DS FK), sr_discd (district FK), sr_name.
    Direct FK columns are used — no join through vihaddata.

    **Parameters:**
    - district_code: Filter by district via sr_discd (optional)
    - ds_code: Filter by DS via sr_dvsCd — takes priority (optional)
    """
    if ds_code:
        query = text("""
            SELECT sr_ssbmcode, sr_ssbname
            FROM cmm_sasanarbm
            WHERE sr_dvcd = :ds_code
            ORDER BY sr_ssbname
        """)
        result = await db.execute(query, {"ds_code": ds_code})
    elif district_code:
        query = text("""
            SELECT sr_ssbmcode, sr_ssbname
            FROM cmm_sasanarbm
            WHERE sr_discd = :district_code
            ORDER BY sr_ssbname
        """)
        result = await db.execute(query, {"district_code": district_code})
    else:
        query = text("""
            SELECT sr_ssbmcode, sr_ssbname
            FROM cmm_sasanarbm
            ORDER BY sr_ssbname
            LIMIT 200
        """)
        result = await db.execute(query)

    rows = result.fetchall()

    return [
        {
            "code": row.sr_ssbmcode,
            "name": row.sr_ssbname or row.sr_ssbmcode
        }
        for row in rows
    ]


@router.get("/grades", summary="Get Vihara Grades")
async def get_grades() -> List[Dict[str, str]]:
    """
    Get list of Vihara grade options.
    
    Returns static list of grades: A, B, C, D
    """
    return [
        {"code": "A", "name": "Grade A"},
        {"code": "B", "name": "Grade B"},
        {"code": "C", "name": "Grade C"},
        {"code": "D", "name": "Grade D"},
    ]


@router.get("/vihara-types", summary="Get Vihara / Arama Types")
async def get_vihara_types(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, str]]:
    """
    Get distinct vihara/arama types (vh_typ) from vihaddata.
    Returns the actual type codes stored in the database.
    """
    result = await db.execute(text("""
        SELECT DISTINCT vh_typ
        FROM vihaddata
        WHERE vh_typ IS NOT NULL AND vh_typ != ''
          AND (vh_is_deleted = false OR vh_is_deleted IS NULL)
        ORDER BY vh_typ
    """))
    rows = result.fetchall()
    return [{"code": row[0], "name": row[0]} for row in rows]
