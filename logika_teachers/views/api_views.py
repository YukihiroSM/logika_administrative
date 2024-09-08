import json
from dataclasses import asdict

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST, require_GET

from logika_statistics.models import Group, OfficeRegion
from logika_teachers.repositories.churn_repository import ChurnRepository
from logika_teachers.repositories.dtos import ChurnRawDTO
from logika_teachers.repositories.group_repository import GroupRepository
from logika_teachers.services.group_service import GroupService
from logika_teachers.services.lms_service import LMSService
from logika_teachers.services.lesson_service import LessonService
from logika_teachers.models import PredictedChurn, TutorProfile, TeacherComment


@require_GET
def get_churn_name(request: WSGIRequest) -> JsonResponse:
    churn_id = request.GET.get("churn_id")
    if churn_id:

        student_dto, status = LMSService.get_student(churn_id)
        if status == 200:
            name = student_dto.last_name + " " + student_dto.first_name
            return JsonResponse({"value": name})
        elif status == 404:
            return JsonResponse({"value": "Учня не знайдено"})
        else:
            return JsonResponse({"value": "Щось пішло не так"})

    else:
        return JsonResponse({"value": "Введіть ID учня"})


@require_GET
def get_group_title(request: WSGIRequest) -> JsonResponse:
    group_id = request.GET.get("group_id")
    if group_id:

        group_dto, status = LMSService.get_group(group_id)
        if status == 200:
            title = group_dto.title or "Назва невідома"
            return JsonResponse({"value": title})
        elif status == 404:
            return JsonResponse({"value": "Група не знайдена"})
        else:
            return JsonResponse({"value": "Щось пішло не так"})

    else:
        return JsonResponse({"value": "Введіть ID групи"})


@require_POST
def change_churn_status(request: WSGIRequest) -> JsonResponse:
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
def add_new_churn(request: WSGIRequest) -> HttpResponseRedirect:
    churn_id = request.POST.get("churn_id")
    churn_status = request.POST.get("churn_status")
    teacher_id = request.POST.get("teacher")
    description = request.POST.get("description", "")
    churn_dto = ChurnRawDTO(
        churn_id=churn_id,
        status=churn_status,
        teacher_id=teacher_id,
        description=description
    )
    ChurnRepository.create_or_update_churn(churn_dto)

    next_url = request.POST.get("next", "/")
    return HttpResponseRedirect(next_url)


@require_GET
def get_open_lessons(request: WSGIRequest) -> JsonResponse:
    tutor = TutorProfile.objects.filter(user=request.user).first()
    teachers = tutor.related_teachers.all()
    groups = Group.objects.filter(teacher_id__in=list(teachers.values_list("lms_id", flat=True)),
                                  type__in=("regular", "individual", "Группа", "Индивидуальная"),
                                  office_id__in=list(tutor.offices.values_list("pk", flat=True)))

    open_lessons = []
    for group in groups:
        if group is None:
            continue
        group_service = GroupService(lms_service=LMSService, group_repository=GroupRepository)
        lesson_service = LessonService(lms_service=LMSService, group_service=group_service)
        lessons = lesson_service.get_lessons(group_id=group.lms_id)
        lessons = lesson_service.filter_open_lessons(lessons)
        for lesson in lessons:
            last_comment = TeacherComment.objects.filter(lesson_id=lesson.lesson_id,
                                                         teacher_id=lesson.teacher_id,
                                                         group_id=lesson.group_id,
                                                         tutor=tutor).order_by("-created_at").first()
            lesson.last_comment = last_comment.comment if last_comment else "Коментаря немає"

            open_lessons.append(asdict(lesson))

    return JsonResponse({"open_lessons": open_lessons})


@require_GET
def get_lesson_comments(request: WSGIRequest) -> JsonResponse:
    lesson_id = request.GET.get("lesson_id")
    teacher_id = request.GET.get("teacher_id")
    group_id = request.GET.get("group_id")
    tutor = TutorProfile.objects.filter(user=request.user).first()
    comments = TeacherComment.objects.filter(lesson_id=lesson_id, tutor=tutor, teacher_id=teacher_id, group_id=group_id)
    if comments.exists():
        comments = comments.values()
        return JsonResponse({"comments": list(comments)})
    return JsonResponse({"comments": []})


@require_GET
def get_churns(request: WSGIRequest) -> JsonResponse:
    teachers = (
        TutorProfile.objects.filter(user=request.user)
        .first()
        .related_teachers
        .values_list("pk", flat=True)
    )
    churns = ChurnRepository.get_churns_by_teachers(teachers)
    churn_list = list()
    for churn in churns:
        churn_list.append(asdict(churn))
    return JsonResponse({"churns": churn_list})



