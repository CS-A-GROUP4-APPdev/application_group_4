"""MODELS layer. One file per model, named as in the proposal (section 2.3).

Django finds the models through this file. Later files depend on earlier ones.
Models hold data and rules only: no requests, no pages, no JSON output.
"""
from gabay.models.user import STAFF_ROLES, User, effective_role  # noqa: F401
from gabay.models.student import GRADE_COLLEGE, GRADE_LEVEL_CHOICES, Student  # noqa: F401
from gabay.models.parent_link import ParentLink  # noqa: F401
from gabay.models.section import Section  # noqa: F401
from gabay.models.subject import Subject  # noqa: F401
from gabay.models.grade import Grade  # noqa: F401
from gabay.models.attendance import Attendance  # noqa: F401
