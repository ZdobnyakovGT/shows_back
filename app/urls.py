from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/topics/search/', search_climbers),  # GET
    path('api/topics/<int:topic_id>/', get_climber_by_id),  # GET
    path('api/topics/<int:topic_id>/image/', get_climber_image),  # GET
    path('api/topics/<int:topic_id>/update/', update_climber),  # PUT
    path('api/topics/<int:topic_id>/update_image/', update_climber_image),  # PUT
    path('api/topics/<int:topic_id>/delete/', delete_climber),  # DELETE
    path('api/topics/create/', create_climber),  # POST
    path('api/topics/<int:topic_id>/add_to_show/', add_climber_to_expedition),  # POST

    # Набор методов для заявок
    path('api/shows/search/', search_expeditions),  # GET
    path('api/shows/<int:show_id>/', get_expedition_by_id),  # GET
    path('api/shows/<int:show_id>/update/', update_expedition),  # PUT
    path('api/shows/<int:show_id>/update_status_user/', update_status_user),  # PUT
    path('api/shows/<int:show_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/shows/<int:show_id>/delete/', delete_expedition),  # DELETE

    # Набор методов для м-м
    path('api/shows/<int:show_id>/update_topic/<int:topic_id>/', update_climber_in_expedition),  # PUT
    path('api/shows/<int:show_id>/delete_topic/<int:topic_id>/', delete_climber_from_expedition),  # DELETE

    # Набор методов пользователей
    path('api/users/register/', register), # POST
    path('api/users/<int:user_id>/update/', update_user), # PUT
]