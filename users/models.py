from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role. Every account in Gabay has exactly one role."""

    class Role(models.TextChoices):
        PARENT = "parent", "Parent/Guardian"
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Subject Teacher"
        ADVISER = "adviser", "Adviser"
        PRINCIPAL = "principal", "Principal/Guidance"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARENT)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class Student(models.Model):
    lrn = models.CharField("LRN", max_length=12, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    grade_level = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=50)
    # Optional: the student's own login account (for the student goal-setting view)
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={"role": "student"}, related_name="student_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["grade_level", "section", "last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.lrn})"


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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["parent", "student"], name="unique_parent_student")
        ]

    def __str__(self):
        return f"{self.parent} -> {self.student}"
