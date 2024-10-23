from django.db import models
from django.contrib.auth.models import User

from app.stats import STATUS_CHOICES


class ShowTopic(models.Model):
    mm_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey('Topics', models.DO_NOTHING, db_column='topic', blank=True, null=True)
    showw = models.ForeignKey('Shows', models.DO_NOTHING, db_column='showw', blank=True, null=True)
    is_main = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'show_topic'
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        constraints = [
            models.UniqueConstraint(fields=['topic', 'showw'], name='unique_topic_showw')
        ]
 

class Shows(models.Model):
    show_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(User, models.DO_NOTHING, db_column='creator')
    moderator = models.ForeignKey(User, models.DO_NOTHING, db_column='moderator', related_name='shows_moderator_set', blank=True, null=True)
    show_date = models.DateField(blank=True, null=True)
    show_time = models.TimeField(blank=True, null=True)
    show_name = models.CharField(max_length=100, blank=True, null=True)
    show_place = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    class Meta:
        db_table = 'shows'
        verbose_name = "Выставка"
        verbose_name_plural = "Выставки"

    def get_topics(self):
        res = []

        for item in ShowTopic.objects.filter(showw=self):
            tmp = item.topic
            res.append(tmp)

        return res

    def get_status(self):
        return dict(STATUS_CHOICES).get(self.status) 


class Topics(models.Model):
    STATUS_CHOICES = (
        ('1', 'Действует'),
        ('0', 'Удалена'),
    )
    
    topic_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    # photo_url = models.CharField(max_length=100, blank=True, null=True)
    photo_url = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='1')  # Используйте choices

    class Meta:
        db_table = 'topics'
        verbose_name_plural = "Темы"
