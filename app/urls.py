from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/topics/search/', search_topic),  # GET
    path('api/topics/<int:topic_id>/', get_topic_by_id),  # GET
    # path('api/topics/<int:topic_id>/image/', get_topic_image),  # GET
    path('api/topics/<int:topic_id>/update/', update_topic),  # PUT
    path('api/topics/<int:topic_id>/update_image/', update_topic_image),  # POST
    path('api/topics/<int:topic_id>/delete/', delete_topic),  # DELETE
    path('api/topics/create/', create_topic),  # POST
    path('api/topics/<int:topic_id>/add_to_show/', add_topic_to_show),  # POST

    # Набор методов для заявок
    path('api/shows/search/', search_shows),  # GET
    path('api/shows/<int:show_id>/', get_show_by_id),  # GET
    path('api/shows/<int:show_id>/update/', update_show),  # PUT
    path('api/shows/<int:show_id>/update_status_user/', update_status_user),  # PUT
    path('api/shows/<int:show_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/shows/<int:show_id>/delete/', delete_show),  # DELETE

    # Набор методов для м-м
    path('api/shows/<int:show_id>/update_topic/<int:topic_id>/', update_topic_in_show),  # PUT
    path('api/shows/<int:showw>/delete_topic/<int:topic_id>/', delete_topic_from_show),  # DELETE

    # Набор методов пользователей
    path('api/users/register/', register), # POST
    path('api/users/<int:user_id>/update/', update_user), # PUT
]