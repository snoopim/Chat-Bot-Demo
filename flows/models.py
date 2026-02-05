from django.db import models


class ProcessFlow(models.Model):
    STATUS_CHOICES = [
        ("not_completed", "Not completed"),
        ("in_progress", "In progress"),
        ("completed", "Completed"),
    ]

    AI_PROVIDER_CHOICES = [
        ("openai", "OpenAI (API Key)"),
        ("claude_sdk", "Claude Agent SDK"),
        ("claude_api", "Claude (API Key)"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    # NEW: user can choose AI engine (we will use openai first)
    ai_provider = models.CharField(
        max_length=20,
        choices=AI_PROVIDER_CHOICES,
        default="openai",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="not_completed",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProcessFlowAnswer(models.Model):
    STATUS_CHOICES = [
        ("unanswered", "Unanswered"),
        ("skipped", "Skipped"),
        ("answered", "Answered"),
    ]

    process_flow = models.ForeignKey(
        ProcessFlow,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question_key = models.CharField(max_length=120)

    answer_text = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="unanswered",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("process_flow", "question_key")

    def __str__(self):
        return f"{self.process_flow_id}:{self.question_key}:{self.status}"
