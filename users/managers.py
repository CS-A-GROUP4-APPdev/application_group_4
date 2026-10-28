"""Model-layer wrappers around the stored procedure and function.

Views never contain raw SQL. They call these methods. On PostgreSQL the methods
call the stored procedure/function; on SQLite they use the ORM with the same rules.
"""
from django.db import connection, models, transaction
from django.utils import timezone


class StudentManager(models.Manager):
    def for_parent(self, parent_id):
        """Students a parent may see (consent must be given)."""
        if connection.vendor == "postgresql":
            with connection.cursor() as cur:
                cur.execute("SELECT student_id FROM fn_students_of_parent(%s)", [parent_id])
                ids = [row[0] for row in cur.fetchall()]
            return self.filter(id__in=ids)
        return self.filter(parent_links__parent_id=parent_id, parent_links__consent_given=True)


class ParentLinkManager(models.Manager):
    def link_parent(self, parent_id, student_id, relationship, consent=False):
        """Link a parent account to a student. Raises ValueError on invalid input."""
        from django.db import DatabaseError
        from .models import Student, User

        if connection.vendor == "postgresql":
            try:
                with transaction.atomic(), connection.cursor() as cur:
                    cur.execute("CALL sp_link_parent(%s, %s, %s, %s)",
                                [parent_id, student_id, relationship, consent])
            except DatabaseError as exc:
                raise ValueError(str(exc).splitlines()[0]) from exc
            return self.get(parent_id=parent_id, student_id=student_id)

        parent = User.objects.filter(pk=parent_id).first()
        if parent is None:
            raise ValueError(f"User {parent_id} does not exist")
        if parent.role != User.Role.PARENT:
            raise ValueError(f"User {parent_id} has role {parent.role}, only parent accounts can be linked")
        if not Student.objects.filter(pk=student_id).exists():
            raise ValueError(f"Student {student_id} does not exist")
        link, _ = self.update_or_create(
            parent_id=parent_id, student_id=student_id,
            defaults={"relationship": relationship, "consent_given": consent,
                      "consent_date": timezone.now() if consent else None},
        )
        return link
