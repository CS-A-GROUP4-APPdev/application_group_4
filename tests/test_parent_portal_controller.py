"""ParentPortal controller tests: the portal page, the child's records page, and the student API."""
from django.test import TestCase
from django.urls import reverse

from gabay.models import ParentLink
from tests.base import PrivacyFixtureMixin


class ParentPortalPageTests(PrivacyFixtureMixin, TestCase):
    def test_parent_portal_lists_only_consented_children(self):
        self.login(self.nanay)
        r = self.client.get(reverse("parent_portal:index"))
        self.assertContains(r, "Maria Cruz")
        self.assertNotContains(r, "Jose Reyes")
        self.assertNotContains(r, "Ana Lim")

    def test_parent_portal_tells_parent_about_waiting_link_without_naming_student(self):
        self.login(self.nanay)
        r = self.client.get(reverse("parent_portal:index"))
        self.assertContains(r, "1 link waiting for consent")
        self.assertNotContains(r, "Jose")
        self.assertNotContains(r, "222222222222")

    def test_parent_with_only_unconsented_links_sees_no_student_information(self):
        ParentLink.objects.link_parent(self.nanay.id, self.maria.id, "Mother", consent=False)
        self.login(self.nanay)
        r = self.client.get(reverse("parent_portal:index"))
        self.assertNotContains(r, "Maria")
        self.assertContains(r, "No students are linked")
        self.assertEqual(self.client.get(reverse("parent_portal:student_detail", args=[self.maria.pk])).status_code, 404)


class StudentDetailPageTests(PrivacyFixtureMixin, TestCase):
    def test_parent_cannot_open_unconsented_or_unlinked_student(self):
        self.login(self.nanay)
        for s in (self.jose, self.ana):
            self.assertEqual(self.client.get(reverse("parent_portal:student_detail", args=[s.pk])).status_code, 404, s)

    def test_parent_can_open_consented_child_with_records(self):
        self.login(self.nanay)
        r = self.client.get(reverse("parent_portal:student_detail", args=[self.maria.pk]))
        self.assertContains(r, "Mathematics")
        self.assertContains(r, "40.00 / 50.00")

    def test_student_can_open_only_own_record(self):
        self.login(self.stu_user)
        self.assertEqual(self.client.get(reverse("parent_portal:student_detail", args=[self.maria.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("parent_portal:student_detail", args=[self.jose.pk])).status_code, 404)

    def test_staff_can_open_any_student(self):
        self.login(self.teacher)
        for s in (self.maria, self.jose, self.ana):
            self.assertEqual(self.client.get(reverse("parent_portal:student_detail", args=[s.pk])).status_code, 200)

    def test_anonymous_cannot_open_student_detail(self):
        r = self.client.get(reverse("parent_portal:student_detail", args=[self.maria.pk]))
        self.assertEqual(r.status_code, 302)


class ApiPrivacyTests(PrivacyFixtureMixin, TestCase):
    def test_api_requires_login(self):
        self.assertIn(self.client.get("/api/students/").status_code, (401, 403))

    def test_parent_list_only_consented(self):
        self.login(self.nanay)
        data = self.client.get("/api/students/").json()
        self.assertEqual([s["lrn"] for s in data], ["111111111111"])

    def test_parent_detail_grades_attendance(self):
        self.login(self.nanay)
        self.assertEqual(self.client.get(f"/api/students/{self.maria.pk}/").status_code, 200)
        self.assertEqual(len(self.client.get(f"/api/students/{self.maria.pk}/grades/").json()), 1)
        self.assertEqual(len(self.client.get(f"/api/students/{self.maria.pk}/attendance/").json()), 1)

    def test_parent_cannot_reach_unconsented_student_via_any_endpoint(self):
        self.login(self.nanay)
        for suffix in ("", "grades/", "attendance/"):
            self.assertEqual(self.client.get(f"/api/students/{self.jose.pk}/{suffix}").status_code, 404, suffix)
            self.assertEqual(self.client.get(f"/api/students/{self.ana.pk}/{suffix}").status_code, 404, suffix)

    def test_staff_sees_all_via_api(self):
        self.login(self.teacher)
        self.assertEqual(len(self.client.get("/api/students/").json()), 3)
