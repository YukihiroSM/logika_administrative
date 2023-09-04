from django.contrib import admin
from logika_teachers.models import TeacherProfile, TutorProfile, TeacherFeedback, RegionalTutorProfile


class TeacherProfileAdmin(admin.ModelAdmin):
    search_fields = ["user.last_name"]

admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(TutorProfile)
admin.site.register(TeacherFeedback)
admin.site.register(RegionalTutorProfile)
# Register your models here.
