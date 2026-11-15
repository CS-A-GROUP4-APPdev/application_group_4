"""MODEL: Attendance. Per-subject, per-period records, one row per student, subject, date, and period."""
from django.core.validators import MinValueValidator
from django.db import models

from gabay.models.student import Student
from gabay.models.subject import Subject


class AttendanceManager(models.Manager):
    def for_student(self, student):
        """All attendance records of one student, newest first, with the subject loaded."""
        return self.filter(student=student).select_related("subject")

    def recent_for_student(self, student, limit=30):
        """The newest ``limit`` records of one student."""
        return self.for_student(student)[:limit]

    def count_absent_on(self, students, day):
        """How many of ``students`` were marked absent on ``day``."""
        return self.filter(student__in=students, date=day, status=Attendance.Status.ABSENT).count()


class Attendance(models.Model):
    """Per-subject, per-period attendance. One row per student, subject, date, and period."""

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="attendance_records")
    date = models.DateField()
    period = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], help_text="Class period, starting at 1")
    status = models.CharField(max_length=10, choices=Status.choices)

    objects = AttendanceManager()

    class Meta:
        ordering = ["-date", "period"]
        verbose_name_plural = "attendance records"
        constraints = [
            # Database-level rule: no duplicate record for the same student, subject, date, and period.
            models.UniqueConstraint(
                fields=["student", "subject", "date", "period"],
                name="unique_attendance_per_period",
            )
        ]

    def __str__(self):
        return f"{self.student} {self.subject} {self.date} P{self.period}: {self.status}"
