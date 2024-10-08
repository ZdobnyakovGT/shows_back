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


# #основная страница
# def GetShow(request):

#     topics_s = request.GET.get("search-theme", "")
#     topics = Topics.objects.filter(name__icontains=topics_s).filter(status='1')
#     draft_show = get_draft_show()
    
#     context = {
#         "topics_s": topics_s,
#         "topics": topics
#     }

#     if draft_show:
#         context["topic_count"] = ShowTopic.objects.filter(showw=draft_show).count()
#         context["draft_show"] = draft_show

#     return render(request, "topics.html", context)


# # корзина
# def show(request, show_id):

    
#     context = {
#         "show": Shows.objects.get(show_id=show_id),
#     }

#     return render(request, "show.html", context)


# #подробнее
# def Info(request, id):
#     topic = Topics.objects.get(topic_id=id) 
#     return render(request, 'topic_info.html', {'data' : topic})


# #черновик
# def get_draft_show():
#     current_user = get_current_user()
#     return Shows.objects.filter(creator=current_user, status=1).first()

# #добавить
# def add_topic(request, topic_id):
#     topic = Topics.objects.get(pk=topic_id)
#     draft_show = get_draft_show()

#     if draft_show is None:
#         draft_show = Shows.objects.create(
#             creator = get_current_user(),
#             created_at = timezone.now()
#         )
#         draft_show.save()


#     if ShowTopic.objects.filter(showw=draft_show, topic=topic).exists():
#         return redirect("/")

#     item = ShowTopic(
#         showw=draft_show,
#         topic=topic
#     )
#     item.save()

#     return redirect("/")


# # текущий юзер
# def get_current_user():
#     return User.objects.filter(is_superuser=False).first()


# # удалить
# def delete_show(request, show_id):
#     submitted_time = timezone.now()
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE shows SET status = 5, submitted_at = %s WHERE show_id = %s", [submitted_time, show_id])

#     return redirect("/")








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


#подробнее
@api_view(["GET"])
def get_topic_by_id(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)
    serializer = TopicSerializer(topic, many=False)

    return Response(serializer.data)


#обновить тему
@api_view(["PUT"])
def update_topic(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)

    image = request.data.get("image")
    if image is not None:
        topic.image = image
        topic.save()

    serializer = TopicSerializer(topic, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


#создать тему
@api_view(["POST"])
def create_topic(request):
    Topics.objects.create()

    topics = Topics.objects.filter(status=1)
    serializer = TopicSerializer(topics, many=True)

    return Response(serializer.data)

#удалить тему
@api_view(["DELETE"])
def delete_topic(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)
    topic.status = 2
    topic.save()

    topics = Topics.objects.filter(status=1)
    serializer = TopicSerializer(topics, many=True)

    return Response(serializer.data)


#добавление
@api_view(["POST"])
def add_topic_to_show(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)

    draft_show = get_draft_show()

    if draft_show is None:
        draft_show = Shows.objects.create()
        draft_show.creator = get_user()
        draft_show.created_at = timezone.now()
        draft_show.save()

    if ShowTopic.objects.filter(expedition=draft_show, topic=topic).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    item = ShowTopic.objects.create()
    item.showw = draft_show
    item.topic = topic
    item.save()

    serializer = ShowSerializer(draft_show, many=False)

    return Response(serializer.data["topics"])


# изображение
@api_view(["GET"])
def get_topic_image(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)
    response = requests.get(topic.image.url.replace("localhost", "minio"))

    return HttpResponse(response, content_type="image/png")


# изменить избр
@api_view(["PUT"])
def update_topic_image(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)

    image = request.data.get("image")
    if image is not None:
        topic.image = image
        topic.save()

    serializer = TopicSerializer(topic)

    return Response(serializer.data)



# @api_view(["GET"])
# def search_shows(request):
#     status = int(request.GET.get("status", 0))
#     date_formation_start = request.GET.get("date_formation_start")
#     date_formation_end = request.GET.get("date_formation_end")

#     expeditions = Expedition.objects.exclude(status__in=[1, 5])

#     if status > 0:
#         expeditions = expeditions.filter(status=status)

#     if date_formation_start and parse_datetime(date_formation_start):
#         expeditions = expeditions.filter(date_formation__gte=parse_datetime(date_formation_start))

#     if date_formation_end and parse_datetime(date_formation_end):
#         expeditions = expeditions.filter(date_formation__lt=parse_datetime(date_formation_end))

#     serializer = ExpeditionsSerializer(expeditions, many=True)

#     return Response(serializer.data)


# заявка
@api_view(["GET"])
def get_show_by_id(request, show_id):
    if not Shows.objects.filter(pk=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(pk=show_id)
    serializer = ShowSerializer(show, many=False)

    return Response(serializer.data)


# обновить заявку
@api_view(["PUT"])
def update_show(request, show_id):
    if not Shows.objects.filter(pk=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(pk=show_id)
    serializer = ShowSerializer(show, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


#  статус подтвержено
@api_view(["PUT"])
def update_status_user(request, show_id):
    if not Shows.objects.filter(pk=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(pk=show_id)

    if show.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show.status = 2
    show.submitted_at = timezone.now()
    show.save()

    serializer = ShowSerializer(show, many=False)

    return Response(serializer.data)


# статус выполнено
@api_view(["PUT"])
def update_status_admin(request, show_id):
    if not Shows.objects.filter(pk=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show = Shows.objects.get(pk=show_id)

    if show.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show.completed_at = timezone.now()
    show.status = request_status
    show.moderator = get_moderator()
    show.save()

    serializer = ShowSerializer(show, many=False)

    return Response(serializer.data)


# удаление заявки
@api_view(["DELETE"])
def delete_show(request, show_id):
    if not Shows.objects.filter(pk=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(pk=show_id)

    if show.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show.status = 5
    show.save()

    serializer = ShowSerializer(show, many=False)

    return Response(serializer.data)


# удвление из заявки
@api_view(["DELETE"])
def delete_topic_from_show(request, show_id, topic_id):
    if not ShowTopic.objects.filter(show_id=show_id, topic_id=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ShowTopic.objects.get(show_id=show_id, topic_id=topic_id)
    item.delete()

    show = Shows.objects.get(pk=show_id)

    serializer = ShowSerializer(show, many=False)
    topics = serializer.data["topics"]

    if len(topics) == 0:
        show.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(topics)


# изменить тему в выставке
@api_view(["PUT"])
def update_topic_in_show(request, show_id, topic_id):
    if not ShowTopic.objects.filter(climber_id=topic_id, expedition_id=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ShowTopic.objects.get(topic_id=topic_id, show_id=show_id)

    serializer = ShowTopicSerializer(item, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


# регистрация
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