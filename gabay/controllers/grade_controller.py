"""CONTROLLER: Grade. GET /api/students/<id>/grades/ (read only)."""
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from gabay.models import Grade, Student
from gabay.views.grade_view import GradeSerializer


class StudentGradesApiController(APIView):
    def get(self, request, pk):
        student = get_object_or_404(Student.objects.visible_to(request.user), pk=pk)  # 404 if not allowed
        return Response(GradeSerializer(Grade.objects.for_student(student), many=True).data)
