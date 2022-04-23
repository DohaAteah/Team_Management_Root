from django.shortcuts import render


def Tasks_List(request):
    return render(request , 'Home/Tasks_List.html' , {})