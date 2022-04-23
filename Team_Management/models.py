from pydoc import describe
from turtle import title
from django.db import models
from django.conf import settings
from django.utils import timezone

class Task(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete= models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_Date = models.DateTimeField(default=timezone.now)
    publish_Date = models.DateTimeField(blank=True, null=True)
    deadLine = models.IntegerField(default=0)
    is_Done = models.BooleanField(default=False)

    def publish(self):
        self.publish_Date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    

