"""MODEL: Section. A class section such as Grade 7 - Rizal."""
from django.db import models

from gabay.models.student import GRADE_LEVEL_CHOICES
from gabay.models.user import User


class Section(models.Model):
    """A class section such as Grade 7 - Rizal, with an optional adviser."""

    name = models.CharField(max_length=50)
    grade_level = models.PositiveSmallIntegerField(choices=GRADE_LEVEL_CHOICES)
    adviser = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={"role": User.Role.ADVISER}, related_name="advised_sections",
    )

    class Meta:
        ordering = ["grade_level", "name"]
        constraints = [
            models.UniqueConstraint(fields=["grade_level", "name"], name="unique_section_per_grade")
        ]

    def __str__(self):
        return f"{self.get_grade_level_display()} - {self.name}"
