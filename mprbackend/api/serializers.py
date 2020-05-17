from rest_framework import serializers
from .models import ChecklistQuestion


class ChecklistQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistQuestion
        fields = ['UUID', 'client_type', 'text', 'active', 'section']