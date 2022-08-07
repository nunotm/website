from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Position(models.Model):
    position = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)
    start = models.DateField(null=True)
    current = models.BooleanField(default=False)
    end = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    achievements = models.TextField(blank=True)

    def __str__(self):
        return self.entity

class Education(models.Model):
    course = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    start = models.DateField(blank=True, null=True)
    end_or_estimated = models.DateField(blank=True, null=True)
    average = models.FloatField(blank = True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.course

class Course(models.Model):
    course = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)
    subjects = models.CharField(max_length=200,blank=True)
    notes = models.TextField(blank=True)
    certificate = models.FileField(blank=True)
    certificate_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.course