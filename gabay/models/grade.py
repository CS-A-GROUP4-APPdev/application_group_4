"""MODEL: Grade. One scored item (a quiz, an exam, a project) for a student in a subject."""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from gabay.models.student import Student
from gabay.models.subject import Subject


class GradeManager(models.Manager):
    def for_student(self, student):
        """All grades of one student, with the subject loaded."""
        return self.filter(student=student).select_related("subject")


class Grade(models.Model):
    """One scored item (a quiz, an exam, a project) for a student in a subject."""

    class Quarter(models.IntegerChoices):
        Q1 = 1, "Quarter 1"
        Q2 = 2, "Quarter 2"
        Q3 = 3, "Quarter 3"
        Q4 = 4, "Quarter 4"

    class Component(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        EXAM = "exam", "Exam"
        PROJECT = "project", "Project"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="grades")
    quarter = models.PositiveSmallIntegerField(choices=Quarter.choices)
    component = models.CharField(max_length=20, choices=Component.choices)
    title = models.CharField(max_length=100, blank=True, help_text="e.g. Quiz 1")
    score = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    highest_possible_score = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = GradeManager()

    class Meta:
        ordering = ["student", "subject", "quarter", "component", "id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(highest_possible_score__gt=0),
                                   name="grade_highest_score_positive"),
            models.CheckConstraint(condition=models.Q(score__gte=0),
                                   name="grade_score_not_negative"),
            models.CheckConstraint(condition=models.Q(score__lte=models.F("highest_possible_score")),
                                   name="grade_score_within_highest"),
        ]

    def __str__(self):
        return f"{self.student} {self.subject} Q{self.quarter} {self.component}: {self.score}/{self.highest_possible_score}"

    @property
    def percentage(self):
        return round(self.score / self.highest_possible_score * 100, 1)
