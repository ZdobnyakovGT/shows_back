# from django.contrib import admin
# from django.urls import path
# from app import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.GetShow),
#     path('info/<int:id>/', views.Info, name='info_url'),
#     path('show/<int:show_id>/', views.show, name='cart_by_id'),
#     path('topic/<int:topic_id>/add_to_show/', views.add_topic),
#     path('show/<int:show_id>/delete/', views.delete_show)
# ]



from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('app.urls')),
    path('admin/', admin.site.urls)
]