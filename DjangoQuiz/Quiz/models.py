from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Question(models.Model):
    uid        = models.CharField(max_length=20, unique=True)
    text       = models.TextField(blank=True, null=True)
    image      = models.ImageField(upload_to="math_2024_430_1_1_BASIC/", blank=True, null=True)
    year       = models.IntegerField(default=2024)
    paper_code = models.CharField(max_length=20, default="30-1-1")

    op1 = models.CharField(max_length=200)
    op2 = models.CharField(max_length=200)
    op3 = models.CharField(max_length=200)
    op4 = models.CharField(max_length=200)

    correct = models.PositiveSmallIntegerField(choices=[(1, "A"), (2, "B"), (3, "C"), (4, "D")])

    def __str__(self):
        return f"Q{self.uid} - {self.paper_code}"


class Choice(models.Model):
    """
    Four choices per question.  Exactly one should have is_correct=True.
    """
    question   = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} – {self.text[:60]}"


class QuizAttempt(models.Model):
    """
    One row per quiz run.
    Only aggregates are stored; per‑question responses are optional.
    """
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at      = models.DateTimeField(auto_now_add=True)
    finished_at     = models.DateTimeField(null=True, blank=True)
    duration        = models.PositiveIntegerField(null=True, blank=True)  # seconds
    score           = models.PositiveSmallIntegerField(default=0)  # /20
    total_attempted = models.PositiveSmallIntegerField(default=0)
    correct         = models.PositiveSmallIntegerField(default=0)
    wrong           = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} – {self.score}/20 on {self.started_at:%d %b %Y %H:%M}"
    

    
