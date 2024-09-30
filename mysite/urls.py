"""
URL configuration for laba_rip1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetShow),
    path('info/<int:id>/', views.Info, name='info_url'),
    path('show/<int:show_id>/', views.show, name='cart_by_id'),
    path('topic/<int:topic_id>/add_to_show/', views.add_topic),
    path('show/<int:show_id>/delete/', views.delete_show)
]

#DB