from django.urls import path
from logika_general.views import index, login_page, logout_page

urlpatterns = [
    path("", index, name="index"),
    path("login/", login_page, name="login"),
    path("logout/", logout_page, name="logout"),
]

app_name = "logika_general"
