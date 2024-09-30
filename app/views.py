from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
import psycopg2
from django.db import connection
from .models import Shows, Topics, ShowTopic
from django.contrib.auth.models import User
from django.utils import timezone



# def GetInfo(id=None):
#     topics = Topics.objects.values('name', 'photo_url', 'description', 'topic_id', 'status').order_by('topic_id')
#     topics_list = list(topics)
#     print(topics_list)
#     return topics_list if id is None else topics_list[id-1]


# def GetTime():
#     return {'id' : '1',
#             'count' : '',
#             'name' : '',
#             'place' : '',
#             'date' : '',
#             'time' :  '',

#             'data' : [
#                 {'info' : GetInfo(4)},
#                 {'info' : GetInfo(7)},
#                 {'info' : GetInfo(8)}
#     ]}




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
        context["topic_count"] = len(draft_show.get_topics())
        context["draft_show"] = draft_show

    return render(request, "topics.html", context)


 # корзина
# def GetCartById(request, id):
#     show = GetTime()
#     return render(request, 'show.html', {
#         'data': {
#             'show_topic': show['data'],
#         }
#     })



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

    return Shows.objects.filter(status='1').first()

#добавить
def add_topic(request, topic_id):
    topic = Topics.objects.get(pk=topic_id)
    draft_show = get_draft_show()

    if draft_show is None:
        draft_show = Shows.objects.create()
        
        draft_show.creator = get_current_user().id



        draft_show.created_at = timezone.now()
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
    show = get_object_or_404(Shows, pk=show_id)  # Получаем шоу или возвращаем 404
    show.status = 5  # Меняем статус
    show.save()  # Сохраняем изменения
    return redirect("/")