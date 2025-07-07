from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from .models import YearPaper, Chapter, ExamAttempt, Question, QuestionAttempt
from django.utils import timezone

def dashboard(request):
    """Home page = your Tailwind index.html."""
    papers = YearPaper.objects.select_related("subject").order_by("-year")
    chapters = Chapter.objects.filter(subject__name="Mathematics").order_by("number")
    context = {"papers": papers, "chapters": chapters}
    return render(request, "exam_prep/index.html", context)


def start_paper(request, year):
    paper = get_object_or_404(YearPaper, year=year)
    attempt = ExamAttempt.objects.create(user=request.user if request.user.is_authenticated else None,
                                         year_paper=paper)
    return redirect("exam:attempt", attempt_id=attempt.id, q_index=1)


def attempt_question(request, attempt_id, q_index):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    questions = attempt.year_paper.questions.order_by("pk")
    question  = questions[q_index - 1]

    if request.method == "POST":
        selected = request.POST.get("choice")
        qa, _ = QuestionAttempt.objects.get_or_create(exam_attempt=attempt, question=question)
        qa.selected_option = selected
        qa.is_correct = selected == question.correct_mcq_option
        qa.save()
        next_index = q_index + 1
        if next_index > questions.count():
            attempt.completed_at = timezone.now()
            attempt.score = sum(1 for a in attempt.answers.filter(is_correct=True))
            attempt.save()
            return redirect("exam:results", attempt_id=attempt.id)
        return redirect("exam:attempt", attempt_id=attempt.id, q_index=next_index)

    return render(request, "exam_prep/question.html",
                  {"attempt": attempt, "question": question, "index": q_index, "total": questions.count()})


def results(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    return render(request, "exam_prep/results.html", {"attempt": attempt})


def view_pdf(request, year):
    paper = get_object_or_404(YearPaper, year=year)
    return FileResponse(paper.pdf.open("rb"), as_attachment=False, filename=f"{year}_maths.pdf")
