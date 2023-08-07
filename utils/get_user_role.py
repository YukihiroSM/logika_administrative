from logika_teachers.models import TeacherProfile, TutorProfile, RegionalTutorProfile


def get_user_role(user):
    try:
        if TeacherProfile.objects.filter(user=user).first():
            return "teacher"
        elif TutorProfile.objects.filter(user=user).first():
            return "tutor"
        elif RegionalTutorProfile.objects.filter(user=user).first():
            return "regional_tutor"
    except:
        pass
    return "undefined"
