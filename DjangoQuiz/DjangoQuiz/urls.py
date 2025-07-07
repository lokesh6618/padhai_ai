from django.contrib import admin
from django.urls import path
from Quiz import views           # import the functions we just rewrote
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ── Admin ───────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── Landing / dashboard ─────────────────────────────────
    path("", views.home, name="home"),

    # ── Quiz flow ───────────────────────────────────────────
    path("quiz/start/",   views.start_quiz,   name="start_quiz"),
    path("quiz/submit/",  views.submit_quiz,  name="submit_quiz"),
    path("quiz/result/<int:attempt_id>/", views.result, name="result"),

    # ── Authentication ─────────────────────────────────────
    path("register/", views.register_page, name="register"),
    path("login/",    views.login_page,    name="login"),
    path("logout/",   views.logout_page,   name="logout"),

    # (Optional) manual question‑adder view, keep only if you still need it:
    # path("add-question/", views.add_question, name="add_question"),
]

# ── Media / static in DEBUG ────────────────────────────────
if settings.DEBUG:                        # serve uploads in dev only
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
