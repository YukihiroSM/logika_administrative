from django.urls import path
from logika_teachers import views

urlpatterns = [
    path("teacher-profile/<int:id>/", views.teacher_profile, name="teacher-profile"),
    path("create-teacher/", views.create_teacher, name="create-teacher"),
    path("teacher-feedback/<int:teacher_id>/<int:tutor_id>/", views.teacher_feedback_form, name="teacher-feedback"),
    path("view-forms/<int:feedback_id>", views.view_forms, name="view-forms"),
    path("create-comment/", views.create_comment, name="create-comment"),
]

app_name = "logika_teachers"
