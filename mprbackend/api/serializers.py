from rest_framework import serializers
from .models import ChecklistQuestion, ChecklistAnswer


class ChecklistQuestionSerializer(serializers.ModelSerializer):
    clientType = serializers.CharField(source='client_type')

    class Meta:
        model = ChecklistQuestion
        fields = ['UUID', 'clientType', 'text', 'active', 'section']


class ChecklistAnswerSerializer(serializers.ModelSerializer):
    visitUUID = serializers.SlugRelatedField(source='visit', slug_field='UUID', read_only=True)
    questionUUID = serializers.PrimaryKeyRelatedField(source='question', read_only=True)

    class Meta:
        model = ChecklistAnswer
        fields = ['visitUUID', 'questionUUID', 'answer1', 'answer2', 'UUID']
