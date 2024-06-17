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
    path(
        "consolidation-report/",
        views.get_consolidation_reports,
        name="consolidation-report",
    ),
    path(
        "resolve-consolidation-report/<int:report_id>/",
        views.resolve_consolidation_report,
        name="resolve-consolidation-report",
    ),
]
app_name = "logika_statistics"
