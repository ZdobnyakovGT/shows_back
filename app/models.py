from django.db import models
from django.contrib.auth.models import User
from app.stats import STATUS_CHOICES


class ShowTopic(models.Model):
    mm_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey('Topics', models.DO_NOTHING, db_column='topic', blank=True, null=True)
    showw = models.ForeignKey('Shows', models.DO_NOTHING, db_column='showw', blank=True, null=True)
    topic_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'show_topic'
        verbose_name = "м-м"
        verbose_name_plural = "м-м"


class Shows(models.Model):
    show_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    # creator = models.ForeignKey(User, verbose_name="Создатель", on_delete=models.CASCADE, null=True, related_name='created_shows')  # related_name исправлено
    # moderator = models.ForeignKey(User, verbose_name="Модератор", on_delete=models.CASCADE, null=True, related_name='moderated_shows') 
    # creator = models.ForeignKey(User, verbose_name= "Создатель", on_delete=models.CASCADE, null=True, related_name='creator')
    # moderator = models.ForeignKey(User, verbose_name= "Модератор", on_delete=models.CASCADE, null=True, related_name='moderator')
    creator = models.IntegerField(blank=True, null=True)
    moderator = models.IntegerField(blank=True, null=True)
    show_date = models.DateField(blank=True, null=True)
    show_time = models.TimeField(blank=True, null=True)
    show_name = models.CharField(max_length=100, blank=True, null=True)
    show_place = models.CharField(max_length=100, blank=True, null=True)
    main_topic = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, default='1', blank=True, null=True)

    class Meta:
        db_table = 'shows'
        verbose_name = "Выставка"
        verbose_name_plural = "Выставки"
        # ordering = ('-date_formation', )

    # def __str__(self):
    #     return "Экспедиция №" + str(self.pk)

    def get_topics(self):
        res = []

        for item in ShowTopic.objects.filter(showw=self):
            tmp = item.topic
            tmp.count = item.topic_count
            res.append(tmp)

        return res

    def get_status(self):
        return dict(STATUS_CHOICES).get(self.status)
    


class Topics(models.Model):
    STATUS_CHOICES = (
        ('active', 'Действует'),
        ('removed', 'Удалена'),
    )
    
    topic_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    photo_url = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='active')  # Используйте choices


    class Meta:
        db_table = 'topics'