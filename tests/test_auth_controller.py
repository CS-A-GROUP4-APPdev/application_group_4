from django.test import TestCase
from django.urls import reverse

from gabay.models import User

from tests.base import PrivacyFixtureMixin


class UserModelTests(TestCase):
    def test_default_role_is_parent(self):
        self.assertEqual(User.objects.create_user("u1", password="x").role, "parent")


class LoginAndRedirectTests(PrivacyFixtureMixin, TestCase):
    def post_login(self, username, password="pw12345!", **extra):
        return self.client.post(reverse("auth:login"), {"username": username, "password": password}, **extra)

    def test_login_page_renders(self):
        r = self.client.get(reverse("auth:login"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Log in")

    def test_parent_redirects_to_parent_portal(self):
        self.assertRedirects(self.post_login("nanay"), reverse("parent_portal:index"))

    def test_staff_roles_redirect_to_staff_dashboard(self):
        for name in ("sir", "maam", "principal", "admin1"):
            self.client.logout()
            self.assertRedirects(self.post_login(name), reverse("report:dashboard"), msg_prefix=name)

    def test_student_redirects_to_own_record(self):
        self.assertRedirects(self.post_login("maria"), reverse("parent_portal:student_detail", args=[self.maria.pk]))

    def test_wrong_password_stays_on_login_with_error(self):
        r = self.post_login("nanay", "wrong")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Wrong username or password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logged_in_user_visiting_login_is_sent_home(self):
        self.login(self.nanay)
        self.assertRedirects(self.client.get(reverse("auth:login")), reverse("parent_portal:index"))

    def test_logout_ends_session_and_shows_page(self):
        self.login(self.nanay)
        r = self.client.post(reverse("auth:logout"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "You are logged out")
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(self.client.get(reverse("parent_portal:index")).status_code, 302)

    def test_home_redirects_by_state(self):
        self.assertRedirects(self.client.get("/"), reverse("auth:login"))
        self.login(self.teacher)
        self.assertRedirects(self.client.get("/"), reverse("report:dashboard"))


class RoleAccessTests(PrivacyFixtureMixin, TestCase):
    """The role guards in the Auth controller, seen from the pages they protect."""

    def test_anonymous_is_sent_to_login(self):
        for name in ("parent_portal:index", "report:dashboard", "report:overview"):
            url = reverse(name)
            self.assertRedirects(self.client.get(url), f"{reverse('auth:login')}?next={url}", msg_prefix=name)

    def test_parent_cannot_open_staff_pages(self):
        self.login(self.nanay)
        for name in ("report:dashboard", "report:overview"):
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 403, name)
            self.assertTemplateUsed(r, "auth/403.html")
            self.assertContains(r, "You cannot open this page", status_code=403)

    def test_staff_cannot_open_parent_portal(self):
        self.login(self.teacher)
        r = self.client.get(reverse("parent_portal:index"))
        self.assertEqual(r.status_code, 403)
        self.assertTemplateUsed(r, "auth/403.html")

    def test_teacher_and_adviser_cannot_open_principal_overview(self):
        for u in (self.teacher, self.adviser):
            self.login(u)
            self.assertEqual(self.client.get(reverse("report:overview")).status_code, 403, u.role)

    def test_principal_and_admin_can_open_overview(self):
        for u in (self.principal, self.admin_user):
            self.login(u)
            self.assertEqual(self.client.get(reverse("report:overview")).status_code, 200, u.role)

    def test_403_page_links_back_to_the_users_home(self):
        self.login(self.nanay)
        r = self.client.get(reverse("report:dashboard"))
        self.assertContains(r, reverse("parent_portal:index"), status_code=403)
