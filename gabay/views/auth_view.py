"""VIEW for the Auth controller: the login, logged-out and "access denied" pages.
No database queries and no decisions here."""
from django.shortcuts import render

LOGIN_TEMPLATE = "auth/login.html"
LOGGED_OUT_TEMPLATE = "auth/logged_out.html"
FORBIDDEN_TEMPLATE = "auth/403.html"


def render_forbidden(request, home_url):
    """The 403 page. ``home_url`` is where to send the user, or None if not logged in."""
    return render(request, FORBIDDEN_TEMPLATE, {"home_url": home_url}, status=403)
