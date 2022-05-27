from datetime import date, datetime
from email.policy import default
from pydoc import describe
from django.db.models.deletion import CASCADE
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Profile(models.Model):
    title = models.CharField(max_length=100)
    owner = models.OneToOneField(User, related_name='owner' , on_delete= models.CASCADE)
    role = models.CharField(max_length=100,default="None")
    photo = models.ImageField(upload_to='static/cover-images/%y/%m/%d/',default = 'static/cover-images/default/Login.png')
    rated = models.IntegerField(default=0)
    doneTasksNum = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Message(models.Model):
    title = models.CharField(max_length=100000)
    date = models.DateTimeField(default=datetime.now , blank= True)
    userName = models.CharField(max_length=100000)
    photo = models.ImageField(default = 'static/cover-images/default/Login.png')
   

class Team(models.Model):
    title = models.CharField(max_length=100)
    leader = models.ForeignKey(Profile, related_name='leader' , on_delete= models.CASCADE)
    members = models.ManyToManyField(Profile, related_name='members')
    messages = models.ManyToManyField(Message, related_name='messages')
    description = models.TextField()
    created_Date = models.DateField(default=date.today())

    def __str__(self):
        return self.title


class Team_Request(models.Model):
    title = models.CharField(max_length=50,default="Team Request")
    teamToJoin = models.ForeignKey(Team, related_name='Team_to_join', on_delete=models.CASCADE)
    userToJoin = models.ForeignKey(Profile, related_name='User_to_join', on_delete= models.CASCADE)
    isUser = models.BooleanField(default=False)
    created_Date = models.DateField(default=date.today())
    
    def __str__(self):
        return self.title



class Project(models.Model):
    title = models.CharField(max_length=50)
    team = models.ForeignKey(Team, related_name='TeamForProject', on_delete=models.CASCADE)
    progress = models.CharField(max_length=100,default="0%")
    description = models.TextField()    
    is_Done = models.BooleanField(default=False)
    started_Date = models.DateField(default=date.today())
    deadLine = models.IntegerField(default=1)

    def __str__(self):
        return self.title


    
class Task(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Profile, related_name='author' , on_delete= models.CASCADE)
    forUser = models.ForeignKey(Profile, related_name='TaskUser', on_delete= models.CASCADE)
    project = models.ForeignKey(Project, related_name='Project', on_delete=models.CASCADE)
    description = models.TextField()    
    created_Date = models.DateField(default=date.today())
    finishedDate = models.DateField(default=date.today())
    deadLine = models.IntegerField(default=1)
    is_Done = models.BooleanField(default=False)
    dyas_Left = models.IntegerField(default=0)
    progress = models.CharField(max_length=100,default="0%")
    dependsOn = models.ForeignKey('self', related_name='dependTask', on_delete=models.CASCADE, null = True)
    suggestion = models.ForeignKey(Profile, related_name='suggest_to', on_delete=models.CASCADE, null = True)


    def __str__(self):
        return self.title



class Notification(models.Model):
    title = models.CharField(max_length=10000,default="Task Notification")
    created_Date = models.DateField(default=date.today())
    forUser = models.ForeignKey(Profile, related_name='forUserNoty', on_delete= models.CASCADE)

class Task_suggest(models.Model):
    task = models.ForeignKey(Task, related_name='suggested_Task',on_delete=models.CASCADE)
    fromUser = models.ForeignKey(Profile, related_name='suggFromUser', on_delete=models.CASCADE)
    forUser = models.ForeignKey(Profile, related_name='suggForUser', on_delete= models.CASCADE)
    created_Date = models.DateField(default=date.today())
