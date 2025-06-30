from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=50)          # e.g. "Mathematics"

    def __str__(self): return self.name


class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name    = models.CharField(max_length=100)      # e.g. "Circles"
    number  = models.PositiveSmallIntegerField()    # 10

    class Meta:
        unique_together = ("subject", "number")

    def __str__(self): return f"{self.subject} – Ch {self.number}: {self.name}"


class YearPaper(models.Model):
    """A complete CBSE board exam for a given year."""
    YEAR_CHOICES = [(y, str(y)) for y in range(2020, 2025)]  # last 5 yrs
    year        = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, unique=True)
    subject     = models.ForeignKey(Subject, on_delete=models.CASCADE)
    pdf         = models.FileField(upload_to="papers/")
    total_time  = models.DurationField(default="03:00:00")
    total_marks = models.PositiveSmallIntegerField(default=80)

    def __str__(self): return f"{self.year} CBSE {self.subject}"


class Question(models.Model):
    """Supports MCQ & short/long answers."""
    PAPER_SECTIONS = [("A", "Section A"), ("B", "Section B"), ("C", "Section C")]
    year_paper = models.ForeignKey(YearPaper, on_delete=models.CASCADE, related_name="questions")
    chapter    = models.ForeignKey(Chapter, on_delete=models.PROTECT)
    section    = models.CharField(max_length=1, choices=PAPER_SECTIONS)
    text       = models.TextField()
    image      = models.ImageField(upload_to="questions/", blank=True)
    marks      = models.PositiveSmallIntegerField(default=1)

    # for MCQ
    option_a   = models.CharField(max_length=255, blank=True)
    option_b   = models.CharField(max_length=255, blank=True)
    option_c   = models.CharField(max_length=255, blank=True)
    option_d   = models.CharField(max_length=255, blank=True)
    correct_mcq_option = models.CharField(max_length=1, blank=True)  # 'A'/'B'/…

    # for subjective
    solution_text = models.TextField(blank=True)
    solution_pdf  = models.FileField(upload_to="solutions/", blank=True)

    def __str__(self): return f"Q{self.pk} ({self.year_paper.year})"


class ExamAttempt(models.Model):
    """One full test attempt by a student (anonymous or auth user)."""
    user        = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True, blank=True)
    year_paper  = models.ForeignKey(YearPaper, on_delete=models.CASCADE)
    started_at  = models.DateTimeField(auto_now_add=True)
    completed_at= models.DateTimeField(null=True, blank=True)
    score       = models.PositiveSmallIntegerField(default=0)

    def duration(self):
        if self.completed_at:
            return self.completed_at - self.started_at
        return None


class QuestionAttempt(models.Model):
    exam_attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question     = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_option = models.CharField(max_length=1, blank=True)  # MCQ
    typed_answer    = models.TextField(blank=True)               # subjective
    is_correct      = models.BooleanField(default=False)
    time_spent      = models.DurationField(null=True, blank=True)
