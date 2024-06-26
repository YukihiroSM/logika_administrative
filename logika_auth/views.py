from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from logika_teachers.models import TutorProfile, RegionalTutorProfile
from utils.get_user_role import get_user_role
from logika_general.models import (
    ClientManagerProfile,
    TerritorialManagerProfile,
    RegionalManagerProfile,
)


@csrf_exempt
def create_user(request):
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    if request.META["REMOTE_ADDR"] != "127.0.0.1":
        return JsonResponse(
            {"status": "False", "details": "Request received from not authorized IP"}
        )
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    role = request_data_GET.get("role")[0]
    territorial_manager = request_data_GET.get("territorial_manager")
    if territorial_manager:
        territorial_manager = territorial_manager[0]
    if role == "territorial_manager_km" and not territorial_manager:
        return JsonResponse(
            {
                "status": "False",
                "details": "Client manager must be followed by territorial_manager",
            }
        )

    username = f"{first_name}_{last_name}"
    raw_password = "abcdefgh"
    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
    if user_obj:
        return JsonResponse({"status": "False", "details": "User already exists."})
    user = User.objects.create_user(username=username, password=raw_password)
    if user:
        user.first_name = first_name
        user.last_name = last_name
        if role == "tutor":
            profile = TutorProfile(user=user)
            profile.save()
        elif role == "general_tutor":
            profile = RegionalTutorProfile(user=user)
            profile.save()
        elif role == "regional":
            profile = RegionalManagerProfile(user=user)
            profile.save()
        elif role == "territorial_manager":
            profile = TerritorialManagerProfile(user=user)
            profile.save()
        elif role == "territorial_manager_km":
            profile = ClientManagerProfile(user=user)
            profile.save()
            if territorial_manager:
                tm_first_name, tm_second_name = territorial_manager.split()[:2]
                tm_user = User.objects.filter(
                    first_name=tm_first_name, last_name=tm_second_name
                ).first()
                if tm_user:
                    tm_profile = TerritorialManagerProfile.objects.filter(
                        user=tm_user
                    ).first()
                    if tm_profile:
                        profile.related_tms.add(tm_profile)
                        profile.save()
        user.save()
        return JsonResponse(
            {
                "status": "True",
                "request_data_GET": request_data_GET,
                "request_data_POST": request_data_POST,
            }
        )
    else:
        return JsonResponse({"status": "False", "details": "Unable to create user"})


@csrf_exempt
def deactivate_user(request):
    if request.META["REMOTE_ADDR"] != "127.0.0.1":
        return JsonResponse(
            {"status": "False", "details": "Request received from not authorized IP"}
        )
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
    if user_obj:
        user_obj.is_active = False
        user_obj.save()
        return JsonResponse(
            {
                "status": "True",
                "request_data_GET": request_data_GET,
                "request_data_POST": request_data_POST,
            }
        )
    else:
        return JsonResponse({"status": "False", "details": "User not found"})


@csrf_exempt
def auth_user(request):
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    token = request_data_GET.get("token")[0]
    user_obj = User.objects.filter(
        first_name=first_name,
        last_name=last_name,
        username__contains=first_name.strip(),
    ).first()
    user_role = get_user_role(user_obj)

    if user_obj:
        if not user_obj.is_active:
            return JsonResponse(
                {"status": "False", "details": "User is out of activity."}
            )
        username = user_obj.username
        profile = None
        if user_role == "tutor":
            profile = TutorProfile.objects.filter(user=user_obj).first()
        elif user_role == "regional_tutor":
            profile = RegionalTutorProfile.objects.filter(user=user_obj).first()
        elif user_role == "regional_manager":
            profile = RegionalManagerProfile.objects.filter(user=user_obj).first()
        elif user_role == "territorial_manager":
            profile = TerritorialManagerProfile.objects.filter(user=user_obj).first()
        elif user_role == "client_manager":
            profile = ClientManagerProfile.objects.filter(user=user_obj).first()

        if token != profile.auth_token:
            if request.META["REMOTE_ADDR"] != "127.0.0.1":
                return JsonResponse(
                    {
                        "status": "False",
                        "details": "Request received from not authorized IP",
                    }
                )
            profile.auth_token = token
            timestamp = datetime.now(timezone.utc)
            profile.login_timestamp = timestamp
            profile.save()
            return JsonResponse(
                {
                    "status": "True",
                    "request_data_GET": request_data_GET,
                    "request_data_POST": request_data_POST,
                }
            )
        else:
            time_now = datetime.now(timezone.utc)
            if time_now - profile.login_timestamp < timedelta(minutes=1):
                password = "abcdefgh"
                user = authenticate(username=username, password=password)
            else:
                return JsonResponse(
                    {"status": "False", "details": "Out of authorisation time"}
                )

        if user is not None:
            login(request, user)
            return redirect("/")
    return JsonResponse(
        {
            "status": "True",
            "request_data_GET": request_data_GET,
            "request_data_POST": request_data_POST,
        }
    )


@csrf_exempt
def update_user(request):
    if request.META["REMOTE_ADDR"] != "127.0.0.1":
        return JsonResponse(
            {"status": "False", "details": "Request received from not authorized IP"}
        )
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    first_name_new = request_data_GET.get("first_name_new")[0]
    last_name_new = request_data_GET.get("last_name_new")[0]
    role_new = request_data_GET.get("role_new")[0]

    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
    user_role = get_user_role(user_obj)
    if user_obj:
        if role_new == "tutor":
            profile_class = TutorProfile
        elif role_new == "general_tutor":
            profile_class = RegionalTutorProfile
        elif role_new == "regional":
            profile_class = RegionalManagerProfile
        elif role_new == "territorial_manager":
            profile_class = TerritorialManagerProfile
        elif role_new == "territorial_manager_km":
            profile_class = ClientManagerProfile
        profile = profile_class.objects.filter(user=user_obj).first()
        if not profile:
            profile = profile_class(user=user_obj)
            profile.save()
        profile = profile_class.objects.filter(user=user_obj).first()
        user_obj.first_name = first_name_new
        user_obj.last_name = last_name_new
        user_obj.username = f"{first_name_new}_{last_name_new}"
        if role_new == "territorial_manager_km":
            try:
                territorial_new = request_data_GET.get("territorial_manager_new")[0]
            except:
                return JsonResponse(
                    {
                        "status": "False",
                        "details": "Territorial manager not specified for client manager",
                    }
                )
            tm_first_name = territorial_new.split()[0]
            tm_last_name = territorial_new.split()[1]
            tm_user = User.objects.get(first_name=tm_first_name, last_name=tm_last_name)
            if tm_user:
                tm_profile = TerritorialManagerProfile.objects.filter(
                    user=tm_user
                ).first()
                if tm_profile:
                    profile.related_tms.add(tm_profile)
        user_obj.save()
        profile.save()

        return JsonResponse(
            {
                "status": "True",
                "request_data_GET": request_data_GET,
                "request_data_POST": request_data_POST,
            }
        )
    else:
        request_data_GET = dict(request.GET)
        request_data_POST = dict(request.POST)
        if request.META["REMOTE_ADDR"] != "127.0.0.1":
            return JsonResponse(
                {
                    "status": "False",
                    "details": "Request received from not authorized IP",
                }
            )
        first_name = request_data_GET.get("first_name_new")[0]
        last_name = request_data_GET.get("last_name_new")[0]
        role = request_data_GET.get("role_new")[0]
        territorial_manager = request_data_GET.get("territorial_manager_new")
        if territorial_manager:
            territorial_manager = territorial_manager[0]
        if role == "territorial_manager_km" and not territorial_manager:
            return JsonResponse(
                {
                    "status": "False",
                    "details": "Client manager must be followed by territorial_manager",
                }
            )

        username = f"{first_name}_{last_name}"
        raw_password = "abcdefgh"
        user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
        if user_obj:
            return JsonResponse({"status": "False", "details": "User already exists."})
        user = User.objects.create_user(username=username, password=raw_password)
        if user:
            user.first_name = first_name
            user.last_name = last_name
            if role == "tutor":
                profile = TutorProfile(user=user)
                profile.save()
            elif role == "general_tutor":
                profile = RegionalTutorProfile(user=user)
                profile.save()
            elif role == "regional":
                profile = RegionalManagerProfile(user=user)
                profile.save()
            elif role == "territorial_manager":
                profile = TerritorialManagerProfile(user=user)
                profile.save()
            elif role == "territorial_manager_km":
                profile = ClientManagerProfile(user=user)
                profile.save()
                if territorial_manager:
                    tm_first_name, tm_second_name = territorial_manager.split()[:2]
                    tm_user = User.objects.filter(
                        first_name=tm_first_name, last_name=tm_second_name
                    ).first()
                    if tm_user:
                        tm_profile = TerritorialManagerProfile.objects.filter(
                            user=tm_user
                        ).first()
                        if tm_profile:
                            profile.related_tms.add(tm_profile)
                            profile.save()
            user.save()
            return JsonResponse(
                {
                    "status": "True",
                    "request_data_GET": request_data_GET,
                    "request_data_POST": request_data_POST,
                }
            )
        else:
            return JsonResponse({"status": "False", "details": "Unable to create user"})
