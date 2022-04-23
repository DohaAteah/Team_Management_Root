from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Tasks_List, name="Tasks"),
    path('', include('Team_Management.urls')),
]
