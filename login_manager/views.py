from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import GymClassForm
from .models import GymClass
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'login_manager/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'login_manager/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('login_manager:home')
            except IntegrityError:
                return render(request, 'login_manager/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose a new username'})
        else:
            return render(request, 'login_manager/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

def login_user(request):
    if request.method == 'GET':
        return render(request, 'login_manager/login_user.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login_manager/login_user.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('gym_classes:agresso')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login_manager:login_user')
    else:
        logout(request)
        return redirect('login_manager:login_user')


@login_required
def createlogin_manager(request):
    if request.method == 'GET':
        return render(request, 'login_manager/createlogin_manager.html', {'form':GymClassForm()})
    else:
        try:
            form = GymClassForm(request.POST)
            newlogin_manager = form.save(commit=False)
            newlogin_manager.user = request.user
            newlogin_manager.save()
            return redirect('currentlogin_managers')
        except ValueError:
            return render(request, 'login_manager/createlogin_manager.html', {'form':GymClassForm(), 'error':'Bad data passed in. Try again.'})

@login_required
def currentlogin_managers(request):
    login_managers = login_manager.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'login_manager/currentlogin_managers.html', {'login_managers':login_managers})

@login_required
def completedlogin_managers(request):
    login_managers = login_manager.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'login_manager/completedlogin_managers.html', {'login_managers':login_managers})

@login_required
def viewlogin_manager(request, login_manager_pk):
    login_manager = get_object_or_404(login_manager, pk=login_manager_pk, user=request.user)
    if request.method == 'GET':
        form = GymClassForm(instance=login_manager)
        return render(request, 'login_manager/viewlogin_manager.html', {'login_manager':login_manager, 'form':form})
    else:
        try:
            form = GymClassForm(request.POST, instance=login_manager)
            form.save()
            return redirect('currentlogin_managers')
        except ValueError:
            return render(request, 'login_manager/viewlogin_manager.html', {'login_manager':login_manager, 'form':form, 'error':'Bad info'})

@login_required
def completelogin_manager(request, login_manager_pk):
    login_manager = get_object_or_404(login_manager, pk=login_manager_pk, user=request.user)
    if request.method == 'POST':
        login_manager.datecompleted = timezone.now()
        login_manager.save()
        return redirect('currentlogin_managers')

@login_required
def deletelogin_manager(request, login_manager_pk):
    login_manager = get_object_or_404(login_manager, pk=login_manager_pk, user=request.user)
    if request.method == 'POST':
        login_manager.delete()
        return redirect('currentlogin_managers')
