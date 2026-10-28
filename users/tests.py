from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import ParentLink, Student, User


class ModelTests(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user("nanay", password="x", role=User.Role.PARENT)
        self.student = Student.objects.create(
            lrn="123456789012", first_name="Maria", last_name="Cruz",
            grade_level=7, section="Rizal",
        )

    def test_default_role_is_parent(self):
        self.assertEqual(User.objects.create_user("u1", password="x").role, "parent")

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
