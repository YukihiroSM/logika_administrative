# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

from logika_statistics import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "programming-updated",
        views.programming_report_updated,
        name="programming-updated",
    ),
    path("edit-location/<int:location_id>/", views.edit_location, name="edit-location"),
    path(
        "delete-location/<int:location_id>/",
        views.delete_location,
        name="delete-location",
    ),
    path("list-locations/", views.list_locations, name="list-locations"),
    path("create-location/", views.create_location, name="create-location"),
]
app_name = "logika_statistics"
