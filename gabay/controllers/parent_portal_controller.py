"""CONTROLLER: ParentPortal.

The parent's pages and the student records they (or a student or staff member) may open.
Every student shown to a user comes from ``Student.objects.visible_to(user)``, so the privacy
rule lives in one place (the Model). A student the user may not see gives 404 (not 403) on
purpose: it does not reveal that the student exists.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from gabay.controllers.auth_controller import parent_required
from gabay.models import Attendance, Grade, ParentLink, Student
from gabay.views import parent_portal_view


@parent_required
def parent_portal(request):
    children = Student.objects.visible_to(request.user).with_attendance_counts()
    waiting = ParentLink.objects.count_waiting_for(request.user)
    return parent_portal_view.render_parent_portal(request, children, waiting)


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.visible_to(request.user), pk=pk)
    return parent_portal_view.render_student_detail(
        request,
        student,
        grades=Grade.objects.for_student(student),
        attendance=Attendance.objects.recent_for_student(student, limit=30),
    )


class StudentApiController(viewsets.ReadOnlyModelViewSet):
    """GET /api/students/ and /api/students/<id>/ (read only)."""

    serializer_class = parent_portal_view.StudentSerializer

    def get_queryset(self):
        return Student.objects.visible_to(self.request.user)
