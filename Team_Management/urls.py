from . import views
from django.urls import path
from Team_Management.views import TaskJson
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.toHome, name="Home"),
    path('Tasks_Json/', TaskJson.as_view(), name="TasksJsonView"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img\Logo.png'))),
    path('signup', views.signup, name="signup"),
    path('login', views.log_in, name="login"),
    path('signout', views.signout, name="signout"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('createTeam', views.create_team, name="createTeam"),
    path('joinTeam', views.join_team, name="joinTeam"),
    path('toCreateTeam', views.toCreateTeam, name="toCreateTeam"),
    path('toJoinTeam', views.toJoinTeam, name="toJoinTeam"),
    path('toViewTeam', views.toViewTeam, name="toViewTeam"),
    path('toTeam', views.toTeam, name="toTeam"),
    path('toAddMembers', views.toAddMembers, name="toAddMembers"),
    path('addMembers', views.addMembers, name="addMembers"),
    path('addTask/<pid>', views.addTask, name="addTask"),
    path('addProject', views.addProject, name="addProject"),
    path('toViewProject/<pid>', views.toViewProject, name="toViewProject"),
    path('taskDelete/<tid>', views.taskDelete, name="taskDelete"),
    path('memberRemove/<tm>/<mem>', views.memberRemove, name="memberRemove"),
    path('teamRemove/<tm>', views.teamRemove, name="teamRemove"),
    path('leaveTeam/<tm>/<mem>', views.leaveTeam, name="leaveTeam"),
    path('JoinTeam/<tm>/<mem>/<id>', views.JoinTeam, name="JoinTeam"),
    path('RequestReject/<id>', views.RequestReject, name="RequestReject"),
    path('toViewTeam_Req', views.toViewTeam_Req, name="toViewTeam_Req"),
    path('saveTaskChanges/<tid>/<pValue>/<pid>', views.saveTaskChanges, name="saveTaskChanges"),
    path('finishTask/<tid>/<pValue>/<pid>', views.finishTask, name="finishTask"),
    path('projectDelete/<pid>', views.projectDelete, name="projectDelete"),
    path('changePhoto', views.changePhoto, name="changePhoto"),
    path('toViewNotifications', views.toViewNotifications, name="toViewNotifications"),
    path('addMessage', views.addMessage, name="addMessage"),
    path('getMessages/<tm>', views.getMessages, name="getMessages"),
    path('getNoty', views.getNoty, name="getNoty"),
    path('removeNoty/<id>', views.removeNoty, name="removeNoty"),
    path('taskSearch', views.taskSearch, name="taskSearch"),

    
]
