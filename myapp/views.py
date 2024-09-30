from django.http import HttpResponse
from django.shortcuts import render
from datetime import date
# from models import Application, Service


def GetInfo(id=None):
    arr = [
            {'nm': 'Искусство и Культура', 'im': 'http://127.0.0.1:9000/riplab1/photo/im1.png', 'description': 'Категория включает в себя выставки, посвящённые живописи, скульптуре, архитектуре, литературе, театру, кино и музыке. Это могут быть как исторические экспозиции, так и современные художественные проекты.', 'id': 1},
            {'nm': 'Наука и Технологии', 'im': 'http://127.0.0.1:9000/riplab1/photo/im2.png', 'description': 'Здесь размещаются выставки, посвящённые научным открытиям, изобретениям, развитию технологий, а также инновациям будущего. Темы могут охватывать разные области науки — физику, биологию, космологию, информатику и другие.', 'id': 2},
            {'nm': 'История и Наследие', 'im': 'http://127.0.0.1:9000/riplab1/photo/im3.png', 'description': 'Категория для выставок, посвящённых историческим событиям, культурному наследию, важным периодам в истории человечества и древним цивилизациям. Это могут быть экспозиции о ключевых фигурах, эпохах и мировом наследии.', 'id': 3},
            {'nm': 'Природа и Экология', 'im': 'http://127.0.0.1:9000/riplab1/photo/im4.png',  'description': 'Выставки в этой категории сосредоточены на окружающей среде, экосистемах, изменении климата и природоохранных инициативах. Здесь можно изучать природные явления, флору и фауну, а также экологические проблемы и их решения.', 'id': 4},
            {'nm': 'Цифровые искусства и новые медиа', 'im': 'http://127.0.0.1:9000/riplab1/photo/im5.png', 'description': 'Выставки, которые исследуют влияние цифровых технологий на искусство, включая мультимедийные инсталляции, видеоарт, 3D-графику и искусственный интеллект в креативной индустрии. Это пространство для современных цифровых проектов.', 'id': 5},
            {'nm': 'Музыка и Звук', 'im': 'http://127.0.0.1:9000/riplab1/photo/im6.png',  'description': 'Экспозиции, посвящённые истории музыки, музыкальным жанрам, известным композиторам и исполнителям. Включает как классическую, так и современную музыку, а также изучение звуковой культуры.', 'id': 6},
            {'nm': 'Человеческое тело', 'im': 'http://127.0.0.1:9000/riplab1/photo/im7.png', 'description': 'Научная выставка, исследующая историю и искусство анатомии и медицины. Экспонаты включают изображения человеческого тела, созданные для научных исследований, а также информацию о развитии медицинских технологий и научных открытий, которые повлияли на здравоохранение. Здесь можно проследить, как знания о теле человека развивались от древности до современных технологий.', 'id': 7},
            {'nm': 'Спорт и Здоровье', 'im': 'http://127.0.0.1:9000/riplab1/photo/im8.png', 'description': 'Категория для выставок, связанных с историей спорта, олимпийским движением, физическим здоровьем, фитнесом и медициной. Здесь могут быть представлены как спортивные достижения, так и темы, связанные с медицинскими инновациями.', 'id': 8}
        ]
    return arr if id is None else arr[id-1]


def GetTime():
    return {'id' : '1',
            'data' : [
                {'nm': 'Природа и Экология', 'im': 'http://127.0.0.1:9000/riplab1/photo/im4.png', 'id': 4},
                {'nm': 'Человеческое тело', 'im': 'http://127.0.0.1:9000/riplab1/photo/im7.png', 'id': 7},
                {'nm': 'Спорт и Здоровье', 'im': 'http://127.0.0.1:9000/riplab1/photo/im8.png',  'id': 8}
    ]}


def GetShow(request):
    if request.method == 'GET':
        search_query = request.GET.get('search-theme', '').lower()  # Приводим поисковый запрос к нижнему регистру
        topics = GetInfo()
        
        if search_query:
            topics = list(filter(lambda x: search_query in x['nm'].lower(), topics))
        
        return render(request, 'topics.html', {
            'data': {
                'cards': topics,
                'id': int(GetTime()['id']),
                'value': search_query,
                'len': len(GetTime()['data'])
            },
            'search_query': search_query
        })
    
    # Возвращаем ошибку 405, если метод запроса не поддерживается
    return HttpResponse("Method not allowed", status=405)


def Info(request, id):
    return render(request, 'topic_info.html', {'data' : GetInfo(id)})


def GetCartById(request, id):
    show = GetTime()
    return render(request, 'show.html', {
        'data': {
            'show_topic': show['data'],
        }
    })











# def applicationList(request):
#     return render(request, 'appls.html', {'data' : {
#         'form_date': date.today(),
#         'appls': Application.objects.all()
#     }})

# def GetApplication(request, id):
#     return render(request, 'appl.html', {'data' : {
#         'form_date': date.today(),
#         'appl': Application.objects.filter(id=id)[0]
#     }})