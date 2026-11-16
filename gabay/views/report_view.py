"""VIEW for the Report controller: the staff dashboard and the school overview."""
from django.shortcuts import render

STAFF_DASHBOARD_TEMPLATE = "report/staff_dashboard.html"
STAFF_OVERVIEW_TEMPLATE = "report/staff_overview.html"


def render_staff_dashboard(request, student_count, absent_today, students):
    return render(request, STAFF_DASHBOARD_TEMPLATE, {
        "student_count": student_count,
        "absent_today": absent_today,
        "students": students,
    })


def render_staff_overview(request, by_grade, with_consent, no_consent):
    return render(request, STAFF_OVERVIEW_TEMPLATE, {
        "by_grade": by_grade,
        "with_consent": with_consent,
        "no_consent": no_consent,
    })
