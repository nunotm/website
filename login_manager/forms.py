from django.forms import ModelForm
from .models import GymClass

class GymClassForm(ModelForm):
    class Meta:
        model = GymClass
        fields = ['name', 'club']
