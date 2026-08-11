import streamlit as st

# ============================================================
# HERO ANIN
# ============================================================
# -----------------------------------------------------------------
# 2️⃣  CSS – on le charge **une seule fois** (vous pouvez le mettre
#    dans un fichier séparé et le lire avec open() si vous le
#    préférez)
# -----------------------------------------------------------------
css = """
<style>
/* ---------- HERO ------------------------------------------------- */
.anin-hero{
    width:100%;
    padding:55px 30px 50px;
    margin:20px 0 40px;
    border-radius:24px;
    background:linear-gradient(
        135deg,
        #111827 0%,
        #1f2937 50%,
        #111827 100%
    );
    text-align:center;
    box-shadow:0 10px 30px rgba(0,0,0,0.15);
    border:1px solid rgba(255,255,255,0.08);
}

/* Logo ----------------------------------------------------------- */
.anin-logo{
    font-size:80px;
    font-weight:900;
    letter-spacing:12px;
    line-height:1;
    color:#fff;
    margin-bottom:18px;
    text-transform:uppercase;
}

/* Subtitle -------------------------------------------------------- */
.anin-subtitle{
    font-size:20px;
    font-weight:600;
    letter-spacing:3px;
    color:#d1d5db;
    margin-bottom:18px;
}

/* Baseline -------------------------------------------------------- */
.anin-baseline{
    font-size:16px;
    letter-spacing:2px;
    color:#9ca3af;
}

/* Responsive (≤ 600 px) ------------------------------------------ */
@media (max-width:600px){
    .anin-logo{
        font-size:55px;
        letter-spacing:7px;
    }
    .inan-subtitle{
        font-size:13px;
        letter-spacing:1.5px;
    }
    .inan-baseline{
        font-size:13px;
    }
}
</style>
"""

# -----------------------------------------------------------------
# 3️⃣  AFFICHAGE du CSS  
#    - Si vous avez Streamlit ≥ 1.38 → `st.html(css)` (recommandé)  
#    - Sinon → `st.markdown(css, unsafe_allow_html=True)`
# -----------------------------------------------------------------
try:
    # st.html existe depuis la version 1.38
    st.html(css)                     # type: ignore[attr-defined]
except AttributeError:               # pragma: no cover
    # Version plus ancienne → on garde l'ancienne méthode
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 4️⃣  HERO HTML (le bloc qui apparaît à l'écran)
# -----------------------------------------------------------------
hero_html = """
<div class="anin-hero">
    <div class="anin-logo">ANIN</div>
    <div class="anin-subtitle">ADAPTIVE NUTRITION & INTENSITY NEXUS</div>
    <div class="anin-baseline">Nutrition · Training · Performance</div>
</div>
"""

# Même logique que pour le CSS : `st.html` si dispo, sinon `st.markdown`
try:
    st.html(hero_html)   # le paramètre height évite le “scroll” inutile
except AttributeError:               # pragma: no cover
    st.markdown(hero_html, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 5️⃣  (Optionnel) – Un petit séparateur ou du contenu supplémentaire
# -----------------------------------------------------------------
st.markdown("---") 
# ============================================================

# Titre principal
st.title("Bienvenue sur l'assistant nutrition et sport le plus évolué.")

# Sous-titre
st.subheader("Comprendre les bases de la nutrition pour mieux manger")

# Contenu introductif
st.markdown("""
La **nutrition** est la science qui étudie les interactions entre les aliments et l’organisme. Elle joue un rôle fondamental dans le maintien de la santé, la prévention des maladies et le bon fonctionnement du corps humain. Une alimentation équilibrée permet d’apporter à l’organisme l’ensemble des nutriments nécessaires à ses besoins énergétiques, à la croissance, à la réparation des tissus et au bon déroulement des fonctions physiologiques.

Les éléments clés de la nutrition sont répartis en deux grandes catégories :  
- **Les macronutriments** : glucides, lipides et protéines. Ils fournissent l’énergie et permettent le fonctionnement global du corps.  
  - *Les glucides* sont la principale source d’énergie.  
  - *Les lipides* participent à la construction cellulaire et au transport de vitamines.  
  - *Les protéines* permettent la construction et la réparation des tissus.  
- **Les micronutriments** : vitamines et minéraux, indispensables en petites quantités mais essentiels à de nombreuses fonctions biologiques.

D'autres facteurs importants :
- **L’hydratation** : indispensable à toutes les fonctions du corps.
- **La densité nutritionnelle** des aliments : il vaut mieux consommer des aliments riches en nutriments que des calories vides.
- **La fréquence et répartition des repas**, le **niveau d’activité physique** et le **contexte social** influencent aussi nos besoins.

---

### 🧮 La balance calorique

La **balance calorique** correspond à la différence entre les calories consommées via l’alimentation et celles dépensées par l’organisme. Elle détermine si l’on prend, perd ou maintient son poids :

- Si **apports > dépenses** : on est en excédent → prise de poids.
- Si **apports < dépenses** : on est en déficit → perte de poids.
- Si **apports = dépenses** : le poids est stable.

Connaître et maîtriser sa balance calorique est un outil central pour atteindre ses objectifs nutritionnels.

---

### 🔍 Explorez les outils disponibles :

#### 👉 Calcul des besoins caloriques
Calculez facilement vos besoins énergétiques journaliers en fonction de votre âge, sexe, taille, poids et activité physique.

#### 👉 Calculateur simple des valeurs nutritionnelles
Recherchez quelques aliments courants et obtenez rapidement leurs apports en calories, protéines, glucides et lipides.

#### 👉 Calculateur avancé basé sur la base CIQUAL
Explorez des milliers d’aliments et affinez votre suivi nutritionnel grâce à la base de données officielle française CIQUAL.

#### 👉 Calendrier pour tracker les performances sportives
Créer tes propres entraînements, ton planning et suis ta progression.

---
""")