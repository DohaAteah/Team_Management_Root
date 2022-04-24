from datetime import date
from pydoc import describe
from turtle import title
from django.db import models
from django.conf import settings
from django.utils import timezone

class Task(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete= models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_Date = models.DateField(default=date.today())
    deadLine = models.IntegerField(default=0)
    is_Done = models.BooleanField(default=False)
    dyas_Left = models.IntegerField(default=0)

    def publish(self):
        self.dyas_Left = self.deadLine - (date.today() - self.created_Date).days
        self.save()

    def __str__(self):
        return str(self.title)


