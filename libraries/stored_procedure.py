"""Shared database helper for stored procedures and functions.

Every Model that needs a PostgreSQL stored procedure or function goes through
this file instead of opening a cursor itself (the same job PdoMySql.php did in
the old clinic system).

The SQL for each procedure lives in ``assets/stored_procedure/*.sql``.
SQLite has no stored procedures, so callers check ``supported()`` first and use
the ORM instead.
"""
from django.db import connection


def supported():
    """True when the active database can run stored procedures (PostgreSQL)."""
    return connection.vendor == "postgresql"


def _placeholders(params):
    return ", ".join(["%s"] * len(params))


def _check_name(name):
    # Names are constants written in our own code, never user input. This guards against slips.
    if not name.replace("_", "").isalnum():
        raise ValueError(f"Invalid stored procedure name: {name!r}")


def call_procedure(name, params):
    """Run ``CALL name(params)``. Database errors propagate to the caller."""
    _check_name(name)
    with connection.cursor() as cur:
        cur.execute(f"CALL {name}({_placeholders(params)})", list(params))


def call_function(name, params, columns="*"):
    """Run ``SELECT columns FROM name(params)`` and return all rows as tuples."""
    _check_name(name)
    with connection.cursor() as cur:
        cur.execute(f"SELECT {columns} FROM {name}({_placeholders(params)})", list(params))
        return cur.fetchall()
