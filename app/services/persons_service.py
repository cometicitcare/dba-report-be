"""
Buddhist Affairs MIS Dashboard - Persons Service
Handles Bhikku & Silmatha combined queries
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from app.schemas.dashboard import PersonListItem


class PersonsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_persons_list(
        self,
        person_type: Optional[str] = None,
        province_code: Optional[str] = None,
        district_code: Optional[str] = None,
        nikaya_code: Optional[str] = None,
        parshawa_code: Optional[str] = None,
        search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 200,
    ) -> List[PersonListItem]:

        # ── Bhikku where clauses ──────────────────────────────────────────
        b_where = ["(b.br_is_deleted = false OR b.br_is_deleted IS NULL)"]

        if province_code:
            b_where.append(f"b.br_province = '{province_code}'")
        if district_code:
            b_where.append(f"b.br_district = '{district_code}'")
        if nikaya_code:
            b_where.append(f"b.br_nikaya = '{nikaya_code}'")
        if parshawa_code:
            b_where.append(f"b.br_parshawaya = '{parshawa_code}'")
        if search and search.strip():
            s = search.strip().replace("'", "''")
            b_where.append(
                f"(b.br_gihiname ILIKE '%{s}%' OR b.br_mahananame ILIKE '%{s}%' OR b.br_regn ILIKE '%{s}%')"
            )
        if date_from:
            b_where.append(f"b.br_updated_at >= '{date_from}'")
        if date_to:
            b_where.append(f"b.br_updated_at < ('{date_to}'::date + INTERVAL '1 day')")

        # ── Silmatha where clauses ────────────────────────────────────────
        s_where = ["(s.sil_is_deleted = false OR s.sil_is_deleted IS NULL)"]

        if province_code:
            s_where.append(f"s.sil_province = '{province_code}'")
        if district_code:
            s_where.append(f"s.sil_district = '{district_code}'")
        if search and search.strip():
            sv = search.strip().replace("'", "''")
            s_where.append(
                f"(s.sil_gihiname ILIKE '%{sv}%' OR s.sil_mahananame ILIKE '%{sv}%' OR s.sil_regn ILIKE '%{sv}%')"
            )
        if date_from:
            s_where.append(f"s.sil_updated_at >= '{date_from}'")
        if date_to:
            s_where.append(f"s.sil_updated_at < ('{date_to}'::date + INTERVAL '1 day')")

        # ── Decide which tables to include ────────────────────────────────
        pt = (person_type or "").upper()
        # If nikaya/parshawa filter is active, silmatha has no such FK → skip silmatha
        has_nikaya_filter = bool(nikaya_code or parshawa_code)

        include_bhikku   = pt in ("", "BHIKKU")
        include_silmatha = pt in ("", "SILMATHA") and not has_nikaya_filter

        parts = []

        # ── Bhikku subquery ───────────────────────────────────────────────
        if include_bhikku:
            parts.append(f"""
                SELECT
                    b.br_id::text                              AS person_id,
                    b.br_regn                                  AS reg_no,
                    'BHIKKU'                                   AS person_type,
                    COALESCE(NULLIF(b.br_mahananame,''), b.br_gihiname) AS name,
                    b.br_gihiname                              AS lay_name,
                    b.br_mahananame                            AS ordained_name,
                    b.br_dofb::text                            AS dob,
                    b.br_mobile                                AS mobile,
                    nk.nk_nname                                AS nikaya_name,
                    pr.pr_pname                                AS parshawa_name,
                    v.vh_vname                                 AS vihara_name,
                    prov.cp_name                               AS province_name,
                    dist.dd_dname                              AS district_name,
                    b.br_cat                                   AS category,
                    b.br_currstat                              AS status,
                    b.br_updated_at::text                      AS updated_at
                FROM bhikku_regist b
                LEFT JOIN cmm_nikayadata    nk   ON nk.nk_nkn    = b.br_nikaya
                LEFT JOIN cmm_parshawadata  pr   ON pr.pr_prn     = b.br_parshawaya
                LEFT JOIN vihaddata         v    ON v.vh_trn      = b.br_livtemple
                LEFT JOIN cmm_province      prov ON prov.cp_code  = b.br_province
                LEFT JOIN cmm_districtdata  dist ON dist.dd_dcode = b.br_district
                WHERE {' AND '.join(b_where)}
            """)

        # ── Silmatha subquery ─────────────────────────────────────────────
        if include_silmatha:
            parts.append(f"""
                SELECT
                    s.sil_id::text                               AS person_id,
                    s.sil_regn                                   AS reg_no,
                    'SILMATHA'                                   AS person_type,
                    COALESCE(NULLIF(s.sil_mahananame,''), s.sil_gihiname) AS name,
                    s.sil_gihiname                               AS lay_name,
                    s.sil_mahananame                             AS ordained_name,
                    s.sil_dofb::text                             AS dob,
                    s.sil_mobile                                 AS mobile,
                    NULL                                         AS nikaya_name,
                    NULL                                         AS parshawa_name,
                    v.vh_vname                                   AS vihara_name,
                    prov.cp_name                                 AS province_name,
                    dist.dd_dname                                AS district_name,
                    s.sil_cat                                    AS category,
                    s.sil_currstat                               AS status,
                    s.sil_updated_at::text                       AS updated_at
                FROM silmatha_regist s
                LEFT JOIN vihaddata         v    ON v.vh_trn      = s.sil_robing_after_residence_temple
                LEFT JOIN cmm_province      prov ON prov.cp_code  = s.sil_province
                LEFT JOIN cmm_districtdata  dist ON dist.dd_dcode = s.sil_district
                WHERE {' AND '.join(s_where)}
            """)

        if not parts:
            return []

        sql = " UNION ALL ".join(parts) + f" ORDER BY name LIMIT {limit}"
        result = await self.db.execute(text(sql))
        rows = result.fetchall()

        return [
            PersonListItem(
                person_id=row[0],
                reg_no=row[1],
                person_type=row[2],
                name=row[3],
                lay_name=row[4],
                ordained_name=row[5],
                dob=str(row[6])[:10] if row[6] else None,
                mobile=row[7],
                nikaya_name=row[8],
                parshawa_name=row[9],
                vihara_name=row[10],
                province_name=row[11],
                district_name=row[12],
                category=row[13],
                status=row[14],
                updated_at=str(row[15])[:19] if row[15] else None,
            )
            for row in rows
        ]
