from django.contrib import admin
from logika_teachers.models import TeacherProfile, TutorProfile, TeacherFeedback

admin.site.register(TeacherProfile)
admin.site.register(TutorProfile)
admin.site.register(TeacherFeedback)
# Register your models here.
