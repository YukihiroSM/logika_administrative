from django.contrib import admin
from logika_teachers.models import (
    TeacherProfile,
    TutorProfile,
    TeacherFeedback,
    RegionalTutorProfile,
)


class RelatedTeachersInline(admin.TabularInline):
    model = TeacherProfile.related_tutors.through
    extra = 0
    autocomplete_fields = ["teacherprofile"]


class TeacherProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__last_name", "user__first_name"]


class TutorProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__last_name", "user__first_name"]
    inlines = [RelatedTeachersInline]


admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(TutorProfile, TutorProfileAdmin)
admin.site.register(TeacherFeedback)
admin.site.register(RegionalTutorProfile)
