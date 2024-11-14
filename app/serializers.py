from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers
from collections import OrderedDict

  
class TopicSerializer(serializers.ModelSerializer):
    is_main = serializers.SerializerMethodField()

    def get_is_main(self, topic):
        show = self.context.get("show")
        if show:
            show_topic = ShowTopic.objects.filter(showw=show, topic=topic).first()
            return show_topic.is_main if show_topic else None
        return None
    class Meta:
        model = Topics
        fields = ('topic_id', 'name', 'description', 'photo_url', 'is_main')
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class ShowSerializer(serializers.ModelSerializer):
    topics = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    topics_count = serializers.SerializerMethodField()

    def get_creator(self, show):
        return show.creator.username

    def get_moderator(self, show):
        if show.moderator:
            return show.moderator.username
    
    def get_topics_count(self, show):
        return ShowTopic.objects.filter(showw=show).count()
        
    def get_topics(self, show):
        items = ShowTopic.objects.filter(showw=show)
        serializer = TopicSerializer([item.topic for item in items], many=True)
        return serializer.data

    class Meta:
        model = Shows
        fields = '__all__'
        extra_fields = ['topics_count']
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class ShowsSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    topics_count = serializers.SerializerMethodField()

    def get_creator(self, show):
        return show.creator.username

    def get_moderator(self, show):
        if show.moderator:
            return show.moderator.username
        
    def get_topics_count(self, show):
        return ShowTopic.objects.filter(showw=show).count()

    class Meta:
        model = Shows
        fields = "__all__"
        extra_fields = ['topics_count']
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class ShowTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTopic
        fields = "__all__"
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'date_joined', 'password', 'username')
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
    

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
