-- ============================================================
-- sp_link_parent.sql
-- Gabay: link a parent account to a student (PROCEDURE)
-- Run by gabay/migrations/0002_stored_procedures.py (PostgreSQL only).
-- ============================================================

CREATE OR REPLACE PROCEDURE sp_link_parent(
    p_parent_id    bigint,
    p_student_id   bigint,
    p_relationship varchar,
    p_consent      boolean
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_role varchar;
BEGIN
    SELECT role INTO v_role FROM users_user WHERE id = p_parent_id;
    IF v_role IS NULL THEN
        RAISE EXCEPTION 'User % does not exist', p_parent_id;
    END IF;
    IF v_role <> 'parent' THEN
        RAISE EXCEPTION 'User % has role %, only parent accounts can be linked', p_parent_id, v_role;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM users_student WHERE id = p_student_id) THEN
        RAISE EXCEPTION 'Student % does not exist', p_student_id;
    END IF;

    INSERT INTO users_parentlink
        (parent_id, student_id, relationship, consent_given, consent_date, created_at)
    VALUES
        (p_parent_id, p_student_id, p_relationship, p_consent,
         CASE WHEN p_consent THEN now() ELSE NULL END, now())
    ON CONFLICT (parent_id, student_id) DO UPDATE
        SET relationship  = EXCLUDED.relationship,
            consent_given = EXCLUDED.consent_given,
            consent_date  = CASE WHEN EXCLUDED.consent_given THEN now() ELSE NULL END;
END;
$$;
