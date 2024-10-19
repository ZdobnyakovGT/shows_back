from django.http import HttpResponse
import requests
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
import psycopg2
from django.db import connection
from .models import Shows, Topics, ShowTopic
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from .serializers import *
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user
from rest_framework.decorators import api_view, permission_classes


def get_draft_show(request):
    user = identity_user(request)

    if user is None:
        return None

    show = Shows.objects.filter(creator=user).filter(status=1).first()

    return show


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_topic(request):
    topic_name = request.GET.get("topic_name", "")

    topics = Topics.objects.filter(status=1)

    if topic_name:
        topics = topics.filter(name__icontains=topic_name)

    serializer = TopicSerializer(topics, many=True)

    draft_show = get_draft_show(request)

    resp = {
        "topics": serializer.data,
        "topics_count": ShowTopic.objects.filter(showw=draft_show).count() if draft_show else None,
        "draft_show_id": draft_show.pk if draft_show else None
    }

    return Response(resp)


#подробнее
@api_view(["GET"])
def get_topic_by_id(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)
    serializer = TopicSerializer(topic)

    return Response(serializer.data)


#обновить тему
@swagger_auto_schema(method='put', request_body=TopicSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_topic(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)

    name = request.data.get("name")
    if name is not None:
        topic.name = name
        topic.save()

    serializer = TopicSerializer(topic, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


#создать тему
@api_view(["POST"])
@permission_classes([IsModerator])
def create_topic(request):
    topic = Topics.objects.create()

    serializer = TopicSerializer(topic)

    return Response(serializer.data)

#удалить тему
@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_topic(request, topic_id):
    if not Topics.objects.filter(pk=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(pk=topic_id)
    topic.status = '0'
    topic.save()

    topics = Topics.objects.filter(status=1)
    serializer = TopicSerializer(topics, many=True)

    return Response(serializer.data)


#добавление
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_topic_to_show(request, topic_id):
    if not Topics.objects.filter(topic_id=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(topic_id=topic_id)

    draft_show = get_draft_show(request)

    if draft_show is None:
        draft_show = Shows.objects.create(
            creator=identity_user(request)
        )
        draft_show.save()


    if ShowTopic.objects.filter(showw=draft_show, topic=topic).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    item = ShowTopic.objects.create()
    item.showw = draft_show
    item.topic = topic
    item.save()

    serializer = ShowSerializer(draft_show)
    return Response(serializer.data["topics"])


# изменить избр
@api_view(["POST"])
@permission_classes([IsModerator])
def update_topic_image(request, topic_id):
    if not Topics.objects.filter(topic_id=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    topic = Topics.objects.get(topic_id=topic_id)

    image = request.data.get("photo_url")
    if image is not None:
        topic.photo_url = image
        topic.save()

    serializer = TopicSerializer(topic)

    return Response(serializer.data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_shows(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    shows = Shows.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_staff:
        shows = shows.filter(creator=user)

    if status > 0:
        shows = shows.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        shows = shows.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        shows = shows.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = ShowsSerializer(shows, many=True)

    return Response(serializer.data)


# заявка
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_show_by_id(request, show_id):
    user = identity_user(request)

    if not Shows.objects.filter(show_id=show_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    showw = Shows.objects.get(show_id=show_id)
    serializer = ShowSerializer(showw)

    return Response(serializer.data)


# обновить заявку
@swagger_auto_schema(method='put', request_body=ShowSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_show(request, show_id):
    user = identity_user(request)

    if not Shows.objects.filter(show_id=show_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(show_id=show_id)
    serializer = ShowSerializer(show, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


#  статус подтвержено
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, show_id):
    user = identity_user(request)

    if not Shows.objects.filter(show_id=show_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(show_id=show_id)

    # if show.status != 1:
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show.status = 2
    show.submitted_at = timezone.now()
    show.save()

    serializer = ShowSerializer(show)

    return Response(serializer.data)


# статус выполнено
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, show_id):
    if not Shows.objects.filter(show_id=show_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show = Shows.objects.get(show_id=show_id)

    if show.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show.completed_at = timezone.now()
    show.status = request_status
    show.moderator = identity_user(request)
    show.save()

    serializer = ShowSerializer(show)

    return Response(serializer.data)


# удаление заявки
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_show(request, show_id):
    user = identity_user(request)

    if not Shows.objects.filter(show_id=show_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    show = Shows.objects.get(show_id=show_id)

    if show.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    show.status = 5
    show.save()

    return Response(status=status.HTTP_200_OK)


# удаление из заявки
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_topic_from_show(request, showw, topic_id):
    user = identity_user(request)
    
    if not Shows.objects.filter(pk=showw, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ShowTopic.objects.filter(showw=showw, topic_id=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ShowTopic.objects.get(showw=showw, topic_id=topic_id)
    item.delete()

    show = Shows.objects.get(show_id=showw)

    serializer = ShowSerializer(show)
    topics = serializer.data["topics"]

    if len(topics) == 0:
        show.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(topics)


# изменить тему в выставке
@swagger_auto_schema(method='PUT', request_body=ShowTopicSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_topic_in_show(request, show_id, topic_id):
    user = identity_user(request)
    
    if not Shows.objects.filter(pk=show_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ShowTopic.objects.filter(showw=show_id, topic_id=topic_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ShowTopic.objects.get(topic_id=topic_id, showw_id=show_id)
    item.is_main = 1
    item.save

    serializer = ShowTopicSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


# регистрация
@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)

    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    access_token = create_access_token(user.id)

    serializer = UserSerializer(user)

    response = Response(serializer.data, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=True)

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    serializer = UserSerializer(user)

    response = Response(serializer.data, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=True)

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
