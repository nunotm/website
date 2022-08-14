from django.shortcuts import render
from . import classes_jupyter
from django.contrib.auth.decorators import login_required

import numpy as np
import pandas as pd
from datetime import datetime

#def call_import_data():
#   con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv = import_data("classes.db")
#   return con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv

# Create your views here.
@login_required
def agresso(request):
    con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv = classes_jupyter.import_data("classes.db")

    mes = 7
    ano = 2022
    raw_data = raw_data_attendance
    payers_data = raw_data_payers

    agresso = classes_jupyter.agresso(mes, ano, raw_data, payers_data)
    return render(request, 'gym_classes/agresso.html', {"agresso":agresso})

@login_required
def class_manager(request):
    return render(request, 'gym_classes/class_manager.html')


@login_required
def content_manager(request):
    return render(request, 'gym_classes/content_manager.html')
