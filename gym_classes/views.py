from django.shortcuts import render
from . import classes_jupyter

#def call_import_data():
#   con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv = import_data("classes.db")
#   return con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv

# Create your views here.
def dashboard(request):
    con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv = import_data("classes.db")
    return render(request, 'gym_classes/dashboard.html', {"classes":raw_data_attendance})


def class_manager(request):
    return render(request, 'gym_classes/class_manager.html')

def content_manager(request):
    return render(request, 'gym_classes/content_manager.html')
