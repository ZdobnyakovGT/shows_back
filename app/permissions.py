
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.permissions import BasePermission
import redis
from django.conf import settings
from django.shortcuts import get_object_or_404

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)



class IsModerator(BasePermission):
    def has_permission(self, request, view):
        try:
            username = session_storage.get(request.COOKIES["session_id"])
            username = username.decode('utf-8')
        except:
            return False
        
        user = get_object_or_404(User,username=username)
        return  bool(user.is_superuser or user.is_staff)
