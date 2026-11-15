"""MODEL: Student.

Also the ONE place that decides which students a user may see (``Student.objects.visible_to``).
Controllers must never query ``Student.objects`` directly to show student data.
"""
from django.db import models
from django.db.models import Count, Q

from gabay.models.user import STAFF_ROLES, User, effective_role
from libraries import stored_procedure


# Grouped choices for Student.grade_level. Stored as integers so ordering and
# range comparisons keep working; College has no single grade, so it uses 13.
GRADE_COLLEGE = 13

GRADE_LEVEL_CHOICES = [
    ("Grade 1-10", [(n, f"Grade {n}") for n in range(1, 11)]),
    ("Senior High", [(11, "Grade 11"), (12, "Grade 12")]),
    ("College", [(GRADE_COLLEGE, "College")]),
]


class StudentQuerySet(models.QuerySet):
    def for_parent(self, parent_id):
        """Students a parent may see (consent must be given)."""
        if stored_procedure.supported():
            rows = stored_procedure.call_function("fn_students_of_parent", [parent_id], columns="student_id")
            return self.filter(id__in=[row[0] for row in rows])
        return self.filter(parent_links__parent_id=parent_id, parent_links__consent_given=True)

    def visible_to(self, user):
        """The students this user is allowed to view. THE privacy rule.

        - Not logged in, or inactive account: nobody.
        - Parent: only linked students WITH consent. No consent means nothing is shown.
        - Student: own record only.
        - Teacher, adviser, principal, admin, superuser: all students (until sections and
          teacher assignments are linked to students).
        """
        if not getattr(user, "is_authenticated", False) or not user.is_active:
            return self.none()

        role = effective_role(user)
        if role == User.Role.PARENT:
            return self.for_parent(user.id)
        if role == User.Role.STUDENT:
            return self.filter(user_id=user.id)
        if role in STAFF_ROLES:
            return self.all()
        return self.none()

    def with_attendance_counts(self):
        """Add ``absences`` and ``lates`` counts to each student."""
        from gabay.models.attendance import Attendance  # avoid a circular import

        return self.annotate(
            absences=Count("attendance_records", filter=Q(attendance_records__status=Attendance.Status.ABSENT)),
            lates=Count("attendance_records", filter=Q(attendance_records__status=Attendance.Status.LATE)),
        )

    def count_by_grade_level(self):
        """Rows of ``{"grade_level": 7, "total": 12}``, lowest grade first."""
        return self.order_by().values("grade_level").annotate(total=Count("id")).order_by("grade_level")


StudentManager = models.Manager.from_queryset(StudentQuerySet)


class Student(models.Model):
    lrn = models.CharField("LRN", max_length=12, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    grade_level = models.PositiveSmallIntegerField(choices=GRADE_LEVEL_CHOICES)
    section = models.CharField(max_length=50)
    # Optional: the student's own login account (for the student goal-setting view)
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={"role": "student"}, related_name="student_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = StudentManager()

    class Meta:
        ordering = ["grade_level", "section", "last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.lrn})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
