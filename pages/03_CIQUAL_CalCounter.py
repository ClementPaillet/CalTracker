import streamlit as st
import pandas as pd

# Chargement de la base CIQUAL

@st.cache_data
def load_data(): 
    df = pd.read_csv("Table-Ciqual-2020_FR_2020-07-07.csv", sep=";", encoding="utf-8")
    df = df[['alim_nom_fr', 'alim_ssssg_libelle_fr', 'Energie, Règlement UE N° 1169/2011 (kcal/100 g)', 'Protéines (g/100 g)', 'Glucides (g/100 g)', 'Lipides (g/100 g)']]
    df = df.dropna(subset=['alim_nom_fr'])
    df.columns = ['Nom', 'Catégorie', 'Calories (kcal/100g)', 'Protéines (g/100g)', 'Glucides (g/100g)', 'Lipides (g/100g)']
    return df

df = load_data()

st.title("Suivi nutritionnel - Base CIQUAL 🇫🇷")

#1 Sélection des aliments

categories = df['Catégorie'].dropna().unique()
cat_selection = st.selectbox("Choisissez une catégorie d'aliments", sorted(categories))

filtrés = df[df['Catégorie'] == cat_selection]
aliments = filtrés['Nom'].unique()
aliment_choisi = st.selectbox("Choisissez un aliment", sorted(aliments))
mass = st.number_input("Quantité consommée (en grammes)", min_value=0, max_value=1000, step=10)

if "repas" not in st.session_state:
    st.session_state.repas = []

if st.button("Ajouter à la liste"):
    ligne = filtrés[filtrés['Nom'] == aliment_choisi].iloc[0]
    st.session_state.repas.append({ "Nom": aliment_choisi, "Quantité (g)": mass, "Calories": round(ligne['Calories (kcal/100g)'] * mass / 100, 2), "Protéines": round(ligne['Protéines (g/100g)'] * mass / 100, 2), "Glucides": round(ligne['Glucides (g/100g)'] * mass / 100, 2), "Lipides": round(ligne['Lipides (g/100g)'] * mass / 100, 2) })

#2 Affichage des aliments ajoutés

if st.session_state.repas:
    st.subheader("Résumé du repas")
    df_repas = pd.DataFrame(st.session_state.repas)
    st.dataframe(df_repas, use_container_width=True)

total = df_repas[['Calories', 'Protéines', 'Glucides', 'Lipides']].sum().to_frame().T
total.index = ['Total']
st.dataframe(total, use_container_width=True)

#3 Réinitialisation

if st.button("Réinitialiser le repas"):
    st.session_state.repas = []