import imp
from django.contrib import admin
from .models import Profile, Task, Team, Team_Request

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Team_Request)
