from django.urls import path
from logika_auth import views

urlpatterns = [
    path('/login/', views.login_page, name='login'),
]