"""VIEW for the Attendance controller: how attendance is shown as JSON."""
from rest_framework import serializers

from gabay.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject.name")

    class Meta:
        model = Attendance
        fields = ["id", "subject", "date", "period", "status"]
