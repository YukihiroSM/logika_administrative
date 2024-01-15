from django.urls import path

from logika_teachers import views

urlpatterns = [
    path("teacher-profile/<int:id>/", views.teacher_profile, name="teacher-profile"),
    path(
        "teacher-profile/<int:id>/<int:tutor_id>",
        views.teacher_profile,
        name="teacher-profile-regional",
    ),
    path("create-teacher/", views.create_teacher, name="create-teacher"),
    path(
        "edit-teacher-profile/<int:id>/",
        views.edit_teacher_profile,
        name="edit-teacher-profile",
    ),
    path(
        "teacher-feedback/<int:teacher_id>/<int:tutor_id>/",
        views.teacher_feedback_form,
        name="teacher-feedback",
    ),
    path("view-forms/<int:feedback_id>/", views.view_forms, name="view-forms"),
    path("create-comment/", views.create_comment, name="create-comment"),
    path(
        "refresh-credentials/<int:user_id>/",
        views.refresh_credentials,
        name="refresh-credentials",
    ),
    path(
        "teacher-performance/<int:teacher_id>",
        views.teacher_performance,
        name="teacher-performance",
    ),
    path("tutor-results/", views.tutor_results, name="tutor-results"),
    path(
        "tutor-month-report/<int:user_id>",
        views.tutor_month_report,
        name="tutor-month-report",
    ),
    path(
        "add-performance-to-report/<int:teacher_id>",
        views.add_performance_to_report,
        name="add-performance-to-report",
    ),
    path(
        "tutor-results-report", views.tutor_results_report, name="tutor-results-report"
    ),
    path("unsub-teacher/<int:teacher_id>", views.unsub_teacher, name="unsub-teacher"),
    path(
        "teacher-conversion/<int:teacher_id>",
        views.get_teacher_conversion,
        name="teacher-conversion",
    ),
    path(
        "teacher-conversion/<int:teacher_id>/<int:tutor_id>",
        views.get_teacher_conversion,
        name="teacher-conversion-regional",
    ),
    path(
        "tutor-teachers-statistics/",
        views.get_tutors_conversion,
        name="tutor-teachers-statistics",
    ),
]

app_name = "logika_teachers"
