from django.http import HttpResponse
import requests
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
import psycopg2
from django.db import connection
from .models import Shows, Topics, ShowTopic
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *


#основная страница
def GetShow(request):

    topics_s = request.GET.get("search-theme", "")
    topics = Topics.objects.filter(name__icontains=topics_s).filter(status='1')
    draft_show = get_draft_show()
    
    context = {
        "topics_s": topics_s,
        "topics": topics
    }

    if draft_show:
        context["topic_count"] = ShowTopic.objects.filter(showw=draft_show).count()
        context["draft_show"] = draft_show

    return render(request, "topics.html", context)


# корзина
def show(request, show_id):

    
    context = {
        "show": Shows.objects.get(show_id=show_id),
    }

    return render(request, "show.html", context)


#подробнее
def Info(request, id):
    topic = Topics.objects.get(topic_id=id) 
    return render(request, 'topic_info.html', {'data' : topic})


#черновик
def get_draft_show():
    current_user = get_current_user()
    return Shows.objects.filter(creator=current_user, status=1).first()

#добавить
def add_topic(request, topic_id):
    topic = Topics.objects.get(pk=topic_id)
    draft_show = get_draft_show()

    if draft_show is None:
        draft_show = Shows.objects.create(
            creator = get_current_user(),
            created_at = timezone.now()
        )
        draft_show.save()


    if ShowTopic.objects.filter(showw=draft_show, topic=topic).exists():
        return redirect("/")

    item = ShowTopic(
        showw=draft_show,
        topic=topic
    )
    item.save()

    return redirect("/")


# текущий юзер
def get_current_user():
    return User.objects.filter(is_superuser=False).first()


# удалить
def delete_show(request, show_id):
    submitted_time = timezone.now()
    with connection.cursor() as cursor:
        cursor.execute("UPDATE shows SET status = 5, submitted_at = %s WHERE show_id = %s", [submitted_time, show_id])

    return redirect("/")








def get_draft_show():
    return Shows.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


#поиск
@api_view(["GET"])
def search_topic(request):
    query = request.GET.get("search-theme", "")
    topics = Topics.objects.filter(name__icontains=query).filter(status='1')

    serializer = TopicSerializer(topics, many=True)

    draft_show = get_draft_show()

    resp = {
        "topics": serializer.data,
        "draft_show": draft_show.pk if draft_show else None
    }

    return Response(resp)


@api_view(["GET"])
def get_climber_by_id(request, climber_id):
    if not Climber.objects.filter(pk=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    climber = Climber.objects.get(pk=climber_id)
    serializer = ClimberSerializer(climber, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_climber(request, climber_id):
    if not Climber.objects.filter(pk=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    climber = Climber.objects.get(pk=climber_id)

    image = request.data.get("image")
    if image is not None:
        climber.image = image
        climber.save()

    serializer = ClimberSerializer(climber, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_climber(request):
    Climber.objects.create()

    climbers = Climber.objects.filter(status=1)
    serializer = ClimberSerializer(climbers, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_climber(request, climber_id):
    if not Climber.objects.filter(pk=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    climber = Climber.objects.get(pk=climber_id)
    climber.status = 2
    climber.save()

    climbers = Climber.objects.filter(status=1)
    serializer = ClimberSerializer(climbers, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_climber_to_expedition(request, climber_id):
    if not Climber.objects.filter(pk=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    climber = Climber.objects.get(pk=climber_id)

    draft_expedition = get_draft_expedition()

    if draft_expedition is None:
        draft_expedition = Expedition.objects.create()
        draft_expedition.owner = get_user()
        draft_expedition.date_created = timezone.now()
        draft_expedition.save()

    if ClimberExpedition.objects.filter(expedition=draft_expedition, climber=climber).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    item = ClimberExpedition.objects.create()
    item.expedition = draft_expedition
    item.climber = climber
    item.save()

    serializer = ExpeditionSerializer(draft_expedition, many=False)

    return Response(serializer.data["climbers"])


@api_view(["GET"])
def get_climber_image(request, climber_id):
    if not Climber.objects.filter(pk=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    climber = Climber.objects.get(pk=climber_id)
    response = requests.get(climber.image.url.replace("localhost", "minio"))

    return HttpResponse(response, content_type="image/png")


@api_view(["PUT"])
def update_climber_image(request, climber_id):
    if not Climber.objects.filter(pk=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    climber = Climber.objects.get(pk=climber_id)

    image = request.data.get("image")
    if image is not None:
        climber.image = image
        climber.save()

    serializer = ClimberSerializer(climber)

    return Response(serializer.data)


@api_view(["GET"])
def search_expeditions(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    expeditions = Expedition.objects.exclude(status__in=[1, 5])

    if status > 0:
        expeditions = expeditions.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        expeditions = expeditions.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        expeditions = expeditions.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = ExpeditionsSerializer(expeditions, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_expedition_by_id(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)
    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_expedition(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)
    serializer = ExpeditionSerializer(expedition, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.status = 2
    expedition.date_formation = timezone.now()
    expedition.save()

    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.date_complete = timezone.now()
    expedition.status = request_status
    expedition.moderator = get_moderator()
    expedition.save()

    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_expedition(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.status = 5
    expedition.save()

    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_climber_from_expedition(request, expedition_id, climber_id):
    if not ClimberExpedition.objects.filter(expedition_id=expedition_id, climber_id=climber_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ClimberExpedition.objects.get(expedition_id=expedition_id, climber_id=climber_id)
    item.delete()

    expedition = Expedition.objects.get(pk=expedition_id)

    serializer = ExpeditionSerializer(expedition, many=False)
    climbers = serializer.data["climbers"]

    if len(climbers) == 0:
        expedition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(climbers)


@api_view(["PUT"])
def update_climber_in_expedition(request, expedition_id, climber_id):
    if not ClimberExpedition.objects.filter(climber_id=climber_id, expedition_id=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ClimberExpedition.objects.get(climber_id=climber_id, expedition_id=expedition_id)

    serializer = ClimberExpeditionSerializer(item, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, many=False, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)