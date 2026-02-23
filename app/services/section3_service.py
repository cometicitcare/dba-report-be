"""
Buddhist Affairs MIS Dashboard - Section 3 Service (Selection Reports)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from app.schemas.dashboard import (
    ParshawaItem,
    SSBMItem,
    DivisionalSecItem,
    GNItem,
    TempleListItem,
    Section3Response,
)
from app.schemas.filters import DashboardFilters


class Section3Service:
    """Service for Section 3 - Selection Reports"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_selection_reports(self, filters: DashboardFilters = None) -> Section3Response:
        """Get all selection report data for Section 3"""
        parshawa = await self.get_parshawa_breakdown(filters)
        ssbm = await self.get_ssbm_by_nikaya(filters)
        ds = await self.get_divisional_secretariat(filters)
        gn = await self.get_gn_divisions(filters)
        temples = await self.get_temple_list(filters)
        
        return Section3Response(
            parshawa=parshawa,
            ssbm_by_nikaya=ssbm,
            divisional_secretariat=ds,
            gn_divisions=gn,
            temples=temples
        )
    
    async def get_parshawa_breakdown(self, filters: DashboardFilters = None) -> List[ParshawaItem]:
        """
        Get Parshawa breakdown with vihara, bhikku and arama counts.
        Uses direct query to support full entity counts and geographic filtering.
        """
        return await self._get_parshawa_fallback(filters)
    
    async def _get_parshawa_fallback(self, filters: DashboardFilters = None) -> List[ParshawaItem]:
        """Fallback method for parshawa breakdown with full entity counts"""
        v_where = b_where = a_where = p_where = ""
        if filters:
            if filters.province_code:
                v_where += f" AND v.vh_province = '{filters.province_code}'"
                b_where += f" AND b.br_province = '{filters.province_code}'"
                a_where += f" AND a.ar_province = '{filters.province_code}'"
            if filters.district_code:
                v_where += f" AND v.vh_district = '{filters.district_code}'"
                b_where += f" AND b.br_district = '{filters.district_code}'"
                a_where += f" AND a.ar_district = '{filters.district_code}'"
            if filters.nikaya_code:
                p_where += f" AND p.pr_nikayacd = '{filters.nikaya_code}'"
            if filters.parshawa_code:
                p_where += f" AND p.pr_prn = '{filters.parshawa_code}'"

        result = await self.db.execute(text(f"""
            SELECT
                p.pr_prn                     AS parshawa_code,
                p.pr_pname                   AS parshawa_name,
                COUNT(DISTINCT v.vh_trn)     AS vihara_count,
                COUNT(DISTINCT b.br_id)      AS bhikku_count,
                COUNT(DISTINCT a.ar_id)      AS arama_count
            FROM cmm_parshawadata p
            LEFT JOIN vihaddata v
                ON v.vh_parshawa = p.pr_prn
               AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
               {v_where}
            LEFT JOIN bhikku_regist b
                ON b.br_parshawaya = p.pr_prn
               AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
               {b_where}
            LEFT JOIN aramadata a
                ON a.ar_parshawa = p.pr_prn
               AND (a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)
               {a_where}
            WHERE (p.pr_is_deleted = false OR p.pr_is_deleted IS NULL)
              {p_where}
            GROUP BY p.pr_prn, p.pr_pname
            HAVING COUNT(DISTINCT v.vh_trn) + COUNT(DISTINCT b.br_id) + COUNT(DISTINCT a.ar_id) > 0
            ORDER BY vihara_count DESC
        """))
        rows = result.fetchall()

        items = [
            ParshawaItem(
                parshawa_code=row[0],
                parshawa_name=row[1] or row[0],
                total=row[2],
                vihara_count=row[2],
                bhikku_count=row[3],
                silmatha_count=0,
                arama_count=row[4],
            )
            for row in rows
        ]

        # Add "No Parshawa" category
        result = await self.db.execute(text(f"""
            SELECT COUNT(*) FROM vihaddata v
            WHERE (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
              AND (v.vh_parshawa IS NULL OR v.vh_parshawa = '')
              {v_where}
        """))
        not_assigned = result.scalar() or 0
        if not_assigned > 0:
            items.append(ParshawaItem(
                parshawa_code="NOT_ASSIGNED",
                parshawa_name="No Parshawa",
                total=not_assigned,
                vihara_count=not_assigned,
                bhikku_count=0,
                silmatha_count=0,
                arama_count=0,
            ))

        return items
    
    async def get_ssbm_org_list(self, filters: DashboardFilters = None) -> list:
        """
        Get SSBM organisations from cmm_sasanarbm with vihara, bhikku,
        silmatha and arama counts — filtered by district and/or DS code.

        Key relationships (confirmed from DB):
          vihaddata.vh_divisional_secretariat = cmm_sasanarbm.sr_dvcd
          bhikku_regist.br_division           = cmm_sasanarbm.sr_dvcd
          silmatha_regist.sil_gndiv / aramadata.ar_gndiv  via vihara GN
        """
        ssbm_where = ""
        v_where    = ""
        if filters:
            if filters.province_code:
                v_where    += f" AND v.vh_province  = '{filters.province_code}'"
            if filters.district_code:
                ssbm_where += f" AND s.sr_discd = '{filters.district_code}'"
                v_where    += f" AND v.vh_district = '{filters.district_code}'"
            if filters.ds_code:
                # sr_dvcd already scopes the DS; also filter viharas directly
                ssbm_where += f" AND s.sr_dvcd = '{filters.ds_code}'"

        result = await self.db.execute(text(f"""
            SELECT
                s.sr_ssbmcode                       AS ssbm_code,
                s.sr_ssbname                        AS ssbm_name,
                COUNT(DISTINCT v.vh_trn)            AS vihara_count,
                COUNT(DISTINCT b.br_id)             AS bhikku_count,
                COUNT(DISTINCT sl.sil_id)           AS silmatha_count,
                COUNT(DISTINCT a.ar_id)             AS arama_count
            FROM cmm_sasanarbm s
            -- Join viharas through the DS code (not vh_ssbmcode which is unpopulated)
            LEFT JOIN vihaddata v
                ON v.vh_divisional_secretariat = s.sr_dvcd
               AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
               {v_where}
            -- Count bhikkus through the vihara's GN division
            LEFT JOIN bhikku_regist b
                ON b.br_gndiv = v.vh_gndiv
               AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
            LEFT JOIN silmatha_regist sl
                ON sl.sil_gndiv = v.vh_gndiv
               AND (sl.sil_is_deleted = false OR sl.sil_is_deleted IS NULL)
            LEFT JOIN aramadata a
                ON a.ar_gndiv = v.vh_gndiv
               AND (a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)
            WHERE (s.sr_is_deleted = false OR s.sr_is_deleted IS NULL)
              {ssbm_where}
            GROUP BY s.sr_ssbmcode, s.sr_ssbname
            HAVING COUNT(DISTINCT v.vh_trn) + COUNT(DISTINCT b.br_id)
                 + COUNT(DISTINCT sl.sil_id) + COUNT(DISTINCT a.ar_id) > 0
            ORDER BY s.sr_ssbname
        """))
        rows = result.fetchall()
        return [
            {
                "ssbm_code":     row[0],
                "ssbm_name":     row[1] or row[0],
                "vihara_count":  row[2],
                "bhikku_count":  row[3],
                "silmatha_count": row[4],
                "arama_count":   row[5],
            }
            for row in rows
        ]

    async def get_ssbm_by_nikaya(self, filters: DashboardFilters = None) -> List[SSBMItem]:
        """
        Get SSBM breakdown by Nikaya with vihara, bhikku and arama counts
        """
        v_where = b_where = a_where = ""
        if filters:
            if filters.province_code:
                v_where += f" AND v.vh_province = '{filters.province_code}'"
                b_where += f" AND b.br_province = '{filters.province_code}'"
                a_where += f" AND a.ar_province = '{filters.province_code}'"
            if filters.district_code:
                v_where += f" AND v.vh_district = '{filters.district_code}'"
                b_where += f" AND b.br_district = '{filters.district_code}'"
                a_where += f" AND a.ar_district = '{filters.district_code}'"

        result = await self.db.execute(text(f"""
            SELECT
                n.nk_nkn                        AS nikaya_code,
                n.nk_nname                      AS nikaya_name,
                COUNT(DISTINCT sar.sar_id)      AS total,
                COUNT(DISTINCT v.vh_trn)        AS vihara_count,
                COUNT(DISTINCT b.br_id)         AS bhikku_count,
                COUNT(DISTINCT a.ar_id)         AS arama_count
            FROM cmm_nikayadata n
            LEFT JOIN vihaddata v
                ON v.vh_nikaya = n.nk_nkn
               AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
               {v_where}
            LEFT JOIN sasanarakshana_regist sar
                ON sar.sar_temple_trn = v.vh_trn
               AND (sar.sar_is_deleted = false OR sar.sar_is_deleted IS NULL)
            LEFT JOIN bhikku_regist b
                ON b.br_nikaya = n.nk_nkn
               AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
               {b_where}
            LEFT JOIN aramadata a
                ON a.ar_nikaya = n.nk_nkn
               AND (a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)
               {a_where}
            WHERE (n.nk_is_deleted = false OR n.nk_is_deleted IS NULL)
            GROUP BY n.nk_nkn, n.nk_nname
            HAVING COUNT(DISTINCT sar.sar_id) > 0
            ORDER BY total DESC
        """))
        rows = result.fetchall()

        return [
            SSBMItem(
                nikaya_code=row[0],
                nikaya_name=row[1] or row[0],
                total=row[2],
                vihara_count=row[3],
                bhikku_count=row[4],
                silmatha_count=0,
                arama_count=row[5],
            )
            for row in rows
        ]
    
    async def get_divisional_secretariat(self, filters: DashboardFilters = None) -> List[DivisionalSecItem]:
        """
        Get Divisional Secretariat breakdown with vihara, bhikku, silmatha and arama counts.
        Uses cmm_dvsec (dv_dvcode, dv_dvname, dv_distrcd) and cmm_gndata (gn_gnc, gn_dvcode).
        """
        v_where = ""
        district_filter = ""
        if filters:
            if filters.province_code:
                v_where += f" AND v.vh_province = '{filters.province_code}'"
            if filters.district_code:
                v_where += f" AND v.vh_district = '{filters.district_code}'"
                district_filter = f" AND dv.dv_distrcd = '{filters.district_code}'"

        result = await self.db.execute(text(f"""
            SELECT
                dv.dv_dvcode                    AS ds_code,
                dv.dv_dvname                    AS ds_name,
                COUNT(DISTINCT v.vh_trn)        AS vihara_count,
                COUNT(DISTINCT b.br_id)         AS bhikku_count,
                COUNT(DISTINCT s.sil_id)        AS silmatha_count,
                COUNT(DISTINCT a.ar_id)         AS arama_count
            FROM cmm_dvsec dv
            LEFT JOIN vihaddata v
                ON v.vh_divisional_secretariat = dv.dv_dvcode
               AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
               {v_where}
            LEFT JOIN cmm_gndata gn
                ON gn.gn_dvcode = dv.dv_dvcode
               AND (gn.gn_is_deleted = false OR gn.gn_is_deleted IS NULL)
            LEFT JOIN bhikku_regist b
                ON b.br_gndiv = gn.gn_gnc
               AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
            LEFT JOIN silmatha_regist s
                ON s.sil_gndiv = gn.gn_gnc
               AND (s.sil_is_deleted = false OR s.sil_is_deleted IS NULL)
            LEFT JOIN aramadata a
                ON a.ar_gndiv = gn.gn_gnc
               AND (a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)
            WHERE (dv.dv_is_deleted = false OR dv.dv_is_deleted IS NULL)
              {district_filter}
            GROUP BY dv.dv_dvcode, dv.dv_dvname
            HAVING COUNT(DISTINCT v.vh_trn) > 0
            ORDER BY dv.dv_dvname
        """))
        rows = result.fetchall()

        return [
            DivisionalSecItem(
                ds_code=row[0],
                ds_name=row[1] or row[0],
                total=row[2],
                vihara_count=row[2],
                bhikku_count=row[3],
                silmatha_count=row[4],
                arama_count=row[5],
            )
            for row in rows
        ]
    
    async def get_gn_divisions(self, filters: DashboardFilters = None) -> List[GNItem]:
        """
        Get GN Division breakdown with vihara, bhikku, silmatha and arama counts.
        Requires ds_code filter to be meaningful.
        Uses cmm_gndata (gn_gnc, gn_gnname, gn_dvcode) — same table as the lookup API.
        """
        if not filters or not filters.ds_code:
            return []

        result = await self.db.execute(text(f"""
            SELECT
                gn.gn_gnc                       AS gn_code,
                gn.gn_gnname                    AS gn_name,
                COUNT(DISTINCT v.vh_trn)        AS vihara_count,
                COUNT(DISTINCT b.br_id)         AS bhikku_count,
                COUNT(DISTINCT s.sil_id)        AS silmatha_count,
                COUNT(DISTINCT a.ar_id)         AS arama_count
            FROM cmm_gndata gn
            LEFT JOIN vihaddata v
                ON v.vh_gndiv = gn.gn_gnc
               AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
            LEFT JOIN bhikku_regist b
                ON b.br_gndiv = gn.gn_gnc
               AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
            LEFT JOIN silmatha_regist s
                ON s.sil_gndiv = gn.gn_gnc
               AND (s.sil_is_deleted = false OR s.sil_is_deleted IS NULL)
            LEFT JOIN aramadata a
                ON a.ar_gndiv = gn.gn_gnc
               AND (a.ar_is_deleted = false OR a.ar_is_deleted IS NULL)
            WHERE (gn.gn_is_deleted = false OR gn.gn_is_deleted IS NULL)
              AND gn.gn_dvcode = '{filters.ds_code}'
            GROUP BY gn.gn_gnc, gn.gn_gnname
            HAVING COUNT(DISTINCT v.vh_trn) + COUNT(DISTINCT b.br_id)
                 + COUNT(DISTINCT s.sil_id) + COUNT(DISTINCT a.ar_id) > 0
            ORDER BY gn.gn_gnname
        """))
        rows = result.fetchall()

        return [
            GNItem(
                gn_code=row[0],
                gn_name=row[1] or row[0],
                total=row[2],
                vihara_count=row[2],
                bhikku_count=row[3],
                silmatha_count=row[4],
                arama_count=row[5],
            )
            for row in rows
        ]
    
    async def get_temple_list(self, filters: DashboardFilters = None, limit: int = 200, search: str = None, date_from: str = None, date_to: str = None) -> List[TempleListItem]:
        """
        Get list of temples with rich field joins.
        Supports geographic/ecclesiastical filters, free-text search on name,
        and optional date range filter on vh_updated_at.
        """
        where_clauses = ["(v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)"]

        if filters:
            if filters.province_code:
                where_clauses.append(f"v.vh_province = '{filters.province_code}'")
            if filters.district_code:
                where_clauses.append(f"v.vh_district = '{filters.district_code}'")
            if filters.ds_code:
                where_clauses.append(f"v.vh_divisional_secretariat = '{filters.ds_code}'")
            if filters.gn_code:
                where_clauses.append(f"v.vh_gndiv = '{filters.gn_code}'")
            if filters.nikaya_code:
                where_clauses.append(f"v.vh_nikaya = '{filters.nikaya_code}'")
            if filters.parshawa_code:
                where_clauses.append(f"v.vh_parshawa = '{filters.parshawa_code}'")
            if getattr(filters, 'ssbm_code', None):
                where_clauses.append(f"v.vh_ssbmcode = '{filters.ssbm_code}'")
            if filters.grade:
                where_clauses.append(f"v.vh_typ = '{filters.grade}'")

        if search and search.strip():
            s = search.strip().replace("'", "''")
            where_clauses.append(
                f"(v.vh_vname ILIKE '%{s}%' OR v.vh_trn ILIKE '%{s}%')"
            )

        if date_from:
            where_clauses.append(f"v.vh_updated_at >= '{date_from}'")
        if date_to:
            where_clauses.append(f"v.vh_updated_at < ('{date_to}'::date + INTERVAL '1 day')")

        where_sql = " AND ".join(where_clauses)

        result = await self.db.execute(text(f"""
            SELECT
                v.vh_trn                              AS vihara_id,
                v.vh_trn                              AS reg_no,
                v.vh_vname                            AS vihara_name,
                v.vh_addrs                            AS address,
                nk.nk_nname                           AS nikaya_name,
                pr.pr_pname                           AS parshawa_name,
                v.vh_typ                              AS grade,
                prov.cp_name                          AS province_name,
                dist.dd_dname                         AS district_name,
                dv.dv_dvname                          AS ds_name,
                gn.gn_gnname                          AS gn_name,
                v.vh_viharadhipathi_name              AS chief_of_temple,
                v.vh_mobile                           AS mobile,
                v.vh_updated_at                       AS updated_at
            FROM vihaddata v
            LEFT JOIN cmm_nikayadata  nk   ON nk.nk_nkn     = v.vh_nikaya
            LEFT JOIN cmm_parshawadata pr  ON pr.pr_prn      = v.vh_parshawa
            LEFT JOIN cmm_province    prov ON prov.cp_code   = v.vh_province
            LEFT JOIN cmm_districtdata dist ON dist.dd_dcode = v.vh_district
            LEFT JOIN cmm_dvsec       dv   ON dv.dv_dvcode   = v.vh_divisional_secretariat
            LEFT JOIN cmm_gndata      gn   ON gn.gn_gnc      = v.vh_gndiv
            WHERE {where_sql}
            ORDER BY v.vh_vname
            LIMIT {limit}
        """))
        rows = result.fetchall()

        return [
            TempleListItem(
                vihara_id=row[0],
                reg_no=row[1],
                vihara_name=row[2] or "",
                vihara_name_en=None,
                address=row[3],
                nikaya_name=row[4],
                parshawa_name=row[5],
                grade=row[6],
                province_name=row[7],
                district_name=row[8],
                ds_name=row[9],
                gn_name=row[10],
                chief_of_temple=row[11],
                mobile=row[12],
                updated_at=str(row[13])[:19] if row[13] else None,
                # legacy aliases
                temple_trn=row[1],
                temple_name=row[2] or "",
            )
            for row in rows
        ]
