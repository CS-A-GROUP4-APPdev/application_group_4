"""VIEW for the Grade controller: how grades are shown as JSON."""
from rest_framework import serializers

from gabay.models import Grade


class GradeSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject.name")

    class Meta:
        model = Grade
        fields = ["id", "subject", "quarter", "component", "title", "score", "highest_possible_score"]
