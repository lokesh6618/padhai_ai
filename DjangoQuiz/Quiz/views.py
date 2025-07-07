# views.py
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import Question, Choice, QuizAttempt   # NEW models

# 1.  Landing page ────────────────────────────────────────────────────────────
def home(request):
    """Simple landing / dashboard page."""
    return render(request, "Quiz/home.html")


# 2.  Register / Login / Logout ──────────────────────────────────────────────
def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)               # auto‑login after sign‑up
        return redirect("home")

    return render(request, "Quiz/register.html", {"form": form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("home")

    return render(request, "Quiz/login.html", {"form": form})


@login_required
def logout_page(request):
    logout(request)
    return redirect("home")


# 3.  Quiz flow ──────────────────────────────────────────────────────────────
@login_required
def start_quiz(request):
    """
    • Creates a new QuizAttempt row
    • Fetches the first 20 questions (code 30‑1‑1, CBSE 2024)
    • Puts attempt_id in session, then renders quiz.html
    """
    # wipe any old, unfinished attempt
    request.session.pop("attempt_id", None)

    questions = Question.objects.all()[:20]              # guaranteed order
    attempt = QuizAttempt.objects.create(user=request.user)
    request.session["attempt_id"] = attempt.id

    return render(request, "Quiz/quiz.html", {"questions": questions})


@login_required
def submit_quiz(request):
    """
    Handles POST from quiz.html (manual submit or auto‑submit after 30 min).
    Calculates score, updates QuizAttempt, and redirects to result page.
    """
    if request.method != "POST":
        return redirect("home")

    attempt_id = request.session.get("attempt_id")
    if not attempt_id:
        return HttpResponse("No active attempt.", status=400)

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    questions = Question.objects.all()[:20]

    total_attempted = correct = 0

    for q in questions:
        choice_id = request.POST.get(f"q{q.id}")
        if not choice_id:
            continue
        total_attempted += 1
        chosen = Choice.objects.filter(id=choice_id, question=q).first()
        if chosen and chosen.is_correct:
            correct += 1

    attempt.total_attempted = total_attempted
    attempt.correct         = correct
    attempt.wrong           = total_attempted - correct
    attempt.score           = correct               # 1 mark each
    attempt.finished_at = timezone.now()
    attempt.duration    = int(
        (attempt.finished_at - attempt.started_at).total_seconds()
    )

    attempt.save()

    # clean up session so the user can’t resubmit
    request.session.pop("attempt_id", None)

    return redirect("result", attempt_id=attempt.id)


@login_required
def result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    # Provide the same context names your original template expects
    percent = attempt.score / 20 * 100          # 20 questions → 20 marks
    context = {
        "score":   attempt.score,
        "percent": round(percent, 2),
        "time":    attempt.duration or 0,
        "correct": attempt.correct,
        "wrong":   attempt.wrong,
        "total":   20,
        "attempt": attempt,                      # in case result.html needs more
    }
    return render(request, "Quiz/result.html", context)
