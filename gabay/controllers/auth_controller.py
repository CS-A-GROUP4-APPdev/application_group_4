"""CONTROLLER: Auth.

Handles login, logout, the home redirect and access control. It is also the home of
the role guards (``parent_required``, ``staff_required``, ...) that every other
controller uses to protect its pages.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from gabay.models import STAFF_ROLES, User, effective_role
from gabay.views import auth_view


# ---------------------------------------------------------------- access control
def role_required(*roles):
    """Allow only logged-in users whose role is in ``roles``.

    Anonymous users are sent to the login page. Logged-in users with the
    wrong role get the custom 403 page.
    """
    allowed = set(roles)

    def decorator(page):
        @wraps(page)
        def inner(request, *args, **kwargs):
            if effective_role(request.user) not in allowed:
                raise PermissionDenied
            return page(request, *args, **kwargs)

        return login_required(inner)

    return decorator


parent_required = role_required(User.Role.PARENT)
staff_required = role_required(*STAFF_ROLES)
leadership_required = role_required(User.Role.PRINCIPAL, User.Role.ADMIN)


def home_url_for(user):
    """Where a user lands after login."""
    role = effective_role(user)
    if role == User.Role.PARENT:
        return reverse("parent_portal:index")
    if role in STAFF_ROLES:
        return reverse("report:dashboard")
    if role == User.Role.STUDENT:
        profile = getattr(user, "student_profile", None)
        if profile is not None:
            return reverse("parent_portal:student_detail", args=[profile.pk])
    return reverse("auth:login")


# ---------------------------------------------------------------- pages
class LoginController(LoginView):
    """Login page. After login, parents go to the Parent Portal and staff to the Staff Dashboard."""

    template_name = auth_view.LOGIN_TEMPLATE
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return home_url_for(self.request.user)


class LogoutController(LogoutView):
    template_name = auth_view.LOGGED_OUT_TEMPLATE


def home(request):
    if request.user.is_authenticated:
        return redirect(home_url_for(request.user))
    return redirect("auth:login")


def forbidden(request, exception=None):
    """Custom 403 Forbidden page (wired up as handler403 in config/urls.py)."""
    home = home_url_for(request.user) if request.user.is_authenticated else None
    return auth_view.render_forbidden(request, home)
