from django.urls import path
from . import views

app_name = "exam_prep"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("papers/<int:year>/start/", views.start_paper, name="start-paper"),
    path("papers/<int:year>/pdf/",   views.view_pdf,   name="pdf"),
    path("attempt/<int:attempt_id>/<int:q_index>/", views.attempt_question, name="attempt"),
    path("attempt/<int:attempt_id>/results/",        views.results,         name="results"),
]
