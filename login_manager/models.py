from django.db import models
from django.contrib.auth.models import User

class GymClass(models.Model):
    club = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    starttime = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=60)
    cover = models.BooleanField(default=False)
    lwp = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " at " + self.club