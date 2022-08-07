from django.shortcuts import render, get_object_or_404
from .models import Position, Course, Education
import datetime


# Create your views here.

def home(request):
    positions = Position.objects.order_by('-start')
    return render(request, 'cv/home.html', {'positions':positions})

def detail(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    achievements = position.achievements.split(";")
    return render(request, 'cv/detail.html',{'position':position, 'achievements':achievements})


def all_courses(request):
    courses = Course.objects.all()
    return render(request, 'cv/all_courses.html', {'courses':courses})


def education(request):
    educations = Education.objects.order_by('-start')
    return render(request, 'cv/education.html', {'educations':educations})


def personal(request):
    return render(request, 'cv/personal.html')


def equality_act(request):
    age=(datetime.datetime.today().date()-datetime.date(1987,1,28)).days/365.25
    return render(request, 'cv/equality.html', {"age":int(age)})
