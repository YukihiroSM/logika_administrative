# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from logika_statistics import views

urlpatterns = [
    path("", views.home, name="home"),
    path("programming_updated", views.programming_report_updated, name="home"),
]
app_name = "logika_statistics"
