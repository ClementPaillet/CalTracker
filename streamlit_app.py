import streamlit as st

from database import init_database
#from pages.training import training_page

init_database()

# Configuration de la page
st.set_page_config(page_title="Mon site", page_icon="🌐", layout="wide")

# ── SIDEBAR PERSONNALISÉ ───────────────────────────────────────────────────
pg = st.navigation({
    "Menu": [
        st.Page(
            "pages/0_accueil.py",
            title="Menu Principal",
            icon="🏠"
        )
    ],
    "Nutrition": [
        st.Page(
            "pages/01_NeededCal.py",
            title="Besoins Caloriques Journaliers",
            icon="🍗"
        ),
        st.Page(
            "pages/02_Simple_CalCounter.py",
            title="Calculateur de Macros - Simple",
            icon="🍽️"
        ),
        st.Page(
            "pages/03_CIQUAL_CalCounter.py",
            title="Calculateur de Macros - Complet",
            icon="🍽️"
        )
    ],
    "Entraînement": [
        #st.Page(
        #    "pages/sport_calendar.py",
        #    title="Calendrier d'entraînements",
        #    icon="📅"
        #),
        st.Page(
            "pages/sport_calendar_copy.py",
            title="Calendrier d'entraînements",
            icon="📅"
        ),
        #st.Page(
        #    "pages/statistiques2.py",
        #    title="Statistiques",
        #    icon="📊"          # optionnel, ajoute un petit icône à droite du label
        #),
        st.Page(
            "pages/statistiques3.py",
            title="Statistiques",
            icon="📊"          # optionnel, ajoute un petit icône à droite du label
        ),
        #st.Page(
        #    "pages/training.py",
        #    title="Base d'entraînements",
        #    icon="🏃"          # optionnel, ajoute un petit icône à droite du label
        #),
        st.Page(
            "pages/training2.py",
            title="Base d'entraînements",
            icon="🏃"          # optionnel, ajoute un petit icône à droite du label
        )
    ],
    "Profils": [
        st.Page(
            "pages/edit_profile.py",
            title="Crée ou édite ton profil",
            icon="🔧"
        )
    ],
}
)




pg.run()