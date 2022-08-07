import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.ticker as mtick
import seaborn as sns
sns.set()

import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import f_regression
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.cluster import KMeans

from datetime import datetime
from datetime import timedelta
from datetime import time

from calendar import monthrange

from scipy.stats import norm
from scipy.stats import t

import sqlite3

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

def plot_evolucao(df, club, week_day, aula, own_class, plot_media_mensal, plot_media_trimestral):

    plt_data = get_plot_data(df, club, week_day, aula, own_class)

    min_data = plt_data["DATE"].min()
    max_data = plt_data["DATE"].max()


    fig, ax = plt.subplots(figsize=(16,9))

    if plot_media_mensal:
        media_mensal = [plt_data[(plt_data["DATE"]>x["DATE"]-timedelta(30)) &
                                 (plt_data["DATE"]<=x["DATE"])
                                ]["ATTENDANCE % CAPACITY"].mean()*100 for ind, x in plt_data.iterrows()]

    if plot_media_trimestral:
        media_trimestral = [plt_data[(plt_data["DATE"]>x["DATE"]-timedelta(90)) &
                                 (plt_data["DATE"]<=x["DATE"])
                                ]["ATTENDANCE % CAPACITY"].mean()*100 for ind, x in plt_data.iterrows()]


    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.scatter(plt_data["DATE"],plt_data["ATTENDANCE % CAPACITY"]*100, linewidth=1, s=4)
    ax.plot(plt_data["DATE"],media_mensal, linewidth=3, color="red", label = "média mensal")
    ax.plot(plt_data["DATE"],media_trimestral, linewidth=2, color="orange", label = "média trimestral")
    plt.legend();

    weekdays = dict({
        1:"ao domingo",
        2:"à segunda",
        3:"à terça",
        4:"à quarta",
        5:"à quinta",
        6:"à sexta",
        7:"ao sábado"
    })

    try:
        week_day = int(week_day)
    except:
        week_day = "all"

    plt.title("Evolução " +
              ("da aula de " + (aula + " ") if aula != "all" else "de todas as aulas ") +
              ((weekdays[week_day] + " ") if week_day != "all" else " ") +
              ("no " + (club + " ") if club != "all" else "em todos os clubes ") +
              ("(inc. substituições)" if own_class == False else ""),
              fontsize=14);

    return plt_data

def get_plot_data(df, club, week_day, aula, own_class):

    filters = []
    values = []

    if club != "all":
        filters.append("CLUB")
        values.append(club)

    if week_day != "all":
        week_day = int(week_day)
        filters.append("WEEKDAY")
        values.append(week_day)

    if aula != "all":
        filters.append("CLASS")
        values.append(aula)

    if own_class != "all":
        own_class = int(own_class)
        filters.append("OWN_CLASS")
        values.append(own_class)

    plt_data = df.copy()
    plt_data = plt_data[plt_data["DATE"]<=datetime.today()]

    for filt,val in zip(filters, values):
        if val!="all":
            plt_data = plt_data[plt_data[filt]==val].reset_index(drop=True)

    plt_data = plt_data[plt_data["CAPACITY"]!=0].reset_index(drop=True)

    return plt_data

def plot_agreg(df, club, week_day, aula, own_class):

    try:
        week_day = int(week_day)
    except:
        week_day = "all"

    plt_data = get_plot_data(df, club, week_day, aula, own_class)

    plt_data["YEAR"]=pd.DataFrame([x["DATE"].year for ind, x in plt_data.iterrows()])
    plt_data["MONTH"]=pd.DataFrame([x["DATE"].month for ind, x in plt_data.iterrows()])

    aux = plt_data.groupby(["YEAR","MONTH"]).mean()*100
    aux["MIN"]=plt_data.groupby(["YEAR","MONTH"])["ATTENDANCE % CAPACITY"].min()*100
    aux["MAX"]=plt_data.groupby(["YEAR","MONTH"])["ATTENDANCE % CAPACITY"].max()*100
    aux["STD"]=plt_data.groupby(["YEAR","MONTH"])["ATTENDANCE % CAPACITY"].std()*100
    aux["DATE_PLOT"]=pd.DataFrame([datetime(x[0], x[1],1) for x in aux.index], index=aux.index)

    fig, ax = plt.subplots(figsize=(16,9))

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.fill_between(aux["DATE_PLOT"],
                    aux["ATTENDANCE % CAPACITY"].values-aux["STD"].values/2,
                    aux["ATTENDANCE % CAPACITY"].values+aux["STD"].values/2,
                    alpha=0.05, color="red", label = "média +/- desv. pad.")
    eb = ax.errorbar(x = aux["DATE_PLOT"],
                y = aux["ATTENDANCE % CAPACITY"],
                yerr = np.append(aux["ATTENDANCE % CAPACITY"].values-aux["MIN"].values,aux["MAX"].values-aux["ATTENDANCE % CAPACITY"].values).reshape(-1, len(aux["MAX"])),
                linewidth = 3,
                elinewidth  = 1, ecolor = "orange",
                capsize = 5, capthick = 1,
               label = "% min/máx.");
    eb[-1][0].set_linestyle("--")

    plt.legend();


    min_data = aux["DATE_PLOT"].min()
    max_data = aux["DATE_PLOT"].max()

    #plt.title("Monthly aggregate performance", fontsize=20)

    weekdays = dict({
        1:"ao domingo",
        2:"à segunda",
        3:"à terça",
        4:"à quarta",
        5:"à quinta",
        6:"à sexta",
        7:"ao sábado"
    })

    plt.title("Evolução mensal agregada " +
              ((weekdays[week_day] + " ") if week_day != "all" else " ") +
              ("da aula de " + (aula + " ") if aula != "all" else "de todas as aulas ") +
              ("no " + (club + " ") if club != "all" else "em todos os clubes ") +
              ("(inc. substituições)" if own_class == False else ""),
              fontsize=14);

def plot_pandemic_impact(df, club, week_day, aula, own_class):

    try:
        week_day = int(week_day)
    except:
        week_day = "all"

    plt_data = get_plot_data(df, club, week_day, aula, own_class)

    slice_1 = plt_data[plt_data["DATE"]<datetime(2020,3,18)]
    slice_2 = plt_data[plt_data["DATE"]>=datetime(2020,3,18)]

    fig, ax = plt.subplots(figsize=(16,9))

    medida = "ATTENDANCE % CAPACITY"

    sns.histplot(slice_1[medida], label="pré-pandemia", bins = np.arange(0,1.1,0.1),alpha=0.5, stat="probability")
    sns.histplot(slice_2[medida], label="pandemia", bins = np.arange(0,1.1,0.1),color="orange",alpha=0.5, stat="probability");

    plt.legend();
    plt.xlim(0,1);

    weekdays = dict({
        1:"ao domingo",
        2:"à segunda",
        3:"à terça",
        4:"à quarta",
        5:"à quinta",
        6:"à sexta",
        7:"ao sábado"
    })

    plt.title("Impacto na ocupação " +
              ("da aula de " + (aula + " ") if aula != "all" else "de todas as aulas ") +
              ((weekdays[week_day] + " ") if week_day != "all" else " ") +
              ("no " + (club + " ") if club != "all" else "em todos os clubes ") +
              ("(inc. substituições)" if own_class == False else ""),
              fontsize=14);

def analise_comparacao_periodos(clube, aula, week_day, data_incio, data_cut_off, data_fim, own_class, conf, side="left"):

    club_classes = raw_data_attendance[raw_data_attendance["DATE"]<=datetime.today()].reset_index(drop=True)

    if clube != "all":
        club_classes = club_classes[
            (club_classes["CLUB"]==clube)
        ].reset_index(drop=True)

    if own_class==True:
        club_classes = club_classes[
            (club_classes["OWN_CLASS"]==1)
        ].reset_index(drop=True)

    if aula!="all":
        club_classes = club_classes[
            (club_classes["CLASS"]==aula)
        ].reset_index(drop=True)

    if week_day!="all":
        club_classes = club_classes[
            (club_classes["WEEKDAY"]==week_day)
        ].reset_index(drop=True)


    club_classes_before = club_classes[(club_classes["DATE"]>=data_inicio) & (club_classes["DATE"]<data_cut_off)]
    club_classes_after = club_classes[(club_classes["DATE"]>=data_cut_off) & (club_classes["DATE"]<data_fim)]

    mu_before = club_classes_before["ATTENDANCE % CAPACITY"].mean()
    mu_after = club_classes_after["ATTENDANCE % CAPACITY"].mean()
    sigma_before = club_classes_before["ATTENDANCE % CAPACITY"].std()
    sigma_after = club_classes_after["ATTENDANCE % CAPACITY"].std()
    n_before = len(club_classes_before["ATTENDANCE % CAPACITY"])
    n_after = len(club_classes_after["ATTENDANCE % CAPACITY"])

    critical_value = (mu_after-mu_before)/(sigma_after**2/n_after+sigma_before**2/n_before)**0.5
    dgs_freedom = n_before+n_after-2

    print("before:\t{mu_b:.2f}% +/- {sigma_b:.2f} pp".format(mu_b=mu_before*100, sigma_b=sigma_before*100))
    print("after:\t{mu_a:.2f}% +/- {sigma_a:.2f} pp".format(mu_a=mu_after*100, sigma_a=sigma_after*100))

    fig,ax = plt.subplots(figsize=(16,9))

    if side=="left":
        cutoff_value = t.ppf(1-conf,dgs_freedom)
    elif side=="right":
        cutoff_value = t.ppf(conf,dgs_freedom)
    else:
        cutoff_value = t.ppf(1-conf/2,dgs_freedom)

    x_range = np.arange(-4,4,0.01)
    y_range = np.array([t.pdf(x,dgs_freedom) for x in x_range])

    p_value = t.cdf(critical_value, dgs_freedom)

    if side == "left":
        if p_value <= 1-conf:
            print("H0 is rejected.")
        else:
            print("H0 is not rejected.")
    elif side == "right":
        if 1-p_value <= 1-conf:
            print("H0 is rejected.")
        else:
            print("H0 is not rejected.")
    else:
        print("tbc")

    plt.plot(x_range,y_range);
    if side == "left":
        plt.fill_between(np.arange(-4, cutoff_value,0.01),0,np.array([t.pdf(x,dgs_freedom) for x in np.arange(-4, cutoff_value,0.01)]), color="pink", alpha=0.3, label="rejection region");
    elif side=="right":
        plt.fill_between(np.arange(cutoff_value,4,0.01),0,np.array([t.pdf(x,dgs_freedom) for x in np.arange(cutoff_value,4,0.01)]), color="pink", alpha=0.3, label="rejection region");
    else:
        plt.fill_between(np.arange(-4, cutoff_value,0.01),0,np.array([t.pdf(x,dgs_freedom) for x in np.arange(-4, cutoff_value,0.01)]), color="pink", alpha=0.3, label="rejection region");
        cutoff_value = t.ppf(1-conf/2,dgs_freedom)
        plt.fill_between(np.arange(cutoff_value,4,0.01),0,np.array([t.pdf(x,dgs_freedom) for x in np.arange(cutoff_value,4,0.01)]), color="pink", alpha=0.3, label="rejection region");

    plt.vlines(cutoff_value,0,t.pdf(cutoff_value,n_before+n_after-2), color="pink");
    plt.scatter(cutoff_value,t.pdf(cutoff_value,n_before+n_after-2), color="pink");
    plt.legend();
    plt.vlines(critical_value,0,t.pdf(critical_value,dgs_freedom), color="red");
    plt.scatter(critical_value,t.pdf(critical_value,dgs_freedom), color="red");
    plt.title("H0: mu_before >= mu_after\nPeríodo de comparação: {dia_min:02d}-{mes_min:02d}-{ano_min:04d} até {dia_max:02d}-{mes_max:02d}-{ano_max:04d}\nPeríodo de análise: {dia_min2:02d}-{mes_min2:02d}-{ano_min2:04d} até {dia_max2:02d}-{mes_max2:02d}-{ano_max2:04d}".format(
        dia_min=club_classes_before.iloc[0]["DATE"].day,
        mes_min=club_classes_before.iloc[0]["DATE"].month,
        ano_min=club_classes_before.iloc[0]["DATE"].year,
        dia_max=club_classes_before.iloc[-1]["DATE"].day,
        mes_max=club_classes_before.iloc[-1]["DATE"].month,
        ano_max=club_classes_before.iloc[-1]["DATE"].year,

        dia_min2=club_classes_after.iloc[0]["DATE"].day,
        mes_min2=club_classes_after.iloc[0]["DATE"].month,
        ano_min2=club_classes_after.iloc[0]["DATE"].year,
        dia_max2=club_classes_after.iloc[-1]["DATE"].day,
        mes_max2=club_classes_after.iloc[-1]["DATE"].month,
        ano_max2=club_classes_after.iloc[-1]["DATE"].year
    ), fontsize=15);


    return club_classes, club_classes_before, club_classes_after, critical_value, dgs_freedom, p_value, cutoff_value

def agresso(mes, ano, raw_data, payers_data):
    a=[list(pair) for pair in payers_data[["NAME","DESIGNATION"]].values]
    a=[pair for pair in np.array(a).reshape(-1)]
    it=iter(a)
    payers_dict = dict(zip(it,it))

    df_agresso = raw_data[
        (raw_data["DATE"]>=datetime(ano,mes,1)) &
        (raw_data["DATE"]<datetime(ano + 1 if mes == 12 else ano,1 if mes == 12 else mes + 1,1)) &
        (raw_data["AGRESSO"]==1)
    ].sort_values(by="DATE").reset_index(drop=True)

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

    for dia in agresso.columns:
        agresso.loc[agresso.index[-1]][dia] = agresso[dia].sum()

    pd.set_option('display.max_columns', None)

    return agresso
