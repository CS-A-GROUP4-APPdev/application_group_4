"""MODEL: User. The account and the facts about roles. No request or HTML code here."""
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    """Custom user with a role. Every account in Gabay has exactly one role."""

    class Role(models.TextChoices):
        PARENT = "parent", "Parent/Guardian"
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Subject Teacher"
        ADVISER = "adviser", "Adviser"
        PRINCIPAL = "principal", "Principal/Guidance"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARENT)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    def apply_role_defaults(self):
        """Set this account's permissions from its role, so nobody has to tick them by hand.

        - Admin: staff + superuser (can use the admin site), group "Admin".
        - Every other role: no admin-site access, member of the group named after the role
          (Parent, Student, Teacher, Adviser, Principal) with that role's permissions.
        """
        is_admin = self.role == self.Role.ADMIN
        self.is_staff = is_admin
        self.is_superuser = is_admin
        self.save(update_fields=["is_staff", "is_superuser"])

        role_groups = {r.value.capitalize(): r for r in self.Role}
        mine = Group.objects.get_or_create(name=self.role.capitalize())[0]
        mine.permissions.set(Permission.objects.filter(
            content_type__app_label="users", codename__in=ROLE_PERMISSIONS.get(self.role, ())))
        # Leave any other groups alone; only swap the role groups.
        self.groups.remove(*Group.objects.filter(name__in=role_groups).exclude(pk=mine.pk))
        self.groups.add(mine)


# Django permissions each role group gets. They matter only for accounts that can open the
# admin site; the app's own pages are protected by the role itself (see effective_role).
_VIEW_ALL = ("view_student", "view_parentlink", "view_section", "view_subject", "view_grade", "view_attendance")
_ENCODE = ("add_grade", "change_grade", "add_attendance", "change_attendance")
ROLE_PERMISSIONS = {
    User.Role.TEACHER: _VIEW_ALL[:1] + _VIEW_ALL[2:] + _ENCODE,
    User.Role.ADVISER: _VIEW_ALL + _ENCODE,
    User.Role.PRINCIPAL: _VIEW_ALL,
}  # Parent, Student: none (they use the portal). Admin: everything, as a superuser.


# Roles that work for the school (as opposed to parents and students).
STAFF_ROLES = frozenset({
    User.Role.TEACHER, User.Role.ADVISER, User.Role.PRINCIPAL, User.Role.ADMIN,
})


def effective_role(user):
    """The role used for access checks. Superusers count as admins; anonymous users have none."""
    if not getattr(user, "is_authenticated", False):
        return None
    if user.is_superuser:
        return User.Role.ADMIN
    return user.role
