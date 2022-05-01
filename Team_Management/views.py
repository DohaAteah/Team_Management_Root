from datetime import date
from Team_Management.form import TeamForm
from tkinter.messagebox import NO
from turtle import title
from unicodedata import name
from django.conf import settings
from django.shortcuts import redirect, render
from Team_Management.models import Task, Team
from django.utils import timezone
from django.views.generic import View , TemplateView
from .models import Task
from django.http import JsonResponse
from django.contrib.auth.models import User,Group
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
   return render(request , 'Home/index.html')

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
        return toLogIn(request)
        

      else:
          messages.error(request, "Incorrect information!")
          return redirect('login')
      
   return render(request, "auth/login.html")      
 
def toLogIn(request):
  myUser = request.user
  return render(request, "Header.html",{'myUser': myUser})
  return redirect('Home')
    

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
      new_Team.leader = request.user

      new_Team.save()

      #set group name
      g1, created = Group.objects.get_or_create(name=new_Team.title)

      if not created:
        print(request,"error")
      #autopopulate / assign author to new team
      g1.user_set.add(new_Team.leader)

      #debug (hopefully print: Team Name, Key, Creator, Members
      print(new_Team)
      return toViewTeam(request)
              

  else:
      print(request,"error")


def toTeam(request):
   if request.user.is_authenticated:
     team = Team.objects.filter(leader=request.user)
     if team.exists():
       return toViewTeam(request)
     else:
         Team1 = Team.objects.all()
         for team_ins in Team1: 
           for member in team_ins.members.all():
             if request.user == member:
              return toViewTeam(request)
          
         return toCreateTeam(request)


def toCreateTeam(request):
       return render(request, "Team/Create_Team.html") 

def toViewTeam(request):
     new_Team = None
     if request.user.is_authenticated:
      all_Tasks = Task.objects.filter(created_Date__lte = timezone.now()).order_by('created_Date')
      if all_Tasks.exists():
       for task in all_Tasks:
        task.dyas_Left = task.deadLine - (date.today() - task.created_Date).days

      new_Team = Team.objects.filter(leader=request.user)
      if new_Team.exists():
       return render(request, "Team/TeamPage.html", {'new_Team': new_Team,'all_Tasks': all_Tasks}) 
      else:
         Teams = Team.objects.all()
         for team_ins in Teams: 
           for member in team_ins.members.all():
             if request.user == member:
              theTeam = Team.objects.filter(title = team_ins.title)
              return render(request, "Team/TeamPage.html", {'new_Team': theTeam,'all_Tasks': all_Tasks}) 
   
def toAddMembers(request):
      return render(request, "Team/Add_Members.html") 

def addMembers(request):
  if request.method == "POST":
    newUser = request.POST['addUser']
    if User.objects.filter(username = newUser).exists():
        the_Team = Team.objects.filter(leader=request.user)
        user = User.objects.get(username = newUser)
        for team in the_Team:
         team.members.add(user)
         return render(request,"Team/Add_Members.html")
    else:
        messages.error(request, "User not found!")
        return render(request,"Team/Add_Members.html")






 