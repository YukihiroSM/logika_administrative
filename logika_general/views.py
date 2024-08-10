from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from logika_teachers.models import (
    TeacherProfile,
    TutorProfile,
    TeacherFeedback,
    RegionalTutorProfile, PredictedChurn, TeacherComment,
)
from utils.get_user_role import get_user_role


@login_required(login_url="/login")
def index(request):
    user_role = get_user_role(request.user)
    teachers = []
    tutors = []
    feedbacks = []
    predicted_churns = []
    churn_comments = []
    from_date = ""
    to_date = ""
    teacher_name = ""
    if user_role == "teacher":
        teacher_profile = TeacherProfile.objects.filter(user=request.user).first()
        feedbacks = (
            TeacherFeedback.objects.filter(teacher=teacher_profile)
            .order_by("-created_at")
            .all()
        )
        tutors = teacher_profile.related_tutors.all()
    if user_role == "tutor":
        if request.method == "POST":
            churn_pk = request.POST.get("churn_pk")
            if churn_pk:
                status = request.POST.get("status", "relevant")
                description = request.POST.get("description", "")
                priority = request.POST.get("priority", 0)
                churn = PredictedChurn.objects.get(pk=churn_pk)
                churn.status = status
                churn.description = description
                churn.priority = priority
                churn.save()
        teachers = (
            TutorProfile.objects.filter(user=request.user)
            .first()
            .related_teachers.all()
        )
        feedbacks = []
        tutor_profile = TutorProfile.objects.filter(user=request.user).first()
        for teacher in teachers:
            feedbacks.append(
                TeacherFeedback.objects.filter(teacher=teacher, tutor=tutor_profile)
                .order_by("-created_at")
                .first()
            )
        teacher_name = request.GET.get("churn_teacher", "")
        if teacher_name:
            churn_teachers = teachers.filter(
                (Q(user__first_name__icontains=teacher_name) | Q(user__last_name__icontains=teacher_name))
            )
        else:
            churn_teachers = teachers
        predicted_churns = PredictedChurn.objects.filter(teacher__in=churn_teachers).order_by("-priority", "-created_at")

        status = request.GET.get("churn_status")
        if status:
            predicted_churns = predicted_churns.filter(status=status)

        from_date = request.GET.get("churn_date_from")
        from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
        to_date = request.GET.get("churn_date_to")
        to_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
        if from_date:
            predicted_churns = predicted_churns.filter(created_at__gte=from_date)
        if to_date:
            predicted_churns = predicted_churns.filter(created_at__lte=to_date)
        tutor_comments = TeacherComment.objects.filter(tutor=tutor_profile)
        churn_comments = []
        for churn in PredictedChurn.objects.filter(teacher__in=teachers):
            churn_comments.append((churn.churn_id, tutor_comments.filter(churn_id=churn.churn_id)))
    if user_role == "regional_tutor" or user_role == "admin":
        regional_tutor_profile = RegionalTutorProfile.objects.filter(
            user=request.user
        ).first()

        tutors = regional_tutor_profile.related_tutors.all()
        teachers = {}
        for tutor in tutors:
            teachers[tutor.id] = tutor.related_teachers.all()

    return render(
        request,
        "index/index.html",
        context={
            "user": request.user,
            "user_role": user_role,
            "tutors": tutors,
            "teachers": teachers,
            "feedbacks": feedbacks,
            "predicted_churns": predicted_churns,
            "churn_comments": churn_comments,
            "from_date": from_date.strftime("%Y-%m-%d") if from_date else "",
            "to_date": to_date.strftime("%Y-%m-%d") if to_date else "",
            "teacher_name": teacher_name,
        },
    )


# # sign in user
def login_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("logika_general:index")
        else:
            return redirect("/login")
    return render(request, "logika_general/login.html")


@login_required(login_url="/login")
def logout_page(request):
    logout(request)
    return redirect("logika_general:index")


def error_404(request, exception):
    return render(request, "error_404.html", context={"error": exception})


def error_500(request):
    return render(request, "error_500.html", context={})
