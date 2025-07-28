import streamlit as st
import pandas as pd

# Chargement de la base CIQUAL
@st.cache_data
def load_full_ciqual():
    df = pd.read_csv("Table-Ciqual-2020_FR_2020-07-07.csv", sep=",", encoding="utf-8")
    df = df[['alim_grp_nom_fr', 'alim_ssgrp_nom_fr', 'alim_ssssgrp_nom_fr', 'alim_nom_fr', 
             'Energie, Règlement UE N° 1169/2011 (kJ/100 g)', 'Energie, Règlement UE N° 1169/2011 (kcal/100 g)',
             'Protéines, N x facteur de Jones (g/100 g)', 'Glucides (g/100 g)', 'Lipides (g/100 g)']]
    return df.dropna(subset=['alim_nom_fr'])

df = load_full_ciqual()

st.title("Suivi nutritionnel - Base CIQUAL 🇫🇷")

# 1. Sélection des aliments
st.markdown("## 🧭 Sélectionne un aliment via les catégories CIQUAL")

# Boîte 1 : Groupe principal
groupes = df["alim_grp_nom_fr"].dropna().unique()
selected_groupe = st.selectbox("Groupe alimentaire principal", sorted(groupes))

# Filtrage par groupe
df_filtered_1 = df[df["alim_grp_nom_fr"] == selected_groupe]

# Boîte 2 : Sous-groupe (s’il existe)
sous_groupes = df_filtered_1["alim_ssgrp_nom_fr"].dropna().unique()
selected_sous_groupe = None
if len(sous_groupes) > 0:
    selected_sous_groupe = st.selectbox("Sous-groupe", sorted(sous_groupes))
    df_filtered_2 = df_filtered_1[df_filtered_1["alim_ssgrp_nom_fr"] == selected_sous_groupe]
else:
    df_filtered_2 = df_filtered_1

# Boîte 3 : Sous-sous-groupe (s’il existe)
sss_groupes = df_filtered_2["alim_ssssgrp_nom_fr"].dropna().unique()
selected_sss_groupe = None
if len(sss_groupes) > 0:
    selected_sss_groupe = st.selectbox("Sous-sous-groupe", sorted(sss_groupes))
    df_filtered_3 = df_filtered_2[df_filtered_2["alim_ssssgrp_nom_fr"] == selected_sss_groupe]
else:
    df_filtered_3 = df_filtered_2

# Boîte 4 : Aliments
aliments = df_filtered_3["alim_nom_fr"].dropna().unique()
selected_aliment = st.selectbox("Choix de l’aliment", sorted(aliments))

st.session_state.selected_aliment = selected_aliment

mass = st.number_input("Quantité consommée (en grammes)", min_value=0, max_value=1000, step=10)

if "repas" not in st.session_state:
    st.session_state.repas = []

if st.button("Ajouter à la liste"):
    ligne = df_filtered_3[df_filtered_3['alim_nom_fr'] == selected_aliment].iloc[0]
    st.session_state.repas.append({
        "Nom": selected_aliment,
        "Quantité (g)": mass,
        "Calories": round(ligne['Energie, Règlement UE N° 1169/2011 (kcal/100 g)'] * mass / 100, 2),
        "Protéines": round(ligne['Protéines, N x facteur de Jones (g/100 g)'] * mass / 100, 2),
        "Glucides": round(ligne['Glucides (g/100g)'] * mass / 100, 2),
        "Lipides": round(ligne['Lipides (g/100g)'] * mass / 100, 2)
    })

# 2. Affichage des aliments ajoutés
if st.session_state.repas:
    st.subheader("Résumé du repas")
    df_repas = pd.DataFrame(st.session_state.repas)
    st.dataframe(df_repas, use_container_width=True)

    total = df_repas[['Calories', 'Protéines', 'Glucides', 'Lipides']].sum().to_frame().T
    total.index = ['Total']
    st.dataframe(total, use_container_width=True)

# 3. Réinitialisation
if st.button("Réinitialiser le repas"):
    st.session_state.repas = []
