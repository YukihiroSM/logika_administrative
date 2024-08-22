import json
from datetime import date

from django.core.serializers import serialize
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST, require_GET

from logika_statistics.models import Group
from logika_teachers.lesson_facade import LessonFacade
from logika_teachers.services.lms_service import LMSService
from logika_teachers.models import PredictedChurn, TutorProfile, TeacherComment, TeacherProfile


@require_GET
def get_churn_name(request) -> JsonResponse:
    churn_id = request.GET.get("churn_id")
    if churn_id:

        data, status = LMSService.get_student(churn_id)
        if status == 200:
            name = data.get("last_name") + " " + data.get("first_name")
            return JsonResponse({"value": name})
        elif status == 404:
            return JsonResponse({"value": "Учня не знайдено"})
        else:
            return JsonResponse({"value": "Щось пішло не так"})

    else:
        return JsonResponse({"value": "Введіть ID учня"})


@require_GET
def get_group_title(request) -> JsonResponse:
    group_id = request.GET.get("group_id")
    if group_id:

        data, status = LMSService.get_group(group_id)
        if status == 200:
            title = data.get("title", "Назва невідома")
            return JsonResponse({"value": title})
        elif status == 404:
            return JsonResponse({"value": "Група не знайдена"})
        else:
            return JsonResponse({"value": "Щось пішло не так"})

    else:
        return JsonResponse({"value": "Введіть ID групи"})


@require_POST
def change_churn_status(request):
    data = json.loads(request.body)
    predicted_churn = PredictedChurn.objects.filter(
        churn_id=data.get("churn_id"),
        teacher=data.get("teacher_id"),
        created_at=data.get("created_at")
    )
    if predicted_churn.exists():
        predicted_churn = predicted_churn.first()
        predicted_churn.status = data.get("status")
        predicted_churn.save()
    return JsonResponse({"value": "test"})


@require_POST
def add_new_churn(request):
    churn_id = request.POST.get("churn_id")
    churn_status = request.POST.get("churn_status")
    teacher_id = request.POST.get("teacher")
    description = request.POST.get("description", "")
    if churn_id and churn_status and teacher_id:
        predicted_churn = PredictedChurn.objects.filter(churn_id=churn_id,
                                                        teacher_id=teacher_id)
        if predicted_churn.exists():
            predicted_churn = predicted_churn.order_by("-priority", "-created_at").first()
            predicted_churn.status = churn_status
            predicted_churn.description = description
            predicted_churn.created_at = date.today()
            predicted_churn.save()
        else:
            PredictedChurn.objects.create(churn_id=churn_id,
                                          status=churn_status,
                                          description=description,
                                          teacher_id=teacher_id)

    next_url = request.POST.get("next", "/")
    return HttpResponseRedirect(next_url)


@require_GET
def get_open_lessons(request):
    teachers = (
        TutorProfile.objects.filter(user=request.user)
        .first()
        .related_teachers.all()
    )
    groups = Group.objects.filter(teacher_id__in=list(teachers.values_list("lms_id", flat=True)),
                                  type__in=("regular", "individual", "Группа", "Индивидуальная"))

    open_lessons = []
    for group in groups:
        lessons_facade = LessonFacade(lms_service=LMSService, group_id=group.lms_id)
        teacher = TeacherProfile.objects.filter(lms_id=group.teacher_id).first()
        lessons_facade.filter_open_lessons()
        for lesson in lessons_facade.lessons:
            last_comment = TeacherComment.objects.filter(lesson_id=lesson["lesson_id"]).order_by("-created_at").first()
            lesson.update({"group_name": group.title,
                           "group_id": group.lms_id,
                           "teacher": group.teacher_name,
                           "teacher_id": teacher.id,
                           "last_comment": last_comment.comment if last_comment else "Коментаря немає",
                           })
        open_lessons.extend(lessons_facade.lessons)

    return JsonResponse({"open_lessons": open_lessons})


@require_GET
def get_lesson_comments(request):
    lesson_id = request.GET.get("lesson_id")
    comments = TeacherComment.objects.filter(lesson_id=lesson_id)
    if comments.exists():
        comments = comments.values()
        return JsonResponse({"comments": list(comments)})
    return JsonResponse({"comments": []})


@require_GET
def get_churns(request):
    teachers = (
        TutorProfile.objects.filter(user=request.user)
        .first()
        .related_teachers.all()
    )
    churns = PredictedChurn.objects.filter(teacher__in=teachers)
    if churns.exists():
        churn_list = list()
        for churn in churns:
            churn_comments = TeacherComment.objects.filter(churn_id=churn.churn_id).order_by("-created_at")
            comment_list = list()
            for comment in churn_comments:
                c = {"description": comment.comment,
                     "created_at": comment.created_at}
                comment_list.append(c)
            churn = {"teacher_pk": churn.teacher.pk,
                     "churn_pk": churn.pk,
                     "churn_id": churn.churn_id,
                     "fullname": churn.fullname,
                     "group_title": churn.group.title,
                     "group_lms": churn.group.lms_id,
                     "description": churn.description,
                     "created_at": churn.created_at,
                     "comment": churn.comment.comment if churn.comment else "",
                     "feedback": churn.feedback.id if churn.feedback else None,
                     "teacher_name": str(churn.teacher),
                     "teacher_id": churn.teacher.id,
                     "status": churn.get_status_display(),
                     "real_status": churn.status,
                     "STATUS_CHOICES": churn.STATUS_CHOICES,
                     "priority": churn.priority,
                     "comments": comment_list}
            churn_list.append(churn)
        return JsonResponse({"churns": churn_list})
    return JsonResponse({"churns": []})
