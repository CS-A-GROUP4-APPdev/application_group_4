"""MODEL layer tests: data rules, database constraints, and the privacy rule."""
from datetime import date

from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from gabay.models import Attendance, Grade, ParentLink, Section, Student, Subject, User
from tests.base import PrivacyFixtureMixin


class StudentModelTests(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user("nanay", password="x", role=User.Role.PARENT)
        self.student = Student.objects.create(
            lrn="123456789012", first_name="Maria", last_name="Cruz",
            grade_level=7, section="Rizal",
        )

    def test_parent_link_created_without_consent_by_default(self):
        link = ParentLink.objects.create(parent=self.parent, student=self.student, relationship="Mother")
        self.assertFalse(link.consent_given)

    def test_same_parent_cannot_link_same_student_twice(self):
        ParentLink.objects.create(parent=self.parent, student=self.student, relationship="Mother")
        with self.assertRaises(IntegrityError), transaction.atomic():
            ParentLink.objects.create(parent=self.parent, student=self.student, relationship="Mother")

    def test_lrn_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Student.objects.create(lrn="123456789012", first_name="X", last_name="Y",
                                   grade_level=7, section="Rizal")

    def test_section_str_and_unique_per_grade(self):
        s = Section.objects.create(name="Rizal", grade_level=7)
        self.assertEqual(str(s), "Grade 7 - Rizal")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Section.objects.create(name="Rizal", grade_level=7)


class ParentLinkProcedureTests(TestCase):
    """Run on both SQLite (ORM fallback) and PostgreSQL (stored procedure/function)."""

    def setUp(self):
        self.parent = User.objects.create_user("nanay", password="x", role=User.Role.PARENT)
        self.teacher = User.objects.create_user("sir", password="x", role=User.Role.TEACHER)
        self.maria = Student.objects.create(lrn="111111111111", first_name="Maria", last_name="Cruz",
                                            grade_level=7, section="Rizal")
        self.jose = Student.objects.create(lrn="222222222222", first_name="Jose", last_name="Reyes",
                                           grade_level=7, section="Rizal")

    def test_link_parent_creates_link_with_consent_date(self):
        link = ParentLink.objects.link_parent(self.parent.id, self.maria.id, "Mother", consent=True)
        self.assertTrue(link.consent_given)
        self.assertIsNotNone(link.consent_date)

    def test_link_parent_twice_updates_instead_of_duplicating(self):
        ParentLink.objects.link_parent(self.parent.id, self.maria.id, "Mother", consent=False)
        ParentLink.objects.link_parent(self.parent.id, self.maria.id, "Guardian", consent=True)
        self.assertEqual(ParentLink.objects.count(), 1)
        self.assertEqual(ParentLink.objects.get().relationship, "Guardian")

    def test_only_parent_accounts_can_be_linked(self):
        with self.assertRaises(ValueError):
            ParentLink.objects.link_parent(self.teacher.id, self.maria.id, "Mother")

    def test_unknown_student_is_rejected(self):
        with self.assertRaises(ValueError):
            ParentLink.objects.link_parent(self.parent.id, 99999, "Mother")

    def test_parent_sees_only_consented_linked_students(self):
        ParentLink.objects.link_parent(self.parent.id, self.maria.id, "Mother", consent=True)
        ParentLink.objects.link_parent(self.parent.id, self.jose.id, "Aunt", consent=False)
        self.assertEqual(list(Student.objects.for_parent(self.parent.id)), [self.maria])


class VisibleToTests(PrivacyFixtureMixin, TestCase):
    """Student.objects.visible_to(user): the one function that decides who may see which student."""

    def visible(self, user):
        return set(Student.objects.visible_to(user))

    def test_parent_sees_only_consented_linked_students(self):
        self.assertEqual(self.visible(self.nanay), {self.maria})
        self.assertEqual(self.visible(self.tatay), {self.jose})

    def test_parent_without_any_consent_sees_nothing(self):
        ParentLink.objects.link_parent(self.nanay.id, self.maria.id, "Mother", consent=False)
        self.assertEqual(self.visible(self.nanay), set())

    def test_parent_with_no_links_sees_nothing(self):
        lone = User.objects.create_user("lone", password="x", role=User.Role.PARENT)
        self.assertEqual(self.visible(lone), set())

    def test_student_sees_only_self(self):
        self.assertEqual(self.visible(self.stu_user), {self.maria})

    def test_staff_roles_and_superuser_see_all(self):
        everyone = {self.maria, self.jose, self.ana}
        for u in (self.teacher, self.adviser, self.principal, self.admin_user):
            self.assertEqual(self.visible(u), everyone, u.role)
        root = User.objects.create_superuser("root", password="x")  # role defaults to parent
        self.assertEqual(self.visible(root), everyone)

    def test_anonymous_and_inactive_see_nothing(self):
        self.assertEqual(self.visible(AnonymousUser()), set())
        self.teacher.is_active = False
        self.assertEqual(self.visible(self.teacher), set())


class GradeModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(lrn="111111111111", first_name="Maria", last_name="Cruz",
                                              grade_level=7, section="Rizal")
        self.math = Subject.objects.create(name="Mathematics")

    def test_grade_percentage(self):
        g = Grade.objects.create(student=self.student, subject=self.math, quarter=1,
                                 component="quiz", score=40, highest_possible_score=50)
        self.assertEqual(g.percentage, 80)

    def test_grade_score_cannot_exceed_highest_possible(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Grade.objects.create(student=self.student, subject=self.math, quarter=1,
                                 component="quiz", score=51, highest_possible_score=50)

    def test_grade_highest_possible_must_be_positive(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Grade.objects.create(student=self.student, subject=self.math, quarter=1,
                                 component="quiz", score=0, highest_possible_score=0)


class AttendanceModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(lrn="111111111111", first_name="Maria", last_name="Cruz",
                                              grade_level=7, section="Rizal")
        self.math = Subject.objects.create(name="Mathematics")
        self.english = Subject.objects.create(name="English")

    def attendance(self, **overrides):
        data = dict(student=self.student, subject=self.math, date=date(2026, 11, 3), period=1, status="present")
        data.update(overrides)
        return Attendance.objects.create(**data)

    def test_duplicate_attendance_is_blocked_by_the_database(self):
        self.attendance()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.attendance(status="absent")  # same student, subject, date, period

    def test_attendance_allowed_when_subject_date_or_period_differs(self):
        self.attendance()
        self.attendance(subject=self.english)
        self.attendance(period=2)
        self.attendance(date=date(2026, 11, 4))
        self.assertEqual(Attendance.objects.count(), 4)

    def test_attendance_constraint_exists_in_the_database(self):
        with connection.cursor() as cur:
            constraints = connection.introspection.get_constraints(cur, Attendance._meta.db_table)
        unique_sets = [c["columns"] for c in constraints.values() if c["unique"] and not c["primary_key"]]
        self.assertIn(["student_id", "subject_id", "date", "period"], unique_sets)
