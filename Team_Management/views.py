from django.shortcuts import render
from .models import Task
from django.utils import timezone

def Tasks_List(request):
    all_Tasks = Task.objects.filter(publish_Date__lte = timezone.now()).order_by('publish_Date')
    return render(request , 'Home/Tasks_List.html' , {'all_Tasks': all_Tasks})