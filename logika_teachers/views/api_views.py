import json

from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST, require_GET

from logika_teachers.services.lms_service import LMSService
from logika_teachers.models import PredictedChurn


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
        PredictedChurn.objects.create(churn_id=churn_id,
                                      status=churn_status,
                                      description=description,
                                      teacher_id=teacher_id)

    next_url = request.POST.get("next", "/")
    return HttpResponseRedirect(next_url)
