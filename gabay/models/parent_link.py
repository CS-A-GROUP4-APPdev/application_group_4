"""MODEL: ParentLink. Connects a parent account to a student, with consent."""
from django.db import DatabaseError, models, transaction
from django.db.models import Count, Q
from django.utils import timezone

from gabay.models.student import Student
from gabay.models.user import User
from libraries import stored_procedure


class ParentLinkManager(models.Manager):
    def link_parent(self, parent_id, student_id, relationship, consent=False):
        """Link a parent account to a student. Raises ValueError on invalid input."""
        if stored_procedure.supported():
            try:
                with transaction.atomic():
                    stored_procedure.call_procedure("sp_link_parent", [parent_id, student_id, relationship, consent])
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

    def count_waiting_for(self, parent):
        """How many of this parent's links still wait for consent. Only a count:
        a link without consent must not reveal anything about the student."""
        return self.filter(parent=parent, consent_given=False).count()

    def consent_summary(self):
        """School-wide totals: ``{"with_consent": n, "no_consent": n}``."""
        return self.aggregate(
            with_consent=Count("id", filter=Q(consent_given=True)),
            no_consent=Count("id", filter=Q(consent_given=False)),
        )


class ParentLink(models.Model):
    """Connects a parent account to a student. Parents may only see linked students."""

    parent = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={"role": "parent"}, related_name="parent_links",
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parent_links")
    relationship = models.CharField(max_length=50, help_text="e.g. Mother, Father, Guardian")
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ParentLinkManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["parent", "student"], name="unique_parent_student")
        ]

    def __str__(self):
        return f"{self.parent} -> {self.student}"
