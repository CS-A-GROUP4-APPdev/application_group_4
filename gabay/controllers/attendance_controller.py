"""CONTROLLER: Attendance. GET /api/students/<id>/attendance/ (read only)."""
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from gabay.models import Attendance, Student
from gabay.views.attendance_view import AttendanceSerializer


class StudentAttendanceApiController(APIView):
    def get(self, request, pk):
        student = get_object_or_404(Student.objects.visible_to(request.user), pk=pk)  # 404 if not allowed
        return Response(AttendanceSerializer(Attendance.objects.for_student(student), many=True).data)
