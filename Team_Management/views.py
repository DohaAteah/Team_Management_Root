from datetime import date
import profile
from Team_Management.form import ProfileForm, TeamForm,TaskForm
from tkinter.messagebox import NO
from turtle import title
from unicodedata import name
from django.conf import settings
from django.shortcuts import redirect, render
from Team_Management.models import Task, Team,Profile, Team_Request
from django.utils import timezone
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



def toHome(request):
    if request.user.username == "admin":
          logout(request)
    if request.user.is_authenticated:
     profile = Profile.objects.get(owner = request.user)
     tasksNum = Task.objects.filter(forUser = profile).count()
     notyCount = Team_Request.objects.filter(userToJoin = profile).count()
     new_Team = Team.objects.filter(leader=profile)
     if new_Team.exists():
      print(new_Team)
     else:
      Team1 = Team.objects.all()
      for team_ins in Team1: 
       for member in team_ins.members.all():
        if request.user == member:
           new_Team = Team.objects.filter(title = team_ins.title)
      myProfile = Profile.objects.get(owner = request.user)
      myProfile.doneTasksNum = tasksNum
      return render(request , 'Home/index.html',{'myUser':request.user,
      'myProfile':myProfile,
      'new_Team':new_Team,
      'notyCount':notyCount
      })
    return render(request , 'Home/index.html',{'myUser':request.user})



class TaskJson(View):
    def get(self , *args  , **kwargs):
      tasks = list(Task.objects.values())
      return JsonResponse({'data' : tasks}, safe=False)


def signup(request):
  if request.method == "POST":
    uname = request.POST['uname']
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    role = request.POST['role']
    pass1 = request.POST['pswd1']
    pass2 = request.POST['pswd2']

    if User.objects.filter(username=uname):
      messages.error(request,"Username is already exist!")
      return redirect('signup')

    elif User.objects.filter(email=email):
      messages.error(request,"Email is already exist!")
      return redirect('signup')

    elif len(uname)>10:
      messages.error(request,"Username must be under 10 characters!")
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
        fname = user.first_name
        return redirect('Home')
        

      else:
          messages.error(request, "Incorrect information!")
          return redirect('login')
      
   return render(request, "auth/login.html")      
 
def toLogIn(request):
  return toHome(request)
    

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
    login(request,my_user)
    return redirect('Home')
  else:
    return redirect(request, "activationFailed.html")

def toCreateTeam(request):
       return render(request, "Team/Create_Team.html",{'myUser':request.user}) 

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


def toTeam(request):
   if request.user.is_authenticated:
     profile = Profile.objects.get(owner = request.user)
     team = Team.objects.filter(leader=profile)
     if team.exists():
        return redirect('toViewTeam')  
     else:
         Team1 = Team.objects.all()
         for team_ins in Team1: 
           for member in team_ins.members.all():
             if profile == member:
               return redirect('toViewTeam')  
          
         return toCreateTeam(request)




def toViewTeam(request):
  if request.user.is_authenticated:
    myProfile = Profile.objects.get(owner = request.user)
    new_Team = Team.objects.filter(leader=myProfile)
    if new_Team.exists():
      print(new_Team)
    else:
       our_Team = Team.objects.all()
       for team_ins in our_Team: 
         for member in team_ins.members.all():
           if myProfile == member:
            new_Team = Team.objects.filter(title = team_ins.title)
            break

    for team in new_Team:
     ldr = team.leader
    all_Tasks = Task.objects.filter(author = ldr).order_by('created_Date')
    my_Tasks = Task.objects.filter(forUser = myProfile,author = ldr)
    if all_Tasks.exists():
       for task in all_Tasks:
        task.dyas_Left = task.deadLine - (date.today() - task.created_Date).days
    if my_Tasks.exists():
       for myTask in my_Tasks:
        myTask.dyas_Left = myTask.deadLine - (date.today() - myTask.created_Date).days
    return render(request, "Team/TeamPage.html", {'new_Team': new_Team,'all_Tasks': all_Tasks, 'my_Tasks': my_Tasks,'myUser': request.user,'myProfile':myProfile}) 
  else:
      return render(request,"HomePage.html") 

def toAddMembers(request):
  profile = Profile.objects.get(owner = request.user)
  new_Team = Team.objects.filter(leader=profile)
  if new_Team.exists():
     print(new_Team)
  else:
    Team1 = Team.objects.all()
    for team_ins in Team1: 
      for member in team_ins.members.all():
       if request.user == member:
          new_Team = Team.objects.filter(title = team_ins.title)
  myProfile = Profile.objects.filter(owner = request.user)
  return render(request, "Team/Add_Members.html",{'myUser':request.user,'myProfile':myProfile,'new_Team':new_Team}) 

def addMembers(request):
  if request.method == "POST":
    newUser = request.POST['addUser']
    prof = Profile.objects.get(owner = request.user)
    ourTeam = Team.objects.get(leader = prof)
    if newUser=="admin":
        messages.error(request, "Can't add admin!")
        return redirect('toAddMembers')
    
    if User.objects.filter(username = newUser).exists():
        profile = Profile.objects.get(owner = request.user)
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


def addTask(request):
  if request.method == "POST": 
    form = TaskForm(request.POST)
    new_Task = form.save(commit=False)
    profile = Profile.objects.get(owner = request.user)
    new_Task.author = profile
    new_Task.title = request.POST['title']
    uname = request.POST['forUser']
    user = User.objects.get(username = uname)
    userProfile = Profile.objects.get(owner = user)
    new_Task.forUser = userProfile
    new_Task.description = request.POST['description']
    new_Task.deadLine = request.POST['deadLine']
    team = Team.objects.get(leader = profile)
    new_Task.team = team
    new_Task.save()
    return redirect('toViewTeam')  

def taskDetails(request, tid):
    theTask = Task.objects.get(id=tid)
    myProfile = Profile.objects.get(owner = request.user)
    new_Team = Team.objects.filter(leader=myProfile)
    if new_Team.exists():
      print(new_Team)
    else:
       our_Team = Team.objects.all()
       for team_ins in our_Team: 
         for member in team_ins.members.all():
           if request.user == member:
            new_Team = Team.objects.filter(title = team_ins.title)
            break

    return render(request,"Team/Task_Details.html",{'theTask':theTask,'new_Team':new_Team,'myProfile':myProfile,'myUser':request.user})

def taskDelete(request, tid):
  Task.objects.filter(id=tid).delete()
  return redirect('toViewTeam')  

def memberRemove(request,tm, mem):
  team = Team.objects.get(title = tm)
  user = Profile.objects.get(title = mem)
  team.members.remove(user)
  return redirect('toViewTeam')  

def teamRemove(request, tm):
    Team.objects.get(title = tm).delete()
    return redirect('Home')

def leaveTeam(request,tm, mem):
  team = Team.objects.get(title = tm)
  user = Profile.objects.get(title = mem)
  team.members.remove(user)
  return redirect('Home')

def toViewTeam_Req(request):
  prof = Profile.objects.get(owner = request.user)
  team_req_noty = Team_Request.objects.filter(userToJoin = prof)
  return render(request,"Notifications/Team_Requests.html",{'team_req_noty':team_req_noty,'myProfile':prof,'myUser':request.user})


def JoinTeam(request,tm, mem, id):
  team = Team.objects.get(title = tm)
  user = Profile.objects.get(title = mem)
  team.members.add(user)
  Team_Request.objects.get(id = id).delete()
  return redirect('toViewTeam')

def RequestReject(request, id):
    Team_Request.objects.get(id = id).delete()
    return redirect('toViewTeam_Req')
  







 