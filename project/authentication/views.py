from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.urls import reverse
from django.contrib import auth
from django.shortcuts import redirect
# Create your views here.

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'email is invalid'},status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'email is in use'},status=409)
        return JsonResponse({'email_valid': True})
    
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only conatin alphanumeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'username taken, choose another one'},status=409)
        return JsonResponse({'username_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']

        context = {
            'fieldValues':request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'password too short')
                    return render(request, 'authentication/register.html', context)                
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.save()
                messages.success(request, 'Account created')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username=request.POST['username']
        password=request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if username and password:
            user = auth.authenticate(username=username, password=password) 

            if user:
                auth.login(request, user)
                messages.success(request, 'welcome, '+user.username) 
                return redirect('expenses')

            messages.error(request, 'wrong username or password ?')       
            return render(request, 'authentication/login.html', context)
        messages.error(request, 'please enter both fields ')       
        return render(request, 'authentication/login.html', context)
    
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'you have been logged out')
        return redirect('login')