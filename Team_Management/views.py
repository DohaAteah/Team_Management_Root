import email
from email import message
import imp
from tkinter.messagebox import NO
from unicodedata import name
from urllib import request
from django.conf import settings
from django.shortcuts import redirect, render
from .models import Task
from django.utils import timezone
from django.views.generic import View , TemplateView
from .models import Task
from django.http import JsonResponse
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




class HomeView(TemplateView):
  def Tasks_List(request):
   all_Tasks = Task.objects.filter(created_Date__lte = timezone.now()).order_by('created_Date')
   return render(request , 'Home/Tasks_List.html' , {'all_Tasks': all_Tasks})

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

    if User.objects.filter(email=email):
      messages.error(request,"Email is already exist!")
      return redirect('signup')

    if len(uname)>10:
      messages.error(request,"Username must be under 10 characters!")
      return redirect('signup')

    if pass1 != pass2:
      messages.error(request, "passwoed didn't match!")
      return redirect('signup')

    if not uname.isalnum():
       messages.error(request, "Username must be Alpha-Numeric!")
       return redirect('signup')

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
        render(request, "Header.html",{'fname': fname})
        return  redirect('Home')
        

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
    login(request,my_user)
    return redirect('Home')
  else:
    return redirect(request, "activationFailed.html")
  

 