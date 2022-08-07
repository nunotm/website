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

    a=[list(pair) for pair in payers_data[["NAME","DESIGNATION"]].values]
    a=[pair for pair in np.array(a).reshape(-1)]
    it=iter(a)
    payers_dict = dict(zip(it,it))

    df_agresso = raw_data[(raw_data["DATE"]>=datetime(ano,mes,1)) & (raw_data["DATE"]<datetime(ano + 1 if mes == 12 else ano,1 if mes == 12 else mes + 1,1)) & (raw_data["AGRESSO"]==1)].sort_values(by="DATE").reset_index(drop=True)

    df_agresso["DAY"], df_agresso["MONTH"],df_agresso["YEAR"] = df_agresso["DATE"].apply(lambda x: x.day),df_agresso["DATE"].apply(lambda x: x.month),df_agresso["DATE"].apply(lambda x: x.year)
    df_agresso["CLUB"]=df_agresso["CLUB"].map(payers_dict)

    df_agresso_agreg = df_agresso.groupby(["CLUB","DAY", "DURATION", "LWP"]).count()
    dias = pd.DataFrame(pd.date_range(datetime(ano,mes,1), datetime(ano + 1 if mes == 12 else ano,1 if mes == 12 else mes + 1,1))[:-1])[0].apply(lambda x: x.day).values

    agresso = pd.DataFrame(0,columns=dias, index=df_agresso.groupby(["CLUB","DURATION", "LWP"]).count().index)
    agresso["TOTAL"]=0
    total = pd.DataFrame(0,columns=dias, index=df_agresso.groupby(["MONTH", "YEAR", "LWP"]).count().index)
    total["TOTAL"]=0

    agresso = pd.concat([agresso,total])

    for indx, row in agresso.iterrows():
        for dia in agresso.columns:
            try:
                agresso.loc[indx[0],indx[1],indx[2]][dia]  = df_agresso_agreg.loc[indx[0],dia,indx[1],indx[2]]["DATE"]
            except:
                pass
        agresso.loc[indx[0],indx[1],indx[2]]["TOTAL"] = agresso.loc[indx[0],indx[1],indx[2]].sum()

    try:
        for dia in agresso.columns:
            agresso.loc[agresso.index[-1]][dia] = agresso[dia].sum()
    except:
        pass

    #pd.set_option('display.max_columns', None)

    return render(request, 'gym_classes/agresso.html', {"agresso":agresso})

@login_required
def class_manager(request):
    return render(request, 'gym_classes/class_manager.html')


@login_required
def content_manager(request):
    return render(request, 'gym_classes/content_manager.html')
