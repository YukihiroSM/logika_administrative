from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from utils.get_user_role import get_user_role
from logika_teachers.models import TeacherProfile, TutorProfile, TeacherFeedback


@login_required(login_url="/login")
def index(request):
    user_role = get_user_role(request.user)
    teachers = []
    tutors = []
    feedbacks = []
    if user_role == "teacher":
        teacher_profile = TeacherProfile.objects.filter(user=request.user).first()
        feedbacks = TeacherFeedback.objects.filter(teacher=teacher_profile).order_by("-created_at").all()
        tutors = teacher_profile.related_tutors.all()
    if user_role == "tutor":
        teachers = TutorProfile.objects.filter(user=request.user).first().related_teachers.all()
        feedbacks = []
        tutor_profile = TutorProfile.objects.filter(user=request.user).first()
        for teacher in teachers:
            feedbacks.append(TeacherFeedback.objects.filter(teacher=teacher, tutor=tutor_profile).order_by("-created_at").first())

    return render(request, "index.html", context={"user": request.user, "user_role": user_role, "tutors": tutors, "teachers": teachers, "feedbacks": feedbacks})


# # sign in user
def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('logika_general:index')
        else:
            return redirect('/login')
    return render(request, 'logika_general/login.html')


@login_required(login_url="/login")
def logout_page(request):
    logout(request)
    return redirect("logika_general:index")


def error_404(request, exception):
    return render(request, "error_404.html", context={"error": exception})


def error_500(request):
    return render(request, "error_500.html", context={})
