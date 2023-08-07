from django.contrib import admin
from logika_teachers.models import TeacherProfile, TutorProfile, TeacherFeedback, RegionalTutorProfile

admin.site.register(TeacherProfile)
admin.site.register(TutorProfile)
admin.site.register(TeacherFeedback)
admin.site.register(RegionalTutorProfile)
# Register your models here.
