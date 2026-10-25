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
