from datetime import date
from Team_Management.form import ProjectForm, TeamForm,TaskForm
from unicodedata import name
from django.conf import settings
from django.shortcuts import redirect, render
from Team_Management.models import  Message, Notification, Project, Task, Task_suggest, Team,Profile, Team_Request
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate ,login,logout
from myApp import settings
from django.core.mail import send_mail,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token
from django.contrib.auth.context_processors import auth


def getProfileRate(prof):
      tasksNum = Task.objects.filter(forUser = prof,is_Done = True).count()
      rate = 0
      if (Task.objects.filter(forUser = prof).count() > 0):
        rate = tasksNum/Task.objects.filter(forUser = prof).count()
      rate *= 100
      rate = "{:.2f}".format(rate)
      rate = float(rate)
      prof.doneTasksNum = tasksNum
      prof.rated = rate
      prof.save()
      pass

def getProfileTeam(prof):
  new_Team = None
  if Team.objects.filter(leader=prof).exists():
    new_Team = Team.objects.get(leader=prof)
  else:
    Team1 = Team.objects.all()
    for team_ins in Team1: 
      for member in team_ins.members.all():
        if prof== member:
         new_Team = Team.objects.get(title = team_ins.title) 
  return new_Team


    
def toHome(request):
    if request.user.username == "admin":
          logout(request)
    if request.user.is_authenticated:
      profile = Profile.objects.get(owner = request.user)
      new_Team = None
      new_Team = getProfileTeam(profile)
      getProfileRate(profile)
      return render(request , 'index.html',{
      'myProfile':profile,
      'new_Team':new_Team
      })
      
    return render(request , 'index.html')

def getNoty(request):
  if request.user.is_authenticated:
     notyCount2 = 0
     profile = Profile.objects.get(owner = request.user)
     notyCount = Team_Request.objects.filter(userToJoin = profile, isUser = False).count()
     allCount = notyCount
     new_Team = getProfileTeam(profile)
     if new_Team is not None:
      notyCount2 = Team_Request.objects.filter(teamToJoin = new_Team, isUser = True).count()
      allCount += notyCount2
     teamNoty = allCount
     notysCount = Notification.objects.filter(forUser = profile).count()
     allCount += notysCount
     suggNoty = Task_suggest.objects.filter(forUser = profile).count()
     allCount += suggNoty
     return JsonResponse({'allCount': allCount,'notysCount':notysCount,'teamNoty':teamNoty,'suggNoty':suggNoty})


  


class TaskJson(View):
    def get(self , *args  , **kwargs):
      tasks = list(Task.objects.values())
      return JsonResponse({'data' : tasks}, safe=False)

def changePhoto(request):
  if request.user.is_authenticated:
    if request.method == "POST":
      img = request.FILES.get('img')
      role = request.POST['role']
      myProfile = Profile.objects.get(owner = request.user)
      myProfile.photo = img
      if role != "" and role is not None:
        myProfile.role = role
      myProfile.save()
  return redirect('Home')


def addMessage(request):
  if request.user.is_authenticated:
    value = request.POST['msg']
    tm = request.POST['tm']
    prof = Profile.objects.get(owner = request.user)
    team = getProfileTeam(prof)
    if team is not None:
      new_msg = Message(title = value, userName = request.user.username, photo = prof.photo)
      new_msg.save()
      team = Team.objects.get(title = tm)
      team.messages.add(new_msg)
      team.save()
    else:
      return redirect('Home')
  return HttpResponse('Success!')


def suggestion(request, tid):
  if request.user.is_authenticated:
      newUser = request.POST['sugg']
      myProfile = Profile.objects.get(owner = request.user)
      user1 = None
      if User.objects.filter(username = newUser).exists():
        user1 = User.objects.get(username = newUser)
        prof = Profile.objects.get(owner = user1)
        task = None
        if Task.objects.filter(id = tid).exists():
          task = Task.objects.get(id = tid)
          if Task_suggest.objects.filter(task = task, fromUser = myProfile, forUser = prof).exists():
            messages.info(request, 'Suggestion request already sent!')
            return redirect('toViewProject', task.project.id)
          else:
            suggReq = Task_suggest(task = task, fromUser = myProfile, forUser = prof)
            suggReq.save()
            messages.info(request, 'Suggestion request sent successfully!')
            return redirect('toViewProject', task.project.id)
  return redirect('Home')



def getMessages(request, tm):
  if request.user.is_authenticated:
    team = Team.objects.get(title = tm)
    Msg = team.messages.all()
    return JsonResponse({"Msg":list(Msg.values())})

def signup(request):
  if request.method == "POST":
    uname = request.POST['uname']
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    role = request.POST['role']
    pass1 = request.POST['pswd1']
    pass2 = request.POST['pswd2']
    img = request.FILES.get('img')

    if User.objects.filter(username=uname):
      messages.error(request,"Username is already exist!")
      return redirect('signup')

    elif User.objects.filter(email=email):
      messages.error(request,"Email is already exist!")
      return redirect('signup')

    elif len(uname)>10:
      messages.error(request,"Username must be under 10 characters!")
      return redirect('signup')

    elif len(pass1)<8:
      messages.error(request,"Password must be at least 8 characters!")
      return redirect('signup')

    elif pass1 != pass2:
      messages.error(request, "passwoed didn't match!")
      return redirect('signup')

    elif not uname.isalnum():
       messages.error(request, "Username must be Alpha-Numeric!")
       return redirect('signup')
    else:
       my_user = User.objects.create_user(uname,email,pass1)
       my_user.first_name = fname
       my_user.last_name = lname
       my_user.is_active = False
       my_user.save()

       new_profile = Profile(title = uname,owner = my_user,role = role)
       print(img)
       if(img):
         new_profile.photo = img 
       new_profile.save()


       messages.success(request,"We have send you a confirmation email, please check your email.")
    # email 
       subject = "Welcome to CONTROL"
       message = "Hello " + my_user.first_name + " \n" + "Thank you for visiting our website.\n We have also send you a confirmation email, please confirm your email address to activate your account.\n\n UDTeam "
       from_email = settings.EMAIL_HOST_USER
       to_list = [my_user.email]
       send_mail(subject, message, from_email, to_list, fail_silently =True)


    # send confirmation email 
       current_site = get_current_site(request)
       email_subject = "Confirm your email @ CONTROL"
       email_message = render_to_string('email_confirmation.html',{
         'name': my_user.first_name,
          'domain': current_site.domain,
          'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
         'token': generate_token.make_token(my_user)
        })
       email = EmailMessage(
         email_subject,
         email_message,
         settings.EMAIL_HOST_USER,
         [my_user.email]
       )
       email.fail_silently = True
       email.send()

       return redirect('login')
    

  return render(request, "auth/signup.html")      




def log_in(request):
   if request.method == "POST":
      username = request.POST['uname']
      pass1 = request.POST['pswd1']

      user = authenticate(username=username, password=pass1)
      if user is not None:
        login(request, user)
        return redirect('Home')
        
      else:
          messages.error(request, "Incorrect information!")
          return redirect('login')
      
   return render(request, "auth/login.html")      

    

def signout(request):
    logout(request)
    return redirect('Home')

def activate(request, uidb64, token):
  try:
    uid = force_text(urlsafe_base64_decode(uidb64))
    my_user = User.objects.get(pk=uid)
  except(TypeError,ValueError,OverflowError,User.DoesNotExist):
    my_user = None

  if my_user is not None and generate_token.check_token(my_user,token):
    my_user.is_active = True
    my_user.save()
    return render(request,'auth/activationSucess.html')
  else:
    return render(request, "auth/activationFailed.html")

def toCreateTeam(request):
  if request.user.is_authenticated:
    profile = Profile.objects.get(owner = request.user) 
    getProfileRate(profile)
    new_Team = None
    new_Team = getProfileTeam(profile)
    return render(request, "Team/Create_Team.html",{'new_Team': new_Team,'myProfile':profile}) 

def toJoinTeam(request):
  if request.user.is_authenticated:
    profile = Profile.objects.get(owner = request.user) 
    getProfileRate(profile)
    new_Team = None
    new_Team = getProfileTeam(profile)
    return render(request, "Team/Join_Team.html",{'new_Team': new_Team,'myProfile':profile}) 

def create_team(request):
  if request.method == "POST":
    teamTitle = request.POST['title']
    if Team.objects.filter(title = teamTitle).exists():
      messages.error(request, "Team name already exists!")
      return redirect('toCreateTeam')
    else:
      form = TeamForm(request.POST)
      new_Team = form.save(commit=False)
      new_Team.title = request.POST['title']
      new_Team.description = request.POST['description']
      profile = Profile.objects.get(owner = request.user)
      new_Team.leader = profile

      new_Team.save()

      new_Team.members.add(profile)
      return redirect('toViewTeam')  
              

  else:
      print(request,"error")

def join_team(request):
  if request.method == "POST":
    teamTitle = request.POST['title']
    if Team.objects.filter(title = teamTitle).exists():
      team = Team.objects.get(title = teamTitle)
      userProf = Profile.objects.get(owner = request.user)
      if Team_Request.objects.filter(userToJoin = userProf, teamToJoin = team).exists():
          messages.error(request, "Request Already sent!")
          return redirect('toJoinTeam')
      else:
          joinRequest = Team_Request(userToJoin = userProf, teamToJoin = team, isUser = True)
          joinRequest.save()
          messages.error(request, "Request successfully sent!")
          return redirect('toJoinTeam') 
    else:
      messages.error(request, "Team not found!")
      return redirect('toJoinTeam')
 
              

  else:
      print(request,"error")





def toTeam(request):
   if request.user.is_authenticated:
     profile = Profile.objects.get(owner = request.user)
     getProfileRate(profile)
     team = Team.objects.filter(leader=profile)
     if team.exists():
        return redirect('toViewTeam')  
     else:
         Team1 = Team.objects.all()
         for team_ins in Team1: 
           for member in team_ins.members.all():
             if profile == member:
               return redirect('toViewTeam')  
          
         return render(request,'Team/review.html',{'new_Team': team,'myProfile':profile})




def toViewTeam(request):
  if request.user.is_authenticated:
    if Profile.objects.filter(owner = request.user).exists():
      myProfile = Profile.objects.get(owner = request.user)
      getProfileRate(myProfile)
      new_Team = getProfileTeam(myProfile)
      if new_Team is not None:
        all_Projects = Project.objects.filter(team = new_Team).order_by('started_Date')
        if all_Projects.exists():
          for project in all_Projects:
            values = 0
            value = 0
            project.dyas_Left = project.deadLine - (date.today() - project.started_Date).days
            for tasks in Task.objects.filter(project = project):
              value = tasks.progress[:-1]
              value = int('0' + value)
              values += value
            if Task.objects.filter(project = project).count():
              values = values/Task.objects.filter(project = project).count()
            values = str(values)
            values = values+"%"
            project.progress = values
            project.save()
        
        return render(request, "Team/TeamPage.html", {'new_Team': new_Team,'all_Projects': all_Projects,'myProfile':myProfile}) 

  return redirect('Home')

def toViewProject(request, pid):
  if request.user.is_authenticated:
    if Project.objects.filter(id = pid).exists():
      project = Project.objects.get(id = pid)
      values = 0
      value = 0
      for tasks in Task.objects.filter(project = project):
            value = tasks.progress[:-1]
            value = int(value)
            values += value
      if Task.objects.filter(project = project).count():
              values = values/Task.objects.filter(project = project).count()
      values = str(values)
      values = values+"%"
      project.progress = values
      project.save()
      if Profile.objects.filter(owner = request.user):
        myProfile = Profile.objects.get(owner = request.user)
        getProfileRate(myProfile)
        new_Team = project.team
        for member in new_Team.members.all():
              if member == myProfile:
                ldr = new_Team.leader
                all_Tasks = Task.objects.filter(author = ldr, project= project).order_by('created_Date')
                my_Tasks = Task.objects.filter(forUser = myProfile, project= project).order_by('created_Date')
                if all_Tasks.exists():
                  for task in all_Tasks:
                    if task.is_Done == False:
                      task.dyas_Left = task.deadLine - (date.today() - task.created_Date).days
                      task.save()
                if my_Tasks.exists():
                  for task in my_Tasks:
                    if task.is_Done == False:
                      task.dyas_Left = task.deadLine - (date.today() - task.created_Date).days
                      task.save()
                return render(request, "Team/ProjectPage.html", {'new_Team': new_Team,'all_Tasks': all_Tasks,'my_Tasks': my_Tasks,'myProfile':myProfile,'project':project})  
  return redirect('Home')

def toAddMembers(request):
  profile = Profile.objects.get(owner = request.user)
  getProfileRate(profile)
  new_Team = Team.objects.filter(leader=profile)
  if new_Team.exists():
     print(new_Team)
  else:
    Team1 = Team.objects.all()
    for team_ins in Team1: 
      for member in team_ins.members.all():
       if profile== member:
          new_Team = Team.objects.filter(title = team_ins.title)
  myProfile = Profile.objects.filter(owner = request.user)
  return render(request, "Team/Add_Members.html",{'myProfile':myProfile,'new_Team':new_Team}) 

def addMembers(request):
  if request.method == "POST":
    newUser = request.POST['addUser']
    prof = Profile.objects.get(owner = request.user)
    ourTeam = Team.objects.get(leader = prof)
    if newUser=="admin":
        messages.error(request, "Can't add admin!")
        return redirect('toAddMembers')
    
    if User.objects.filter(username = newUser).exists():  
        the_Team = Team.objects.filter()
        user = User.objects.get(username = newUser)
        userProf = Profile.objects.get(owner = user)

        
        for team in the_Team:
          for member in team.members.all():
            if userProf == member:
              messages.error(request, "User already in team!")
              return redirect('toAddMembers')
        if Team_Request.objects.filter(userToJoin = userProf, teamToJoin = ourTeam).exists():
          messages.error(request, "Request Already sent!")
          return redirect('toAddMembers')
        else:
          joinRequest = Team_Request(userToJoin = userProf, teamToJoin = ourTeam)
          joinRequest.save()
          #team.members.add(userProf)
          messages.error(request, "Request successfully sent!")
          return redirect('toAddMembers')
    else:
        messages.error(request, "User not found!")
        return redirect('toAddMembers')


def addTask(request, pid):
  if request.method == "POST":
    profile = Profile.objects.get(owner = request.user)
    project = Project.objects.get(id = pid)
    if project.team.leader == profile:
      form = TaskForm(request.POST)
      new_Task = form.save(commit=False)
      new_Task.author = profile
      new_Task.project = project
      new_Task.title = request.POST['title']
      uname = request.POST['forUser']
      user = User.objects.get(username = uname)
      userProfile = Profile.objects.get(owner = user)
      new_Task.forUser = userProfile
      new_Task.description = request.POST['description']
      new_Task.deadLine = request.POST['deadLine']
      team = Team.objects.get(leader = profile)
      new_Task.team = team
      depend = request.POST['depend']
      if depend is not None and depend != "":
        dependOnTask = Task.objects.get(id = depend)
        if dependOnTask is not None:
          new_Task.dependsOn = dependOnTask
      new_Task.save()
      new_noty = Notification(title = "There is a new task for you. |  Project name: "+new_Task.project.title+" | Task number: "+str(new_Task.id) ,forUser = new_Task.forUser)
      new_noty.save()
      print(new_noty.title)
      return redirect('toViewProject',pid) 
    else:
      return redirect('Home') 

def addProject(request):
  if request.method == "POST": 
    form = ProjectForm(request.POST)
    new_Project = form.save(commit=False)
    profile = Profile.objects.get(owner = request.user)
    team = Team.objects.get(leader = profile)
    new_Project.team = team
    new_Project.title = request.POST['title']
    new_Project.description = request.POST['description']
    new_Project.deadLine = request.POST['deadLine']
    
    new_Project.save()
    return redirect('toViewTeam')  


def taskDelete(request, tid):
  if request.user.is_authenticated:
    profile = Profile.objects.get(owner = request.user)
    if Task.objects.filter(id=tid, author = profile).exists():
      pid = Task.objects.get(id=tid, author = profile).team.id
      Task.objects.filter(id=tid, author = profile).delete()
      return redirect('toViewProject',pid)
    return redirect('Home')

def projectDelete(request, pid):
    if request.user.is_authenticated:
      profile = Profile.objects.get(owner = request.user)
      if Project.objects.filter(id=pid).exists():
        team = Project.objects.get(id=pid).team
        profTeam = getProfileTeam(profile)
        if team == profTeam:
          Project.objects.get(id=pid).delete()
      return redirect('toViewTeam')
    else:
     return redirect('Home') 

def memberRemove(request,tm, mem):
  if request.user.is_authenticated:
    prof = Profile.objects.get(owner = request.user)
    profTeam = getProfileTeam(prof)
    team = Team.objects.get(title = tm)
    if profTeam == team:
      if profTeam.leader == prof:
        user = Profile.objects.get(title = mem)
        team.members.remove(user)
    return redirect('toViewTeam') 

def teamRemove(request, tm):
  if request.user.is_authenticated:
    prof = Profile.objects.get(owner = request.user)
    profTeam = getProfileTeam(prof)
    team = Team.objects.get(title = tm)
    if profTeam == team:
      if profTeam.leader == prof:
        team.delete()
  return redirect('Home')

def leaveTeam(request,tm, mem):
  if request.user.is_authenticated:
    profile = Profile.objects.get(owner = request.user)
    user2 = Profile.objects.get(title = mem)
    team = Team.objects.get(title = tm)
    if profile == user2:
      for member in team.members.all():
        if member == user2:
          team.members.remove(user2)
          noty = Notification(title = mem+" left the team!", forUser = team.leader)
          noty.save()
  return redirect('Home')

def toViewTeam_Req(request):
  if request.user.is_authenticated:
    prof = Profile.objects.get(owner = request.user)
    team = getProfileTeam(prof)
    team_req_noty = None
    if Team_Request.objects.filter(userToJoin = prof, isUser = False).exists():
      team_req_noty = Team_Request.objects.filter(userToJoin = prof, isUser = False)
    team_req_noty2 = None
    if Team.objects.filter(leader = prof):
      team = Team.objects.get(leader = prof)
      team_req_noty2 = Team_Request.objects.filter(teamToJoin = team, isUser = True)
    return render(request,"Notifications/Team_Requests.html",{'team_req_noty':team_req_noty,'team_req_noty2':team_req_noty2,'myProfile':prof,'new_Team':team})
  else:
    return redirect('Home')

def toViewNotifications(request):
  if request.user.is_authenticated:
    prof = Profile.objects.get(owner = request.user)
    team = getProfileTeam(prof)
    notifications = Notification.objects.filter(forUser = prof)
    return render(request,"Notifications/Notification.html",{'notifications':notifications,'myProfile':prof,'new_Team':team})
  else:
    return redirect('Home')


def toViewSuggestion(request):
  if request.user.is_authenticated:
    prof = Profile.objects.get(owner = request.user)
    team = getProfileTeam(prof)
    suggRequest = Task_suggest.objects.filter(forUser = prof)
    return render(request,"Notifications/Suggest_Requests.html",{'suggRequest':suggRequest,'myProfile':prof,'new_Team':team})
  else:
    return redirect('Home')

def applySuggestion(request, sid):
  if request.user.is_authenticated:
    if Profile.objects.filter(owner = request.user).exists():
      prof = Profile.objects.get(owner = request.user)
      suggReq = Task_suggest.objects.filter(id = sid)
      if suggReq.exists():
        suggRequest = Task_suggest.objects.get(id = sid)
        if suggRequest is not None:
          if prof == suggRequest.forUser:
            task = suggRequest.task
            task.forUser = suggRequest.forUser
            task.save()
            noty = Notification(title = "[ ^_^ ] "+ suggRequest.forUser.owner.username+" accept your suggest to do the task with number: "+str(suggRequest.task.id), forUser = suggRequest.fromUser)
            noty.save()
            suggRequest.delete()
            if Task_suggest.objects.filter(task = suggRequest.task).exists():
              Task_suggest.objects.filter(task = suggRequest.task).delete()
            return redirect('toViewSuggestion')
  return redirect('Home')

def rejectSuggestion(request, sid):
  if request.user.is_authenticated:
    prof = Profile.objects.get(owner = request.user)
    suggReq = Task_suggest.objects.filter(id = sid)
    if suggReq.exists():
      suggRequest = Task_suggest.objects.get(id = sid)
      if prof == suggRequest.forUser:
        noty = Notification(title = "[ x_x ] "+ suggRequest.forUser.owner.username+" reject your suggest to do the task with number: "+str(suggRequest.task.id), forUser = suggRequest.fromUser)
        noty.save()
        suggRequest.delete()
        return redirect('toViewSuggestion')
  return redirect('Home')



def JoinTeam(request,tm, mem, id):
  if request.user.is_authenticated:
    team = Team.objects.get(title = tm)
    user = Profile.objects.get(title = mem)
    team.members.add(user)
    noty = Notification(title = mem+" joined the team!", forUser = team.leader)
    noty2 = Notification(title = "You are now "+team.title+ " member!", forUser = user)
    noty.save()
    noty2.save()
    Team_Request.objects.get(id = id).delete()
    return redirect('toViewTeam_Req')

def RequestReject(request, id):
  if request.user.is_authenticated:
    if Team_Request.objects.filter(id = id).exists():
      teamReq = Team_Request.objects.get(id = id);
      if teamReq.isUser:
        noty = Notification(title = teamReq.teamToJoin.title+" reject your join request!", forUser = teamReq.userToJoin)
      else:
        noty = Notification(title = teamReq.userToJoin.owner.username+" reject your request!", forUser = teamReq.teamToJoin.leader)
      
      teamReq.delete()
      noty.save()
      
    return redirect('toViewTeam_Req')

def removeNoty(request, id):
  if request.user.is_authenticated:
    if Notification.objects.filter(id = id).exists():
     Notification.objects.get(id = id).delete()
  return redirect('toViewNotifications')

def saveTaskChanges(request, tid, pValue,pid):
  if request.user.is_authenticated:
    project = Project.objects.get(id = pid)
    task = Task.objects.get(id = tid)
    task.progress = pValue
    task.save()
    return redirect('toViewProject',project.id)
  else:
    return redirect('Home')

def finishTask(request, pValue,tid ,pid):
  if request.user.is_authenticated:
    project = Project.objects.get(id = pid)
    task = Task.objects.get(id = tid)
    task.progress = pValue
    task.is_Done = True
    task.finishedDate = date.today()
    for task2 in Task.objects.filter(project = project):
      if task2.dependsOn == task:
        task2.dependsOn = None
        task2.created_Date = date.today()
        task2.save()
    task.save()
    noty = Notification(title = task.forUser.owner.username+" finished the task with number: " + str(task.id),forUser = project.team.leader)
    noty.save()
    return redirect('toViewProject',project.id)
  else:
    return redirect('Home')

def taskSearch(request):
  if request.user.is_authenticated:
    newTask = None
    newProf = None
    profTeam = None
    if request.method == "POST":
      prof = Profile.objects.get(owner = request.user)
      new_Team = getProfileTeam(prof)
      if new_Team is not None:   
        searchResault = request.POST['search']
        if User.objects.filter(username = searchResault).exists():
          user = User.objects.get(username = searchResault)
          newProf = Profile.objects.get(owner = user)
          profTeam = getProfileTeam(newProf)
          print(newProf)  
        if searchResault.isnumeric():    
          if Task.objects.filter(id = searchResault).exists():
            newTask = Task.objects.get(id = searchResault)
            newTask.dyas_Left = newTask.deadLine - (date.today() - newTask.created_Date).days
            newTask.save()
            project = newTask.project
            if project.team == new_Team:
              return render(request,'Search.html',{'new_Team':new_Team,'myProfile':prof,'newTask':newTask,'newProf':newProf,'profTeam':profTeam})
 
    return render(request,'Search.html',{'new_Team':new_Team,'myProfile':prof,'newTask':newTask,'newProf':newProf,'profTeam':profTeam})
  else:
    return redirect('login')
