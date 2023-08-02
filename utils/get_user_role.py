from logika_teachers.models import TeacherProfile, TutorProfile


def get_user_role(user):
    if TeacherProfile.objects.filter(user=user).first():
        return "teacher"
    elif TutorProfile.objects.filter(user=user).first():
        return "tutor"
    else:
        return "undefined"
