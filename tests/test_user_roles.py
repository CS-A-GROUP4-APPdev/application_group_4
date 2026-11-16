"""Creating accounts: the role sets the permissions automatically."""
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from gabay.models import User


class ApplyRoleDefaultsTests(TestCase):
    def make(self, role):
        user = User.objects.create_user(f"u{User.objects.count()}_{role}", password="x", role=role)
        user.apply_role_defaults()
        return user

    def test_every_role_joins_its_own_group_only(self):
        for role in User.Role:
            user = self.make(role)
            self.assertEqual([g.name for g in user.groups.all()], [role.value.capitalize()], role)

    def test_only_admin_gets_admin_site_access(self):
        for role in User.Role:
            user = self.make(role)
            is_admin = role == User.Role.ADMIN
            self.assertEqual((user.is_staff, user.is_superuser), (is_admin, is_admin), role)

    def test_group_permissions_match_the_role(self):
        perms = lambda role: set(self.make(role).groups.get().permissions.values_list("codename", flat=True))
        self.assertEqual(perms(User.Role.PARENT), set())
        self.assertEqual(perms(User.Role.STUDENT), set())
        self.assertIn("change_grade", perms(User.Role.TEACHER))
        self.assertNotIn("view_parentlink", perms(User.Role.TEACHER))
        self.assertIn("view_parentlink", perms(User.Role.ADVISER))
        self.assertEqual({p for p in perms(User.Role.PRINCIPAL) if not p.startswith("view_")}, set())

    def test_changing_the_role_swaps_the_group_and_removes_admin_access(self):
        user = self.make(User.Role.ADMIN)
        extra = Group.objects.create(name="Library")
        user.groups.add(extra)
        user.role = User.Role.TEACHER
        user.apply_role_defaults()
        user.refresh_from_db()
        self.assertEqual(sorted(g.name for g in user.groups.all()), ["Library", "Teacher"])  # other groups kept
        self.assertEqual((user.is_staff, user.is_superuser), (False, False))

    def test_seed_demo_applies_roles(self):
        call_command("seed_demo", verbosity=0)
        self.assertEqual([g.name for g in User.objects.get(username="nanay").groups.all()], ["Parent"])
        self.assertEqual([g.name for g in User.objects.get(username="sir").groups.all()], ["Teacher"])


class AdminScreenTests(TestCase):
    """The real Django admin screens."""

    def setUp(self):
        self.boss = User.objects.create_superuser("boss", password="pw12345!")  # made like `createsuperuser`
        self.client.force_login(self.boss)

    def add_user(self, username, role):
        return self.client.post(reverse("admin:users_user_add"), {
            "username": username, "password1": "Str0ng-pass!9", "password2": "Str0ng-pass!9", "role": role})

    def test_adding_a_user_applies_the_role(self):
        for role in User.Role:
            r = self.add_user(f"new_{role}", role)
            self.assertEqual(r.status_code, 302, role)
            user = User.objects.get(username=f"new_{role}")
            self.assertEqual([g.name for g in user.groups.all()], [role.value.capitalize()])
            self.assertEqual(user.is_staff, role == User.Role.ADMIN)

    def change_data(self, user, **overrides):
        data = {"username": user.username, "first_name": "", "last_name": "", "email": "", "is_active": "on",
                "role": user.role, "date_joined_0": user.date_joined.strftime("%Y-%m-%d"),
                "date_joined_1": user.date_joined.strftime("%H:%M:%S")}
        data.update(overrides)
        return data

    def test_changing_the_role_in_the_admin_updates_permissions(self):
        self.add_user("rita", User.Role.TEACHER)
        rita = User.objects.get(username="rita")
        r = self.client.post(reverse("admin:users_user_change", args=[rita.pk]),
                             self.change_data(rita, role=User.Role.ADMIN))
        self.assertEqual(r.status_code, 302)
        rita.refresh_from_db()
        self.assertEqual((rita.role, rita.is_staff, rita.is_superuser), ("admin", True, True))
        self.assertEqual([g.name for g in rita.groups.all()], ["Admin"])

    def test_staff_superuser_and_groups_cannot_be_edited_by_hand(self):
        self.add_user("pia", User.Role.PARENT)
        pia = User.objects.get(username="pia")
        self.client.post(reverse("admin:users_user_change", args=[pia.pk]),
                         self.change_data(pia, is_superuser="on", is_staff="on"))
        pia.refresh_from_db()
        self.assertEqual((pia.is_staff, pia.is_superuser), (False, False))

    def test_saving_an_existing_superuser_without_a_role_change_leaves_it_alone(self):
        r = self.client.post(reverse("admin:users_user_change", args=[self.boss.pk]),
                             self.change_data(self.boss, first_name="Boss"))
        self.assertEqual(r.status_code, 302)
        self.boss.refresh_from_db()
        self.assertEqual((self.boss.first_name, self.boss.is_superuser, self.boss.is_staff), ("Boss", True, True))

    def test_a_teacher_cannot_open_the_admin_site(self):
        self.add_user("tess", User.Role.TEACHER)
        self.client.logout()
        self.client.force_login(User.objects.get(username="tess"))
        self.assertEqual(self.client.get("/admin/").status_code, 302)
