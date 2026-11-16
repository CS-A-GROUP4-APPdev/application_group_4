"""CONTROLLER: Report.

The staff dashboard (all school staff) and the school overview (principal and admin only).
"""
from datetime import date

from gabay.controllers.auth_controller import leadership_required, staff_required
from gabay.models import Attendance, ParentLink, Student
from gabay.views import report_view


@staff_required
def staff_dashboard(request):
    students = Student.objects.visible_to(request.user)
    return report_view.render_staff_dashboard(
        request,
        student_count=students.count(),
        absent_today=Attendance.objects.count_absent_on(students, date.today()),
        students=students[:50],
    )


@leadership_required
def staff_overview(request):
    students = Student.objects.visible_to(request.user)
    consent = ParentLink.objects.consent_summary()
    return report_view.render_staff_overview(
        request,
        by_grade=students.count_by_grade_level(),
        with_consent=consent["with_consent"],
        no_consent=consent["no_consent"],
    )
