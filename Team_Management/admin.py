import imp
from django.contrib import admin
from .models import Profile, Task, Team

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Profile)
