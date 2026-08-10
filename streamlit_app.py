import streamlit as st

from database import init_database
#from pages.training import training_page

init_database()

# Configuration de la page
st.set_page_config(page_title="Accueil - Mon site de nutrition", page_icon="🥦", layout="wide")

# Titre principal
st.title("🥗 Bienvenue sur votre assistant nutrition et sport 🏃")

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
