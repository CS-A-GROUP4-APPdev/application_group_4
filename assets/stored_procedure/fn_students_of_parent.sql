-- ============================================================
-- fn_students_of_parent.sql
-- Gabay: students a parent may see, consent required (FUNCTION)
-- Run by gabay/migrations/0002_stored_procedures.py (PostgreSQL only).
-- ============================================================

CREATE OR REPLACE FUNCTION fn_students_of_parent(p_parent_id bigint)
RETURNS TABLE (
    student_id   bigint,
    lrn          varchar,
    first_name   varchar,
    last_name    varchar,
    grade_level  smallint,
    section      varchar,
    relationship varchar
)
LANGUAGE sql
STABLE
AS $$
    SELECT s.id, s.lrn, s.first_name, s.last_name, s.grade_level, s.section, pl.relationship
    FROM users_parentlink pl
    JOIN users_student s ON s.id = pl.student_id
    WHERE pl.parent_id = p_parent_id
      AND pl.consent_given = TRUE
    ORDER BY s.last_name, s.first_name;
$$;
