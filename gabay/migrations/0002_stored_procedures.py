"""Stored procedure and function for PostgreSQL.

- sp_link_parent(...)       PROCEDURE: validates and links a parent to a student.
- fn_students_of_parent(id) FUNCTION : returns only the students a parent may see.

The SQL lives in assets/stored_procedure/*.sql so it can be read and reviewed as plain SQL.
On SQLite (no stored procedure support) this migration does nothing, and the Python
methods in the Model files use the ORM instead.
"""
from pathlib import Path

from django.conf import settings
from django.db import migrations

SQL_DIR = Path(settings.BASE_DIR) / "assets" / "stored_procedure"
SQL_FILES = ["sp_link_parent.sql", "fn_students_of_parent.sql"]

DROP_SQL = """
DROP FUNCTION IF EXISTS fn_students_of_parent(bigint);
DROP PROCEDURE IF EXISTS sp_link_parent(bigint, bigint, varchar, boolean);
"""


def create(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        for name in SQL_FILES:
            schema_editor.execute((SQL_DIR / name).read_text(encoding="utf-8"), params=None)


def drop(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(DROP_SQL, params=None)


class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]
    operations = [migrations.RunPython(create, drop)]
