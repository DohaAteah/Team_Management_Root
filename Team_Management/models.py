from datetime import date
from pydoc import describe
from turtle import title
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='author' , on_delete= models.CASCADE)
    forUser = models.ForeignKey(User, related_name='TaskUser', on_delete= models.CASCADE)
    description = models.TextField()    
    created_Date = models.DateField(default=date.today())
    deadLine = models.IntegerField(default=1)
    is_Done = models.BooleanField(default=False)
    dyas_Left = models.IntegerField(default=0)


    def __str__(self):
        return self.title


class Team(models.Model):
    title = models.CharField(max_length=100)
    leader = models.ForeignKey(User, related_name='leader' , on_delete= models.CASCADE)
    members = models.ManyToManyField(User, related_name='members')
    description = models.TextField()
    created_Date = models.DateField(default=date.today())

    def __str__(self):
        return self.title
