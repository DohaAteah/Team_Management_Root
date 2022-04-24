from . import views
from django.urls import path
from Team_Management.views import HomeView, TaskJson
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', HomeView.Tasks_List, name="Home"),
    path('Tasks_Json/', TaskJson.as_view(), name="TasksJsonView"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
