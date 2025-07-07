from django.contrib import admin
from .models import Question, Choice, QuizAttempt  # ✅ your new models

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuizAttempt)