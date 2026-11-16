"""VIEW for the ParentPortal controller: the portal page, the child's records page, and the student JSON.
No database queries and no access rules here."""
from django.shortcuts import render
from rest_framework import serializers

from gabay.models import Student

PARENT_PORTAL_TEMPLATE = "parent_portal/parent_portal.html"
STUDENT_DETAIL_TEMPLATE = "parent_portal/student_detail.html"


def render_parent_portal(request, children, waiting_links):
    return render(request, PARENT_PORTAL_TEMPLATE, {"children": children, "waiting_links": waiting_links})


def render_student_detail(request, student, grades, attendance):
    return render(request, STUDENT_DETAIL_TEMPLATE, {
        "student": student,
        "grades": grades,
        "attendance": attendance,
    })


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "lrn", "first_name", "last_name", "grade_level", "section"]
