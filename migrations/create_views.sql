-- =============================================
-- Buddhist Affairs MIS Dashboard - Materialized Views
-- =============================================
-- These views optimize dashboard queries for large-scale usage
-- Run these in the dbhrms-ranjith database
-- =============================================

-- =============================================
-- 1. OVERALL SUMMARY VIEW (Section 1 - Summary A)
-- =============================================

-- Drop if exists
DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_type_summary CASCADE;

-- Create the view
CREATE MATERIALIZED VIEW mv_dashboard_type_summary AS
SELECT 
    'bikku' as type_key,
    'Bikku' as type_name,
    'bhikku' as icon,
    COUNT(*) as total
FROM bhikku_regist 
WHERE br_is_deleted = false OR br_is_deleted IS NULL

UNION ALL

SELECT 
    'silmatha' as type_key,
    'Silmatha' as type_name,
    'silmatha' as icon,
    COUNT(*) as total
FROM silmatha_regist 
WHERE sil_is_deleted = false OR sil_is_deleted IS NULL

UNION ALL

SELECT 
    'vihara' as type_key,
    'Vihara' as type_name,
    'temple' as icon,
    COUNT(*) as total
FROM vihaddata 
WHERE vh_is_deleted = false OR vh_is_deleted IS NULL

UNION ALL

SELECT 
    'arama' as type_key,
    'Arama' as type_name,
    'arama' as icon,
    COUNT(*) as total
FROM aramadata 
WHERE ar_is_deleted = false OR ar_is_deleted IS NULL

UNION ALL

SELECT 
    'ssbm' as type_key,
    'SSBM' as type_name,
    'ssbm' as icon,
    COUNT(*) as total
FROM sasanarakshana_regist
WHERE sar_is_deleted = false OR sar_is_deleted IS NULL

UNION ALL

-- Placeholder for Dahampasal Teachers (table not created yet)
SELECT 
    'dahampasal_teachers' as type_key,
    'Dahampasal Teachers' as type_name,
    'teacher' as icon,
    0 as total

UNION ALL

-- Placeholder for Dahampasal Students (table not created yet)
SELECT 
    'dahampasal_students' as type_key,
    'Dahampasal Student' as type_name,
    'student' as icon,
    0 as total

UNION ALL

-- Placeholder for Dahampasal (table not created yet)
SELECT 
    'dahampasal' as type_key,
    'Dahampasal' as type_name,
    'school' as icon,
    0 as total;

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX idx_mv_dashboard_type_summary ON mv_dashboard_type_summary(type_key);


-- =============================================
-- 2. NIKAYA SUMMARY VIEW (Section 1 - Summary B)
-- =============================================

DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_nikaya_summary CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_nikaya_summary AS
-- First, get nikaya from cmm_nikayadata with proper names
SELECT
    n.nk_nkn as nikaya_code,
    n.nk_nname as nikaya_name,
    COUNT(DISTINCT v.vh_trn) as vihara_count,
    COUNT(DISTINCT b.br_regn) as bikku_count
FROM cmm_nikayadata n
LEFT JOIN vihaddata v ON v.vh_nikaya = n.nk_nkn AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
LEFT JOIN bhikku_regist b ON b.br_nikaya = n.nk_nkn AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
WHERE n.nk_is_deleted = false OR n.nk_is_deleted IS NULL
GROUP BY n.nk_nkn, n.nk_nname

UNION ALL

-- Then, get nikaya codes from bhikku_regist that don't exist in cmm_nikayadata
-- Uses pre-aggregated subqueries to avoid a massive cross-join on large tables
SELECT
    COALESCE(b_grp.br_nikaya, 'UNASSIGNED') as nikaya_code,
    CASE 
        WHEN b_grp.br_nikaya = 'NK001' THEN 'NK001 - Main Order'
        WHEN b_grp.br_nikaya = 'NK002' THEN 'NK002 - Main Order'
        WHEN b_grp.br_nikaya = 'NK003' THEN 'NK003 - Main Order'
        WHEN b_grp.br_nikaya = 'KJK' THEN 'KJK - Other'
        WHEN b_grp.br_nikaya = 'KSD' THEN 'KSD - Other'
        WHEN b_grp.br_nikaya = 'SLA' THEN 'SLA - Other'
        WHEN b_grp.br_nikaya = 'SWJ' THEN 'SWJ - Other'
        WHEN b_grp.br_nikaya IS NULL THEN 'Unassigned'
        ELSE COALESCE(b_grp.br_nikaya, 'Unknown')
    END as nikaya_name,
    COALESCE(v_grp.vihara_count, 0) as vihara_count,
    b_grp.bikku_count
FROM (
    SELECT br_nikaya, COUNT(DISTINCT br_regn) as bikku_count
    FROM bhikku_regist
    WHERE (br_is_deleted = false OR br_is_deleted IS NULL)
      AND (
          br_nikaya IS NULL
          OR br_nikaya NOT IN (
              SELECT nk_nkn FROM cmm_nikayadata
              WHERE nk_is_deleted = false OR nk_is_deleted IS NULL
          )
      )
    GROUP BY br_nikaya
) b_grp
LEFT JOIN (
    SELECT vh_nikaya, COUNT(DISTINCT vh_trn) as vihara_count
    FROM vihaddata
    WHERE vh_is_deleted = false OR vh_is_deleted IS NULL
    GROUP BY vh_nikaya
) v_grp ON v_grp.vh_nikaya = b_grp.br_nikaya;

CREATE UNIQUE INDEX idx_mv_dashboard_nikaya_summary ON mv_dashboard_nikaya_summary(nikaya_code);


-- =============================================
-- 3. VIHARA GRADING VIEW (Section 1 - Summary C)
-- =============================================

DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_grade_summary CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_grade_summary AS
SELECT 
    vh_typ as grade,
    CASE 
        WHEN vh_typ = 'A' THEN 'Grade A'
        WHEN vh_typ = 'B' THEN 'Grade B'
        WHEN vh_typ = 'C' THEN 'Grade C'
        WHEN vh_typ = 'D' THEN 'Grade D'
        ELSE 'Unknown'
    END as grade_name,
    COUNT(*) as total
FROM vihaddata
WHERE (vh_is_deleted = false OR vh_is_deleted IS NULL)
  AND vh_typ IS NOT NULL
GROUP BY vh_typ;

CREATE UNIQUE INDEX idx_mv_dashboard_grade_summary ON mv_dashboard_grade_summary(grade);


-- =============================================
-- 4. PROVINCE GEOGRAPHIC VIEW (Section 2)
-- =============================================

DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_province_summary CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_province_summary AS
SELECT 
    p.cp_code as province_code,
    p.cp_name as province_name,
    COALESCE(v.vihara_count, 0) as vihara_count,
    COALESCE(b.bikku_count, 0) as bikku_count,
    COALESCE(s.silmatha_count, 0) as silmatha_count,
    COALESCE(a.arama_count, 0) as arama_count,
    COALESCE(ssbm.ssbm_count, 0) as ssbm_count,
    0 as dahampasal_teachers_count,
    0 as dahampasal_students_count,
    0 as dahampasal_count
FROM cmm_province p
LEFT JOIN (
    SELECT vh_province, COUNT(*) as vihara_count 
    FROM vihaddata WHERE vh_is_deleted = false OR vh_is_deleted IS NULL
    GROUP BY vh_province
) v ON v.vh_province = p.cp_code
LEFT JOIN (
    SELECT br_province, COUNT(*) as bikku_count 
    FROM bhikku_regist WHERE br_is_deleted = false OR br_is_deleted IS NULL
    GROUP BY br_province
) b ON b.br_province = p.cp_code
LEFT JOIN (
    SELECT sil_province, COUNT(*) as silmatha_count 
    FROM silmatha_regist WHERE sil_is_deleted = false OR sil_is_deleted IS NULL
    GROUP BY sil_province
) s ON s.sil_province = p.cp_code
LEFT JOIN (
    SELECT ar_province, COUNT(*) as arama_count 
    FROM aramadata WHERE ar_is_deleted = false OR ar_is_deleted IS NULL
    GROUP BY ar_province
) a ON a.ar_province = p.cp_code
LEFT JOIN (
    SELECT v2.vh_province, COUNT(*) as ssbm_count 
    FROM sasanarakshana_regist sar
    JOIN vihaddata v2 ON sar.sar_temple_trn = v2.vh_trn
    WHERE sar.sar_is_deleted = false OR sar.sar_is_deleted IS NULL
    GROUP BY v2.vh_province
) ssbm ON ssbm.vh_province = p.cp_code
WHERE p.cp_is_deleted = false OR p.cp_is_deleted IS NULL;

CREATE UNIQUE INDEX idx_mv_dashboard_province_summary ON mv_dashboard_province_summary(province_code);


-- =============================================
-- 5. DISTRICT GEOGRAPHIC VIEW (Section 2)
-- =============================================

DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_district_summary CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_district_summary AS
SELECT 
    d.dd_dcode as district_code,
    d.dd_dname as district_name,
    d.dd_prcode as province_code,
    COALESCE(v.vihara_count, 0) as vihara_count,
    COALESCE(b.bikku_count, 0) as bikku_count,
    COALESCE(s.silmatha_count, 0) as silmatha_count,
    COALESCE(a.arama_count, 0) as arama_count,
    COALESCE(ssbm.ssbm_count, 0) as ssbm_count,
    0 as dahampasal_teachers_count,
    0 as dahampasal_students_count,
    0 as dahampasal_count
FROM cmm_districtdata d
LEFT JOIN (
    SELECT vh_district, COUNT(*) as vihara_count 
    FROM vihaddata WHERE vh_is_deleted = false OR vh_is_deleted IS NULL
    GROUP BY vh_district
) v ON v.vh_district = d.dd_dcode
LEFT JOIN (
    SELECT br_district, COUNT(*) as bikku_count 
    FROM bhikku_regist WHERE br_is_deleted = false OR br_is_deleted IS NULL
    GROUP BY br_district
) b ON b.br_district = d.dd_dcode
LEFT JOIN (
    SELECT sil_district, COUNT(*) as silmatha_count 
    FROM silmatha_regist WHERE sil_is_deleted = false OR sil_is_deleted IS NULL
    GROUP BY sil_district
) s ON s.sil_district = d.dd_dcode
LEFT JOIN (
    SELECT ar_district, COUNT(*) as arama_count 
    FROM aramadata WHERE ar_is_deleted = false OR ar_is_deleted IS NULL
    GROUP BY ar_district
) a ON a.ar_district = d.dd_dcode
LEFT JOIN (
    SELECT v2.vh_district, COUNT(*) as ssbm_count 
    FROM sasanarakshana_regist sar
    JOIN vihaddata v2 ON sar.sar_temple_trn = v2.vh_trn
    WHERE sar.sar_is_deleted = false OR sar.sar_is_deleted IS NULL
    GROUP BY v2.vh_district
) ssbm ON ssbm.vh_district = d.dd_dcode
WHERE d.dd_is_deleted = false OR d.dd_is_deleted IS NULL;

CREATE UNIQUE INDEX idx_mv_dashboard_district_summary ON mv_dashboard_district_summary(district_code);


-- =============================================
-- 6. BIKKU TYPE BREAKDOWN VIEW (Section 2)
-- =============================================

DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_bikku_types CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_bikku_types AS
-- Samanera: Monks who are only in bhikku_regist (not in high_regist)
SELECT 
    'samanera' as type_key,
    'Samanera' as type_name,
    COUNT(*) as total
FROM bhikku_regist b
WHERE (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
  AND NOT EXISTS (
      SELECT 1 FROM bhikku_high_regist bh 
      WHERE bh.bhr_samanera_serial_no = b.br_regn
        AND (bh.bhr_is_deleted = false OR bh.bhr_is_deleted IS NULL)
  )

UNION ALL

-- Upasampada: Monks who are in high_regist
SELECT 
    'upasampada' as type_key,
    'Upasampada' as type_name,
    COUNT(*) as total
FROM bhikku_high_regist
WHERE bhr_is_deleted = false OR bhr_is_deleted IS NULL

UNION ALL

-- Upavidi (placeholder - criteria not specified)
SELECT 
    'upavidi' as type_key,
    'Upavidi' as type_name,
    0 as total;

CREATE UNIQUE INDEX idx_mv_dashboard_bikku_types ON mv_dashboard_bikku_types(type_key);


-- =============================================
-- 7. PARSHAWA SUMMARY VIEW (Section 3)
-- =============================================

DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_parshawa_summary CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_parshawa_summary AS
SELECT
    p.pr_prn as parshawa_code,
    p.pr_pname as parshawa_name,
    COUNT(DISTINCT v.vh_trn) as vihara_count,
    COUNT(DISTINCT b.br_regn) as bikku_count
FROM cmm_parshawadata p
LEFT JOIN vihaddata v ON v.vh_parshawa = p.pr_prn AND (v.vh_is_deleted = false OR v.vh_is_deleted IS NULL)
LEFT JOIN bhikku_regist b ON b.br_parshawaya = p.pr_prn AND (b.br_is_deleted = false OR b.br_is_deleted IS NULL)
WHERE p.pr_is_deleted = false OR p.pr_is_deleted IS NULL
GROUP BY p.pr_prn, p.pr_pname

UNION ALL

SELECT 
    'NOT_ASSIGNED' as parshawa_code,
    'No Parshawa' as parshawa_name,
    COUNT(DISTINCT v.vh_trn) as vihara_count,
    COUNT(DISTINCT b.br_regn) as bikku_count
FROM vihaddata v
FULL OUTER JOIN bhikku_regist b ON 1=0
WHERE (v.vh_parshawa IS NULL OR v.vh_parshawa = '')
   OR (b.br_parshawaya IS NULL OR b.br_parshawaya = '');

CREATE UNIQUE INDEX idx_mv_dashboard_parshawa_summary ON mv_dashboard_parshawa_summary(parshawa_code);

-- =============================================
-- REFRESH FUNCTION
-- =============================================

CREATE OR REPLACE FUNCTION refresh_dashboard_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_type_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_nikaya_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_grade_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_province_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_district_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_bikku_types;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_parshawa_summary;
END;
$$ LANGUAGE plpgsql;


-- =============================================
-- GRANT PERMISSIONS
-- =============================================

GRANT SELECT ON mv_dashboard_type_summary TO app_admin;
GRANT SELECT ON mv_dashboard_nikaya_summary TO app_admin;
GRANT SELECT ON mv_dashboard_grade_summary TO app_admin;
GRANT SELECT ON mv_dashboard_province_summary TO app_admin;
GRANT SELECT ON mv_dashboard_district_summary TO app_admin;
GRANT SELECT ON mv_dashboard_bikku_types TO app_admin;
GRANT SELECT ON mv_dashboard_parshawa_summary TO app_admin;


-- =============================================
-- INITIAL DATA REFRESH
-- =============================================
-- Views are already populated on creation above.
-- Call refresh_dashboard_views() manually when needed,
-- or schedule via pg_cron: cron.schedule('0 * * * *', 'SELECT refresh_dashboard_views();')

-- =============================================
-- NOTES:
-- 1. Run this script once to create all views
-- 2. Call refresh_dashboard_views() periodically to update data
-- 3. For automatic refresh, set up pg_cron:
--    SELECT cron.schedule('*/5 * * * *', 'SELECT refresh_dashboard_views()');
-- =============================================
