from django.shortcuts import render

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.collections import LineCollection
# from matplotlib.colors import ListedColormap, BoundaryNorm
# import matplotlib.ticker as mtick
# import seaborn as sns
# sns.set()
#
# import statsmodels.api as sm
# from sklearn.linear_model import LinearRegression
# from sklearn.feature_selection import f_regression
# from sklearn.preprocessing import StandardScaler, Normalizer
# from sklearn.cluster import KMeans
#
# from datetime import datetime
# from datetime import timedelta
# from datetime import time
#
# from calendar import monthrange
#
# from scipy.stats import norm
# from scipy.stats import t
#
# import sqlite3

def import_data(db_file):
    con = sqlite3.connect(db_file)
    raw_data_attendance = pd.read_sql_query("SELECT * from ATTENDANCE", con)
    raw_data_classes = pd.read_sql_query("SELECT * from CLASSES", con)
    raw_data_payers = pd.read_sql_query("SELECT * from PAYERS", con)
    raw_data_rv = pd.read_sql_query("SELECT * from RECIBOS_VERDES", con)

    raw_data_attendance.sort_values(by=["DATE", "TIME"])

    raw_data_attendance["DATE"] = raw_data_attendance["DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    raw_data_classes["START_DATE"] = raw_data_classes["START_DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    raw_data_classes["END_DATE"] = raw_data_classes["END_DATE"].fillna("-".join([str(datetime.today().year).zfill(4),str(datetime.today().month).zfill(2),str(datetime.today().day).zfill(2)]))
    raw_data_classes["END_DATE"] = raw_data_classes["END_DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    raw_data_attendance["DAY_DIFF"] = raw_data_attendance["DATE"].apply(lambda x: (x-datetime.today()).days+1)
    raw_data_attendance["WEEKDAY"] = raw_data_attendance["DATE"].apply(lambda x: x.isoweekday())
    raw_data_attendance["WEEKDAY"]=raw_data_attendance["WEEKDAY"]+1
    raw_data_attendance["WEEKDAY"]=raw_data_attendance["WEEKDAY"].replace(to_replace=8, value=1)
    raw_data_classes["STUDIO"] = raw_data_classes["STUDIO"].fillna("")

    raw_data_rv["DATA_EMISSAO"] = raw_data_rv["DATA_EMISSAO"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    raw_data_rv["INICIO_PERIODO"] = raw_data_rv["INICIO_PERIODO"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    raw_data_rv["FIM_PERIODO"] = raw_data_rv["FIM_PERIODO"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))

    raw_data_rv["ANO_EMISSAO"] = raw_data_rv["DATA_EMISSAO"].apply(lambda x: x.year)
    raw_data_rv["MES_EMISSAO"] = raw_data_rv["DATA_EMISSAO"].apply(lambda x: x.month)


    raw_data_attendance["CAPACITY"]=pd.DataFrame(np.zeros_like(raw_data_attendance.index))
    for ind, row in raw_data_attendance[raw_data_attendance["DAY_DIFF"]<=0].iterrows():
        capacity_df = raw_data_classes[(raw_data_classes["WEEKDAY"]==row["WEEKDAY"]) &
                                   (raw_data_classes["CLUB"]==row["CLUB"]) &
                                   (raw_data_classes["CLASS"]==row["CLASS"]) &
                                   (raw_data_classes["TIME"]==row["TIME"]) &
                                   (raw_data_classes["DURATION"]==row["DURATION"])]

        capacity_df = capacity_df[capacity_df["END_DATE"]>=row["DATE"]]

        try:
            capacity_df = capacity_df[capacity_df["END_DATE"]==min(capacity_df["END_DATE"])]
        except:
            continue

        if len(raw_data_classes) > 1:
            capacity_df=capacity_df[capacity_df["STUDIO"]!=""]

        try:
            raw_data_attendance.loc[ind,"CAPACITY"] = capacity_df["CAPACITY"].iloc[0]
        except:
            continue

    raw_data_attendance["RESERVATIONS % CAPACITY"] = pd.DataFrame(np.zeros_like(raw_data_attendance.index))
    raw_data_attendance["ATTENDANCE % RESERVATIONS"] = pd.DataFrame(np.zeros_like(raw_data_attendance.index))
    raw_data_attendance["ATTENDANCE % CAPACITY"] = pd.DataFrame(np.zeros_like(raw_data_attendance.index))


    for ind, row in raw_data_attendance.iterrows():


        if row["CAPACITY"]!=0:
            raw_data_attendance.loc[ind,"RESERVATIONS % CAPACITY"] = row["RESERVATIONS"] / row["CAPACITY"]

        if row["RESERVATIONS"]!=0:
            raw_data_attendance.loc[ind,"ATTENDANCE % RESERVATIONS"] = row["ATTENDANCE"] / row["RESERVATIONS"]

        if row["CAPACITY"]!=0:
            raw_data_attendance.loc[ind,"ATTENDANCE % CAPACITY"] = row["ATTENDANCE"] / row["CAPACITY"]

   return con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv

def call_import_data():
   con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv = import_data("classes.db")
   return con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv

# Create your views here.
def dashboard(request):
#    con, raw_data_attendance, raw_data_classes, raw_data_payers, raw_data_rv = call_import_data()
    return render(request)#, 'gym_classes/dashboard.html', {"classes":raw_data_attendance})


def class_manager(request):
    return render(request, 'gym_classes/class_manager.html')

def content_manager(request):
    return render(request, 'gym_classes/content_manager.html')
