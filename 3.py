
#Importation des librairies

import streamlit as st
import datetime
import pandas as pd
import numpy as np

#Importation du tableau de taux 

def taux(date_str):
    
    date_obj=date_str

    u1="https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-obligataire/Marche-des-bons-de-tresor/Marche-secondaire/Taux-de-reference-des-bons-du-tresor?"

    #u2="date=24%2F02%2F2023&"

    u3="block=e1d6b9bbf87f86f8ba53e8518e882982#address-c3367fcefc5f524397748201aee5dab8-e1d6b9bbf87f86f8ba53e8518e882982"

    u21="date="

    u22=date_obj.day

    u23="%2F"

    u24=date_obj.month

    u25="%2F"

    u26=date_obj.year

    u27="&"

    u2=u21+ str(u22) + u23 + str(u24) + u25 + str(u26) + u27

    url=u1+u2+u3

    data=pd.read_html(url)

    data[0].drop(data[0].index[-1], inplace=True)

    return data[0]

#Création d'interface streamlit et affichage du tableau

st.title("Taux de référence des bons du Trésor")
date_str = st.sidebar.date_input("Entrez la date de valeur :")
data = taux(date_str)
st.write("Tableau des taux de référence des bons du Trésor pour la date:", date_str)
st.write(data)


#Manipulation du tableau et affichage sur streamlit


data["Maturité"] = pd.to_datetime(data["Date d'échéance"],format='%d/%m/%Y') - pd.to_datetime(data['Date de la valeur'],format='%d/%m/%Y')

data["Maturité"] = data["Maturité"].dt.total_seconds().astype(float)/ (24 * 60 * 60)

data["Maturitéa"] = data["Maturité"]/ (365)

del data["Transaction"]

data.rename(columns={"Date d'échéance": 'Echeance', 'Taux moyen pondéré': 'Taux', 'Date de la valeur':'Date valeur', 'Maturité':'Maturité', 'Maturitéa':'Maturité en années' }, inplace=True)

data["Taux"] = data["Taux"].str.replace('%', '').str.replace(',', '.').astype(float)
data["Taux"]=data["Taux"]/100
del data["Date valeur"]


data["TMPA"] = 0
for i in range(len(data)):
    if data['Maturité'][i] < 365:
        data['TMPA'][i] = ((1 + (data['Taux'][i] * data['Maturité'][i] / 360)) ** (365 / data['Maturité'][i]) - 1)
    elif data['Maturité'][i] > 365:
        data['TMPA'][i] = data['Taux'][i]
    

#Méthode de bootstrap

data= data.sort_values(by='Maturité', ascending=False)


#sidebar
date_echeance=st.sidebar.date_input("Veuillez entrer la date d'échéance de l'obligation")
date_emission=st.sidebar.date_input("Veuillez entrer la date d'émission de l'obligation")

date_emission= datetime.datetime.combine(date_emission, datetime.datetime.min.time())
date_echeance= datetime.datetime.combine(date_echeance, datetime.datetime.min.time())

MJ = (date_echeance - date_emission).days

#MJ=st.number_input('Veuiller entrer la maturité en jours',step=1)

def interpolation_lineaire(MJ, data):
    taux_interpole=0
    x=MJ
    if x<data['Maturité'][0]:
        x1 = data['Maturité'][0]
        x2 = data['Maturité'][1]
        y1 = data['Taux'][0]
        y2 = data['Taux'][1]
        taux_interpole=y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    elif x>data['Maturité'][len(data)-1] :
        x1 = data['Maturité'][len(data)-1]
        x2 = data['Maturité'][len(data)-2]
        y1 = data['Taux'][len(data)-1]
        y2 = data['Taux'][len(data)-2]
        taux_interpole=y1 + (y1 - y2) * (x - x1) / (x1 - x2)      
    else :
        for i in range(len(data['Maturité']) - 1):
            if x==data['Maturité'][i]:
                taux_interpole = data['Taux'][i]
            elif data['Maturité'][i] <= MJ < data['Maturité'][i + 1]:
                if data['Maturité'][i]<365 and data['Maturité'][i + 1]>365 :
                    x1 = data['Maturité'][i]
                    x2 = data['Maturité'][i + 1]
                    y1 = data['TMPA'][i]
                    y2 = data['TMPA'][i + 1]
                    taux_interpole = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
                else :
                    x1 = data['Maturité'][i]
                    x2 = data['Maturité'][i + 1]
                    y1 = data['Taux'][i]
                    y2 = data['Taux'][i + 1]
                    taux_interpole = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
                

    return taux_interpole


taux_inter = interpolation_lineaire(MJ, data)
st.write(f"Cette obligation est de maturité de {MJ} jours dont le taux : {taux_inter:.4f}")





tab_tenors=st.sidebar.radio("Voulez vous afficher le tableau de tenors ?",["Oui","Non"])




##Création de base de données des tenors standards


fd=pd.DataFrame({'Maturité pleine':['JJ','13 sem','26sem','52sem','1an','2ans','3ans','4ans','5ans','6ans','7ans','8ans','9ans','10ans','11ans','12ans','13ans','14ans','15ans','16ans','17ans','18ans','19ans','20ans','21ans','22ans','23ans','24ans','25ans','26ans','27ans','28ans','29ans','30ans'],'Maturité':[1,91,182,364,365,731,1096,1461,1826,2192,2557,2922,3287,3653,4018,4383,4748,5114,5479,5844,6209,6575,6940,7305,7670,8036,8401,8766,9131,9497,9862,10227,10592,10958
]})
fd['Taux rendement'] = fd['Maturité'].apply(lambda maturite: interpolation_lineaire(maturite, data))

if tab_tenors=="Oui":
    st.write(fd)




