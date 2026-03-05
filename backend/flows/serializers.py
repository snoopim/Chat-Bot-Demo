from rest_framework import serializers
from .models import ProcessFlow, ProcessFlowAnswer


class ProcessFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessFlow
        fields = ["id", "name", "description", "status", "created_at", "updated_at"]


class ProcessFlowAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessFlowAnswer
        fields = ["question_key", "answer_text", "status", "updated_at"]
