from django.urls import path

from logika_teachers.views import teacher_views, api_views, tutor_views

urlpatterns = [
    path("teacher-profile/<int:id>/", teacher_views.teacher_profile, name="teacher-profile"),
    path(
        "teacher-profile/<int:id>/<int:tutor_id>",
        teacher_views.teacher_profile,
        name="teacher-profile-regional",
    ),
    path("create-teacher/", teacher_views.create_teacher, name="create-teacher"),
    path(
        "edit-teacher-profile/<int:id>/",
        teacher_views.edit_teacher_profile,
        name="edit-teacher-profile",
    ),
    path(
        "teacher-feedback/<int:teacher_id>/<int:tutor_id>/",
        teacher_views.teacher_feedback_form,
        name="teacher-feedback",
    ),
    path(
        "teacher-feedback-get-chur-name/",
        api_views.get_churn_name,
        name="get-churn-name",
    ),
    path(
        "teacher-feedback-get-group-title/",
        api_views.get_group_title,
        name="get_group_title",
    ),
    path(
        "teacher-profile-change-churn-status/",
        api_views.change_churn_status,
        name="change-churn-status",
    ),
    path(
        "teacher-profile-add-new-churn/",
        api_views.add_new_churn,
        name="add-new-churn",
    ),
    path(
        "api/open-lessons/",
        api_views.get_open_lessons,
        name="open-lessons",
    ),
    path(
        "api/lesson_comments/",
        api_views.get_lesson_comments,
        name="open-lessons-comments",
    ),
    path(
        "api/churns/",
        api_views.get_churns,
        name="get-churns",
    ),
    path(
        "api/change-tutor-offices/",
        api_views.change_tutor_offices,
        name="change-tutor-offices",
    ),
    path("view-forms/<int:feedback_id>/", teacher_views.view_forms, name="view-forms"),
    path("create-comment/", teacher_views.create_comment, name="create-comment"),
    path(
        "refresh-credentials/<int:user_id>/",
        teacher_views.refresh_credentials,
        name="refresh-credentials",
    ),
    path(
        "teacher-performance/<int:teacher_id>",
        teacher_views.teacher_performance,
        name="teacher-performance",
    ),
    path(
        "tutor-month-report/<int:user_id>",
        tutor_views.tutor_month_report,
        name="tutor-month-report",
    ),
    path(
        "add-performance-to-report/<int:teacher_id>",
        teacher_views.add_performance_to_report,
        name="add-performance-to-report",
    ),
    path(
        "tutor-results-report", tutor_views.tutor_results_report, name="tutor-results-report"
    ),
    path("unsub-teacher/<int:teacher_id>", teacher_views.unsub_teacher, name="unsub-teacher"),
    path(
        "teacher-conversion/<int:teacher_id>",
        teacher_views.get_teacher_conversion,
        name="teacher-conversion",
    ),
    path(
        "teacher-conversion/<int:teacher_id>/<int:tutor_id>",
        teacher_views.get_teacher_conversion,
        name="teacher-conversion-regional",
    ),
    path(
        "tutor-teachers-statistics/",
        tutor_views.get_tutors_conversion,
        name="tutor-teachers-statistics",
    ),
]

app_name = "logika_teachers"
