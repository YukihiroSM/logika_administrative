from logika_teachers.models import TeacherProfile, TutorProfile, RegionalTutorProfile
from logika_general.models import RegionalManagerProfile, TerritorialManagerProfile, ClientManagerProfile


def get_user_role(user):
    try:
        if user.username == "logikaadmin":
            return "admin"
        if TeacherProfile.objects.filter(user=user).first():
            return "teacher"
        elif TutorProfile.objects.filter(user=user).first():
            return "tutor"
        elif RegionalTutorProfile.objects.filter(user=user).first():
            return "regional_tutor"
        elif RegionalManagerProfile.objects.filter(user=user).first():
            return "regional_manager"
        elif TerritorialManagerProfile.objects.filter(user=user).first():
            return "territorial_manager"
        elif ClientManagerProfile.objects.filter(user=user).first():
            return "client_manager"
    except:
        pass
    return "undefined"


def get_user_role_by_request(request):
    role = get_user_role(request.user)
    return {"user_role": role}
