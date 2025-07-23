import streamlit as st
import pandas as pd

st.title("🔥 Calcul des besoins caloriques")

st.markdown("""
## 🧠 Comprendre le métabolisme de base (MB)

Le **métabolisme de base (MB)** représente la quantité d’énergie minimale que votre corps dépense au repos pour assurer ses fonctions vitales : respiration, circulation sanguine, activité cérébrale, régulation thermique, etc.  
Il constitue **60 à 75 %** de la dépense énergétique totale quotidienne.

### 🎯 Pourquoi connaître son MB ?
- Adapter son alimentation à ses objectifs (perte de poids, maintien, prise de masse)
- Mieux comprendre sa dépense énergétique
- Optimiser ses performances sportives et sa récupération

### ⚙️ Facteurs influençant le MB
- **Masse musculaire** (plus de muscles = MB plus élevé)
- **Activité thyroïdienne**
- **Température ambiante**
- **Thermogenèse alimentaire**
- **Âge et sexe**
- **Stress chronique**
- **Activité physique quotidienne (NEAT)**

### 📏 Du MB aux besoins caloriques journaliers
Pour estimer vos besoins caloriques totaux, on multiplie le MB par un facteur d'activité (NAP) :

| Niveau d'activité       | NAP    |
|-------------------------|--------|
| Sédentaire              | 1.2    |
| Légèrement actif        | 1.4–1.6|
| Modérément actif        | 1.7–1.8|
| Très actif              | 1.9–2.1|
| Extrêmement actif       | 2.2–2.5|

""")

st.divider()

# ==== Saisie des données utilisateur ====
st.markdown("## 🧮 Entrez vos informations")

col1, col2 = st.columns(2)
with col1:
    sexe = st.radio("Sexe", ("Homme", "Femme"))
    poids = st.number_input("Poids (kg)", min_value=30.0, max_value=250.0, value=70.0, step=0.1)
    taille = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=175.0, step=0.1)
with col2:
    age = st.number_input("Âge (années)", min_value=10, max_value=100, value=30)
    masse_maigre = st.number_input("Masse maigre estimée (kg)", min_value=0.0, max_value=150.0, value=55.0, step=0.1)
    nap = st.number_input("Niveau d'activité (NAP)", min_value=1.0, max_value=3.0, value=1.0, step=0.1)

# ==== Calcul des MB ====

def calcul_bmr(poids, taille, age, sexe, masse_maigre):
    s = 1 if sexe == "Homme" else 0

    # Harris & Benedict
    if sexe == "Homme":
        hb = 66.473 + 13.7516 * poids + 5.0033 * taille - 6.755 * age
    else:
        hb = 655.0955 + 9.5634 * poids + 1.8496 * taille - 4.6756 * age

    # Mifflin-St Jeor
    mifflin = 10 * poids + 6.25 * taille - 5 * age + (5 if sexe == "Homme" else -161)

    # Cunningham
    cunningham = 370 + 21.6 * masse_maigre

    # Schofield (18–29 ans uniquement ici)
    if sexe == "Homme":
        schofield = 15.057 * poids + 692.2
    else:
        schofield = 14.818 * poids + 486.6

    # Henry (2005)
    henry = 14.2 * poids + 593

    return {
        "Harris & Benedict": round(hb),
        "Mifflin-St Jeor": round(mifflin),
        "Cunningham (1991)": round(cunningham),
        "Schofield": round(schofield),
        "Henry (Oxford, 2005)": round(henry)
    }

if st.button("Calculer mon métabolisme de base"):
    resultats = calcul_bmr(poids, taille, age, sexe, masse_maigre)
    df = pd.DataFrame(resultats.items(), columns=["Formule", "MB (kcal/jour)"])
    moyenne = round(df["MB (kcal/jour)"].mean(), 1)
    st.success("✅ Résultats du métabolisme de base")
    st.dataframe(df, use_container_width=True)

    st.markdown(f"### 📊 Moyenne des estimations : **{moyenne} kcal/jour**")
    st.markdown(f"### 🔥 Besoins caloriques totaux (MB × NAP = DEJ) : **{round(moyenne * nap)} kcal/jour**")

st.divider()
st.markdown("## 🏋️‍♂️ Peut-on augmenter son métabolisme de base ?")

st.markdown("""
Oui, et c’est même l’un des leviers les plus puissants pour améliorer sa dépense énergétique au repos. Voici trois leviers efficaces :

### 1️⃣ Musculation + cardio : le combo gagnant
L’association **musculation + endurance** permet :
- 🔼 Une augmentation de la **masse maigre** (musculation)
- 🔽 Une réduction de la **masse grasse** (cardio)
- 📉 Une diminution du **tour de taille**

➡️ Plus la masse musculaire augmente, plus le métabolisme de base s’élève, car le muscle est actif même au repos.

### 2️⃣ HIIT : l’effet post-effort
Les **entraînements fractionnés à haute intensité** (HIIT) provoquent un phénomène appelé **EPOC** (Excess Post-Exercise Oxygen Consumption), qui augmente temporairement le métabolisme après l’effort.

Pendant cette phase de récupération, le corps :
- Recharge ses réserves énergétiques (ATP)
- Élimine les déchets métaboliques (lactate)
- Rééquilibre sa température et ses hormones de stress

📌 Même si l’EPOC ne dure que quelques heures, l’intensité élevée de l’exercice contribue à un métabolisme plus actif.

### 3️⃣ Le NEAT : bouger au quotidien
Le **NEAT** correspond à toutes les dépenses énergétiques hors sport : marcher, se tenir debout, prendre les escaliers, etc.

- Très variable selon les modes de vie (de 6 à 50 % de la dépense totale !)
- Réduit en période de régime strict, ce qui peut ralentir les résultats
- ✅ Un **NEAT élevé est un facteur protecteur** contre la reprise de poids

💡 **Astuce** : Intégrer davantage de mouvement dans la journée (marche active, pauses dynamiques, escaliers...) peut avoir un effet significatif sur le métabolisme, sans effort structuré supplémentaire.
""")
