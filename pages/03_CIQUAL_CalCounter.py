# ➕🍽️➕ Calculateur de Macros - Complet

import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(
    page_title="Calculateur de Macros - Complet",
    page_icon="🍽️",
)

# Chargement de la base CIQUAL
# @st.cache_data
# def load_full_ciqual():
#     df = pd.read_csv("Table-Ciqual-2020_FR_2020-07-07.csv", sep=",", encoding="utf-8")
#     df = df[['alim_grp_nom_fr', 'alim_ssgrp_nom_fr', 'alim_ssssgrp_nom_fr', 'alim_nom_fr', 
#              'Energie, Règlement UE N° 1169/2011 (kJ/100 g)', 'Energie, Règlement UE N° 1169/2011 (kcal/100 g)',
#              'Protéines, N x facteur de Jones (g/100 g)', 'Glucides (g/100 g)', 'Lipides (g/100 g)']]
#     return df.dropna(subset=['alim_nom_fr'])
@st.cache_data
def load_full_ciqual():
    df = pd.read_csv("Table-Ciqual-2020_FR_2020-07-07.csv", sep=",", encoding="utf-8")
    df = df[['alim_grp_nom_fr', 'alim_ssgrp_nom_fr', 'alim_ssssgrp_nom_fr', 'alim_nom_fr', 
             'Energie, Règlement UE N° 1169/2011 (kJ/100 g)', 
             'Energie, Règlement UE N° 1169/2011 (kcal/100 g)',
             'Protéines, N x facteur de Jones (g/100 g)', 
             'Glucides (g/100 g)', 
             'Lipides (g/100 g)']]

    # Conversion des valeurs nutritionnelles en float
    cols_nutrition = [
        'Energie, Règlement UE N° 1169/2011 (kcal/100 g)',
        'Protéines, N x facteur de Jones (g/100 g)', 
        'Glucides (g/100 g)', 
        'Lipides (g/100 g)'
    ]
    for col in cols_nutrition:
        df[col] = df[col].str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df.dropna(subset=['alim_nom_fr'])


def normalize_text(text):
    """
    Normalise un texte pour faciliter la recherche :
    - minuscules
    - suppression des accents
    """
    if pd.isna(text):
        return ""

    text = str(text).lower()

    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

df = load_full_ciqual()

if "repas" not in st.session_state:
    st.session_state.repas = []

st.title("Suivi nutritionnel - Base CIQUAL 🇫🇷")

# ============================================================
# 🔎 RECHERCHE RAPIDE DANS TOUTE LA BASE CIQUAL
# ============================================================

st.markdown("## 🔎 Recherche rapide")

st.caption(
    "Commence à écrire le nom d'un aliment pour rechercher "
    "directement dans toute la base CIQUAL."
)

# Création d'une colonne de recherche normalisée
if "alim_nom_normalise" not in df.columns:
    df["alim_nom_normalise"] = df["alim_nom_fr"].apply(normalize_text)

# Barre de recherche
search_query = st.text_input(
    "Rechercher un aliment",
    placeholder="Exemple : poulet, riz, tomate, fromage..."
)

# Résultats de recherche
search_results = pd.DataFrame()

if search_query.strip():

    query_normalized = normalize_text(search_query.strip())

    # Recherche dans le nom de l'aliment
    search_results = df[
        df["alim_nom_normalise"].str.contains(
            query_normalized,
            case=False,
            na=False,
            regex=False
        )
    ].copy()

    # Nombre maximum de résultats affichés
    search_results = search_results.head(30)

    if len(search_results) > 0:

        # Création d'un libellé plus informatif
        search_results["label_recherche"] = (
            search_results["alim_nom_fr"]
            + " — "
            + search_results["alim_ssgrp_nom_fr"].fillna("")
        )

        selected_search_label = st.selectbox(
            "Résultats CIQUAL",
            search_results["label_recherche"].tolist()
        )

        # Récupération de la ligne correspondant au résultat choisi
        selected_search_row = search_results[
            search_results["label_recherche"] == selected_search_label
        ].iloc[0]

        # Affichage des informations de l'aliment
        st.info(
            f"**{selected_search_row['alim_nom_fr']}**\n\n"
            f"Groupe : {selected_search_row['alim_grp_nom_fr']}\n\n"
            f"Sous-groupe : {selected_search_row['alim_ssgrp_nom_fr']}"
        )

        # Quantité
        search_mass = st.number_input(
            "Quantité consommée (g)",
            min_value=1,
            max_value=5000,
            value=100,
            step=10,
            key="search_mass"
        )

        # Ajout au repas
        if st.button(
            "➕ Ajouter cet aliment",
            key="add_search_food"
        ):

            st.session_state.repas.append({
                "Nom": selected_search_row["alim_nom_fr"],
                "Quantité (g)": search_mass,
                "Calories": round(
                    selected_search_row[
                        "Energie, Règlement UE N° 1169/2011 (kcal/100 g)"
                    ] * search_mass / 100,
                    2
                ),
                "Protéines": round(
                    selected_search_row[
                        "Protéines, N x facteur de Jones (g/100 g)"
                    ] * search_mass / 100,
                    2
                ),
                "Glucides": round(
                    selected_search_row[
                        "Glucides (g/100 g)"
                    ] * search_mass / 100,
                    2
                ),
                "Lipides": round(
                    selected_search_row[
                        "Lipides (g/100 g)"
                    ] * search_mass / 100,
                    2
                )
            })

            st.success(
                f"{selected_search_row['alim_nom_fr']} "
                f"({search_mass} g) ajouté au repas !"
            )

    else:
        st.warning(
            f"Aucun aliment trouvé pour « {search_query} »."
        )

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

#if "repas" not in st.session_state:
#    st.session_state.repas = []

if st.button("Ajouter à la liste"):
    ligne = df_filtered_3[df_filtered_3['alim_nom_fr'] == selected_aliment].iloc[0]
    st.session_state.repas.append({
        "Nom": selected_aliment,
        "Quantité (g)": mass,
        "Calories": round(ligne['Energie, Règlement UE N° 1169/2011 (kcal/100 g)'] * mass / 100, 2),
        "Protéines": round(ligne['Protéines, N x facteur de Jones (g/100 g)'] * mass / 100, 2),
        "Glucides": round(ligne['Glucides (g/100 g)'] * mass / 100, 2),
        "Lipides": round(ligne['Lipides (g/100 g)'] * mass / 100, 2)
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
