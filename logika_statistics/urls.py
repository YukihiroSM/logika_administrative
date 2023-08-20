# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from logika_statistics import views

urlpatterns = [
    path('english_new', views.english_new, name='home'),
    path('', views.home, name='home'),
    path('programming_new', views.programming_report_updated, name='home'),
    path('issues', views.issues_new, name='home'),
    path('issues_new', views.issues_new, name='home'),
    path('issues_tutors', views.issues_tutors, name='home'),
    path('add_student_amo_ref_new/<str:issue_id>',
         views.create_student_amo_ref_new, name='home'),
    path('add_student_amo_ref/<str:issue_id>',
         views.create_student_amo_ref_new, name='home'),
    path('programming_tutor_new', views.programming_tutor_new, name='home'),
    path('teachers_programming',
         views.programming_teacher_new, name='home'),
    path('teachers_english', views.english_teacher_new, name='home'),
    path('english_tutor_new', views.english_tutor_new, name='home'),
    path('close_issue/<str:issue_id>', views.close_issue_new, name='home'),
    path('close_issue_new/<str:issue_id>', views.close_issue_new, name='home'),
    path('close_issue_reason/<str:issue_id>',
         views.close_issue_reason_new, name='home'),
    path('close_issue_reason_new/<str:issue_id>',
         views.close_issue_reason_new, name='home'),
    path('close_no_actions_issue_reason/<str:issue_id>',
         views.close_no_actions_issue_reason_new, name='home'),
    path('close_no_actions_issue_reason_new/<str:issue_id>',
         views.close_no_actions_issue_reason_new, name='home'),
    path('resolve_amo_issue/<str:issue_id>',
         views.resolve_no_amo_issue_without_actions_new, name='home'),
    path('resolve_amo_issue_new/<str:issue_id>',
         views.resolve_no_amo_issue_without_actions_new, name='home'),
    path('check_small_payment/<str:issue_id>',
         views.check_small_payment, name='home'),
    path('add_small_payment/<str:issue_id>',
         views.add_small_payment, name='home'),
    path('add_student_id/<str:issue_id>', views.add_student_id, name='home'),
    path('add_client_manager/<str:issue_id>',
         views.add_client_manager, name='home'),
    path('add_location/<str:issue_id>', views.add_location, name='home'),
    path('assign_issue/<str:issue_id>', views.assign_issue, name='home'),
    path('assign_issue_tutor/<str:issue_id>',
         views.assign_issue_tutor, name='home'),
    path('add_teacher_for_group/<str:issue_id>',
         views.add_teacher_for_group, name='home'),
    path('revert_issue/<str:issue_id>', views.revert_issue, name='home'),
    path('consolidation_issue_resolve/<str:issue_id>',
         views.consolidation_issue_resolve, name='home'),
    path('consolidation_issue_close/<str:issue_id>',
         views.consolidation_issue_close, name='home'),
    path('health', views.health, name='home'),
    # path('programming_test', views.programming_report, name="home"),
    path('consolidation', views.consolidation_report, name="home"),
    path('lessons_links_collection', views.collect_lessons_links, name="home"),
    path('lessons_links_collection_extended',
         views.collect_lessons_links_extended, name="home"),
    path('programming_updated', views.programming_report_updated, name="home"),
    path('', views.home, name='home'),

    # Matches any html file
#     re_path(r'^.*\.*', views.pages, name='pages'),
]
app_name = "logika_statistics"