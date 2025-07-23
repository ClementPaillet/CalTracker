import streamlit as st
import pandas as pd

# ---------------------------
# Base de données des aliments
# ---------------------------
data = [
    # ----------------- Protéines -----------------
    {"Aliment": "Poulet (cuit)", "Catégorie": "Protéines", "Protéines (g/100g)": 30.0, "Glucides (g/100g)": 0.0, "Lipides (g/100g)": 3.5, "Calories (kcal/100g)": 165},
    {"Aliment": "Œufs", "Catégorie": "Protéines", "Protéines (g/100g)": 13.0, "Glucides (g/100g)": 1.1, "Lipides (g/100g)": 11.0, "Calories (kcal/100g)": 143},
    {"Aliment": "Poisson blanc", "Catégorie": "Protéines", "Protéines (g/100g)": 19.0, "Glucides (g/100g)": 0.0, "Lipides (g/100g)": 1.0, "Calories (kcal/100g)": 90},
    {"Aliment": "Tofu", "Catégorie": "Protéines", "Protéines (g/100g)": 8.0, "Glucides (g/100g)": 1.9, "Lipides (g/100g)": 4.8, "Calories (kcal/100g)": 76},
    {"Aliment": "Steak haché 5%", "Catégorie": "Protéines", "Protéines (g/100g)": 26.0, "Glucides (g/100g)": 0.0, "Lipides (g/100g)": 5.0, "Calories (kcal/100g)": 155},
    {"Aliment": "Jambon blanc", "Catégorie": "Protéines", "Protéines (g/100g)": 18.5, "Glucides (g/100g)": 1.0, "Lipides (g/100g)": 3.5, "Calories (kcal/100g)": 110},
    {"Aliment": "Thon en conserve", "Catégorie": "Protéines", "Protéines (g/100g)": 25.0, "Glucides (g/100g)": 0.0, "Lipides (g/100g)": 1.0, "Calories (kcal/100g)": 115},
    {"Aliment": "Saumon", "Catégorie": "Protéines", "Protéines (g/100g)": 20.0, "Glucides (g/100g)": 0.0, "Lipides (g/100g)": 13.0, "Calories (kcal/100g)": 208},
    {"Aliment": "Tempeh", "Catégorie": "Protéines", "Protéines (g/100g)": 19.0, "Glucides (g/100g)": 9.0, "Lipides (g/100g)": 11.0, "Calories (kcal/100g)": 192},

    # ----------------- Glucides -----------------
    {"Aliment": "Riz cuit", "Catégorie": "Glucides", "Protéines (g/100g)": 2.7, "Glucides (g/100g)": 28.0, "Lipides (g/100g)": 0.3, "Calories (kcal/100g)": 130},
    {"Aliment": "Pâtes cuites", "Catégorie": "Glucides", "Protéines (g/100g)": 5.0, "Glucides (g/100g)": 25.0, "Lipides (g/100g)": 1.1, "Calories (kcal/100g)": 131},
    {"Aliment": "Pain complet", "Catégorie": "Glucides", "Protéines (g/100g)": 9.0, "Glucides (g/100g)": 40.0, "Lipides (g/100g)": 2.0, "Calories (kcal/100g)": 230},
    {"Aliment": "Pommes de terre", "Catégorie": "Glucides", "Protéines (g/100g)": 2.0, "Glucides (g/100g)": 17.0, "Lipides (g/100g)": 0.1, "Calories (kcal/100g)": 85},
    {"Aliment": "Quinoa", "Catégorie": "Glucides", "Protéines (g/100g)": 4.1, "Glucides (g/100g)": 21.3, "Lipides (g/100g)": 1.9, "Calories (kcal/100g)": 120},
    {"Aliment": "Flocons d'avoine", "Catégorie": "Glucides", "Protéines (g/100g)": 13.0, "Glucides (g/100g)": 60.0, "Lipides (g/100g)": 7.0, "Calories (kcal/100g)": 370},
    {"Aliment": "Boulgour", "Catégorie": "Glucides", "Protéines (g/100g)": 3.1, "Glucides (g/100g)": 18.6, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 83},

    # ----------------- Lipides -----------------
    {"Aliment": "Huile d'olive", "Catégorie": "Lipides", "Protéines (g/100g)": 0.0, "Glucides (g/100g)": 0.0, "Lipides (g/100g)": 100.0, "Calories (kcal/100g)": 900},
    {"Aliment": "Amandes", "Catégorie": "Lipides", "Protéines (g/100g)": 21.0, "Glucides (g/100g)": 22.0, "Lipides (g/100g)": 50.0, "Calories (kcal/100g)": 575},
    {"Aliment": "Avocat", "Catégorie": "Lipides", "Protéines (g/100g)": 2.0, "Glucides (g/100g)": 9.0, "Lipides (g/100g)": 15.0, "Calories (kcal/100g)": 160},
    {"Aliment": "Noix de cajou", "Catégorie": "Lipides", "Protéines (g/100g)": 18.0, "Glucides (g/100g)": 30.0, "Lipides (g/100g)": 44.0, "Calories (kcal/100g)": 553},
    {"Aliment": "Beurre", "Catégorie": "Lipides", "Protéines (g/100g)": 0.8, "Glucides (g/100g)": 0.1, "Lipides (g/100g)": 82.0, "Calories (kcal/100g)": 740},

    # ----------------- Fruits -----------------
    {"Aliment": "Pomme", "Catégorie": "Fruits", "Protéines (g/100g)": 0.3, "Glucides (g/100g)": 11.0, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 52},
    {"Aliment": "Banane", "Catégorie": "Fruits", "Protéines (g/100g)": 1.1, "Glucides (g/100g)": 23.0, "Lipides (g/100g)": 0.3, "Calories (kcal/100g)": 89},
    {"Aliment": "Orange", "Catégorie": "Fruits", "Protéines (g/100g)": 0.9, "Glucides (g/100g)": 8.3, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 47},
    {"Aliment": "Fraises", "Catégorie": "Fruits", "Protéines (g/100g)": 0.8, "Glucides (g/100g)": 7.7, "Lipides (g/100g)": 0.3, "Calories (kcal/100g)": 32},
    {"Aliment": "Raisins", "Catégorie": "Fruits", "Protéines (g/100g)": 0.6, "Glucides (g/100g)": 17.0, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 69},
    {"Aliment": "Poire", "Catégorie": "Fruits", "Protéines (g/100g)": 0.4, "Glucides (g/100g)": 10.0, "Lipides (g/100g)": 0.1, "Calories (kcal/100g)": 57},
    {"Aliment": "Kiwi", "Catégorie": "Fruits", "Protéines (g/100g)": 1.1, "Glucides (g/100g)": 14.0, "Lipides (g/100g)": 0.5, "Calories (kcal/100g)": 61},

    # ----------------- Légumes -----------------
    {"Aliment": "Carotte", "Catégorie": "Légumes", "Protéines (g/100g)": 0.9, "Glucides (g/100g)": 9.6, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 41},
    {"Aliment": "Brocoli", "Catégorie": "Légumes", "Protéines (g/100g)": 2.8, "Glucides (g/100g)": 6.6, "Lipides (g/100g)": 0.4, "Calories (kcal/100g)": 34},
    {"Aliment": "Tomate", "Catégorie": "Légumes", "Protéines (g/100g)": 0.9, "Glucides (g/100g)": 3.9, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 18},
    {"Aliment": "Épinards", "Catégorie": "Légumes", "Protéines (g/100g)": 2.7, "Glucides (g/100g)": 1.1, "Lipides (g/100g)": 0.3, "Calories (kcal/100g)": 23},
    {"Aliment": "Courgette", "Catégorie": "Légumes", "Protéines (g/100g)": 1.2, "Glucides (g/100g)": 2.1, "Lipides (g/100g)": 0.3, "Calories (kcal/100g)": 17},
    {"Aliment": "Poivron", "Catégorie": "Légumes", "Protéines (g/100g)": 1.0, "Glucides (g/100g)": 6.0, "Lipides (g/100g)": 0.3, "Calories (kcal/100g)": 29},
    {"Aliment": "Haricots verts", "Catégorie": "Légumes", "Protéines (g/100g)": 1.8, "Glucides (g/100g)": 3.1, "Lipides (g/100g)": 0.2, "Calories (kcal/100g)": 31},
    
    # Produits laitiers
    {"Aliment": "Lait entier", "Catégorie": "Produits laitiers", "Protéines (g/100g)": 3.2, "Glucides (g/100g)": 4.8, "Lipides (g/100g)": 3.6, "Calories (kcal/100g)": 64},
    {"Aliment": "Yaourt nature", "Catégorie": "Produits laitiers", "Protéines (g/100g)": 3.5, "Glucides (g/100g)": 4.0, "Lipides (g/100g)": 1.5, "Calories (kcal/100g)": 60},
    {"Aliment": "Fromage (emmental)", "Catégorie": "Produits laitiers", "Protéines (g/100g)": 28.0, "Glucides (g/100g)": 1.0, "Lipides (g/100g)": 31.0, "Calories (kcal/100g)": 380},

]

# DataFrame de base
df = pd.DataFrame(data)

# ---------------------------
# Interface utilisateur
# ---------------------------
st.set_page_config(page_title="Calculateur Nutritionnel", layout="centered")
st.title("🍽️ Calculateur Nutritionnel")
st.markdown("Ajoute les aliments consommés et leur quantité en grammes.")

# Liste complète des catégories présentes dans la base
categories = df["Catégorie"].unique().tolist()

# Mémoire de sélection persistante
if "selected_items" not in st.session_state:
    st.session_state.selected_items = []

st.markdown("### 1. Choisis tes aliments")

# Sélection dynamique de la catégorie
selected_category = st.selectbox("Catégorie :", categories)
aliments_in_category = df[df["Catégorie"] == selected_category]["Aliment"].tolist()

# Sélection dans un formulaire pour ajouter l’aliment
with st.form("form"):
    aliment = st.selectbox("Aliment :", aliments_in_category, key=selected_category)
    masse = st.number_input("Quantité consommée (en grammes)", min_value=1, max_value=1000, step=10)
    submitted = st.form_submit_button("Ajouter à la liste")

    if submitted:
        st.session_state.selected_items.append((aliment, masse))


# Affichage des aliments sélectionnés
st.markdown("### 2. Aliments sélectionnés")
if st.session_state.selected_items:
    for i, (a, m) in enumerate(st.session_state.selected_items):
        st.write(f"{i+1}. {a} - {m} g")
else:
    st.info("Aucun aliment sélectionné pour l'instant.")

# Calcul des résultats
if st.button("🔢 Calculer PGL + Calories") and st.session_state.selected_items:
    result_data = []

    for aliment, masse in st.session_state.selected_items:
        row = df[df["Aliment"] == aliment].iloc[0]
        ratio = masse / 100.0
        result_data.append({
            "Aliment": aliment,
            "Quantité (g)": masse,
            "Protéines (g)": round(row["Protéines (g/100g)"] * ratio, 1),
            "Glucides (g)": round(row["Glucides (g/100g)"] * ratio, 1),
            "Lipides (g)": round(row["Lipides (g/100g)"] * ratio, 1),
            "Calories (kcal)": round(row["Calories (kcal/100g)"] * ratio, 1),
        })

    result_df = pd.DataFrame(result_data)
    total_row = pd.DataFrame([{
        "Aliment": "Total",
        "Quantité (g)": "",
        "Protéines (g)": result_df["Protéines (g)"].sum(),
        "Glucides (g)": result_df["Glucides (g)"].sum(),
        "Lipides (g)": result_df["Lipides (g)"].sum(),
        "Calories (kcal)": result_df["Calories (kcal)"].sum()
    }])

    st.markdown("### 3. Résultat nutritionnel")
    st.dataframe(pd.concat([result_df, total_row], ignore_index=True))