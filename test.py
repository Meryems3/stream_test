pip install lxml
import streamlit as st
import pandas as pd

st.title("Taux de référence des bons du Trésor")
date_str = st.sidebar.date_input("Entrez la date de valeur :")

def taux(date_str):
    try:
        date_obj = date_str

        u1 = "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-obligataire/Marche-des-bons-de-tresor/Marche-secondaire/Taux-de-reference-des-bons-du-tresor?"

        u3 = "block=e1d6b9bbf87f86f8ba53e8518e882982#address-c3367fcefc5f524397748201aee5dab8-e1d6b9bbf87f86f8ba53e8518e882982"

        u21 = "date="
        u22 = date_obj.day
        u23 = "%2F"
        u24 = date_obj.month
        u25 = "%2F"
        u26 = date_obj.year
        u27 = "&"

        u2 = u21 + str(u22) + u23 + str(u24) + u25 + str(u26) + u27

        url = u1 + u2 + u3

        data = pd.read_html(url)

        if len(data) > 0:
            data[0].drop(data[0].index[-1], inplace=True)
            return data[0]
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error("Erreur lors du chargement des données : " + str(e))
        return pd.DataFrame()

# Création d'interface Streamlit et affichage du tableau
data = taux(date_str)
if not data.empty:
    st.write("Tableau des taux de référence des bons du Trésor pour la date:", date_str)
    st.write(data)
else:
    st.error("Le DataFrame est vide. Veuillez charger des données valides.")


