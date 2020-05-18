from rest_framework import serializers
from .models import ChecklistQuestion


class ChecklistQuestionSerializer(serializers.ModelSerializer):
    clientType = serializers.CharField(source='client_type')
    class Meta:
        model = ChecklistQuestion
        fields = ['UUID', 'clientType', 'text', 'active', 'section']