import imp
from unicodedata import name
from django.shortcuts import render
from .models import Task
from django.utils import timezone
from django.views.generic import View , TemplateView
from .models import Task
from django.http import JsonResponse



class HomeView(TemplateView):
  def Tasks_List(request):
   all_Tasks = Task.objects.filter(created_Date__lte = timezone.now()).order_by('created_Date')
   return render(request , 'Home/Tasks_List.html' , {'all_Tasks': all_Tasks})
   # template_name = 'Home/Tasks_List.html'

class TaskJson(View):
    def get(self , *args  , **kwargs):
      tasks = list(Task.objects.values())
      return JsonResponse({'data' : tasks}, safe=False)
 
 