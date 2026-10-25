"""Stored procedure and function for PostgreSQL.

- sp_link_parent(...)       PROCEDURE: validates and links a parent to a student.
- fn_students_of_parent(id) FUNCTION : returns only the students a parent may see.

On SQLite (no stored procedure support) this migration does nothing, and the
Python methods in users/managers.py use the ORM instead.
"""
from django.db import migrations

CREATE_SQL = """
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
"""

DROP_SQL = """
DROP FUNCTION IF EXISTS fn_students_of_parent(bigint);
DROP PROCEDURE IF EXISTS sp_link_parent(bigint, bigint, varchar, boolean);
"""


def create(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(CREATE_SQL, params=None)


def drop(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(DROP_SQL, params=None)


class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]
    operations = [migrations.RunPython(create, drop)]
