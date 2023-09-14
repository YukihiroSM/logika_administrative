from django.urls import path
from logika_auth import views

urlpatterns = [
    path("create_user", views.create_user, name="create_user"),
    path("deactivate_user", views.deactivate_user, name="deactivate_user"),
    path("auth_user", views.auth_user, name="auth_user"),
    path("update_user", views.update_user, name="update_user")
]