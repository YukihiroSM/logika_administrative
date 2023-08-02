from django.urls import path
from logika_teachers import views

urlpatterns = [
    path("teacher-profile/<int:id>/", views.teacher_profile, name="teacher-profile"),
    path("create-teacher/", views.create_teacher, name="create-teacher"),
]

app_name = "logika_general"
