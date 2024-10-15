from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
import psycopg2
from django.db import connection
from .models import Shows, Topics, ShowTopic
from django.contrib.auth.models import User
from django.utils import timezone


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
    with connection.cursor() as cursor:
        cursor.execute("UPDATE shows SET status = 5 WHERE show_id = %s", [show_id])

    return redirect("/")
