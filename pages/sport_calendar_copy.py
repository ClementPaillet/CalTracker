import streamlit as st
import sqlite3
import calendar
from datetime import date
from pathlib import Path
import json


# ------------------------------------------------------------------
# 1️⃣  Chargement du fichier JSON (mise en cache)
# ------------------------------------------------------------------
#@st.cache_data(show_spinner=False)   # cache pour ne charger le fichier qu'une fois
def load_user_data() -> dict:
    """Lit le fichier users.json et renvoie le dictionnaire complet."""
    file_path = Path(__file__).parent.parent / "users.json"   # à la racine du projet
    if not file_path.is_file():
        st.error(f"❌ Le fichier {file_path} est introuvable.")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

USER_DB = load_user_data()   # dictionnaire global

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Calendrier d'entraînements",
    page_icon="📅",
    layout="wide"
)


# ============================================================
# DÉTECTION DES BASES DE DONNÉES
# ============================================================

DATABASE_FILES = sorted(
    Path(".").glob("training_*.db")
)

if not DATABASE_FILES:

    st.error(
        "Aucune base de données trouvée.\n\n"
        "Crée au moins une base du type "
        "`training_user1.db`."
    )

    st.stop()


# ============================================================
# CRÉATION DU DICTIONNAIRE DES UTILISATEURS
# ============================================================

# Exemple :
#
# training_clement.db -> Clement
# training_antoine.db -> Antoine
#
DATABASES = {
    db.stem.replace("training_", ""): str(db)
    for db in DATABASE_FILES
}


# ============================================================
# SÉLECTION DE LA BASE
# ============================================================

st.title("📅 Calendrier d'entraînement")

st.markdown(
    "Planifie tes séances à partir de ta banque d'activités."
)


## ============================================================
## SÉLECTION DE LA BASE
## ============================================================
with st.container(border=True):                 # <‑ contexte « container » (facultatif)
    # ── Votre code d'origine ───────────────────────
    selected_user = st.selectbox(
        "👤 Utilisateur",
        options=list(DATABASES.keys()),
        placeholder="Choisissez votre profil"
    )

    DB_NAME = DATABASES[selected_user]

    st.caption(f"Base utilisée : `{DB_NAME}`")
    # ────────────────────────────────────────────────

    # ------------------------------------------------------------------
    # 3️⃣  Récupération et affichage de la fiche utilisateur
    # ------------------------------------------------------------------
    # On enlève le suffixe « .db »
    stem = Path(DB_NAME).stem
    # On retire le pré‑fixe « training_ » 
    key = stem.removeprefix("training_")

    user_info = USER_DB.get(key)

    if user_info is None:
        st.warning("⚠️ Aucune information disponible pour cet utilisateur.")
    else:
        # Mise en forme « beau » avec colonnes
        col1, col2 = st.columns([1, 2], gap="small")

        # Colonne 1 : Photo / Emoji + quelques stats rapides
        with col1:
            st.metric("Âge", f"{user_info['age']} ans")
            st.metric("Taille", f"{user_info['taille_cm']} cm")
            st.metric("Poids", f"{user_info['poids_kg']} kg")
            st.metric("Sexe", user_info['sexe'])

        # Colonne 2 : Texte détaillé
        with col2:
            full_name = f"{user_info['prenom']} {user_info['nom']}"
            nickname  = user_info.get('surnom')
            bodycount = user_info.get('bodycount')
            description = user_info.get('description', "")

            # Titre + sous‑titre
            st.markdown(f"### {full_name}  \n")
            st.markdown(f"<h1 style='font-size:48px'>{user_info.get('emoji','🧑')}</h1>", unsafe_allow_html=True)
            st.markdown(f"**Surnom** : *{nickname}*  \n"
                        f"**Body‑count** : {bodycount}")

            # Bloc description (markdown)
            st.markdown(f"---\n{description}\n---")


# ============================================================
# BASE DE DONNÉES
# ============================================================

def get_connection():

    return sqlite3.connect(DB_NAME)


# ============================================================
# RÉCUPÉRATION DES ACTIVITÉS
# ============================================================

def get_activities():
    """
    Récupère toutes les activités disponibles
    dans la banque d'activités.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            type,
            format,
            duration,
            description
        FROM activities
        ORDER BY name
    """)

    activities = cursor.fetchall()

    conn.close()

    return activities


# ============================================================
# RÉCUPÉRATION D'UNE ACTIVITÉ
# ============================================================

def get_activity(activity_id):
    """
    Récupère une activité précise.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            type,
            format,
            duration,
            description
        FROM activities
        WHERE id = ?
    """, (activity_id,))

    activity = cursor.fetchone()

    conn.close()

    return activity


# ============================================================
# RÉCUPÉRATION DU CALENDRIER
# ============================================================
def get_calendar_activities(year, month):
    """
    Récupère toutes les activités programmées
    pour un mois donné.
    """

    conn = get_connection()
    cursor = conn.cursor()

    start_date = f"{year:04d}-{month:02d}-01"

    last_day = calendar.monthrange(year, month)[1]

    end_date = (
        f"{year:04d}-{month:02d}-{last_day:02d}"
    )

    cursor.execute("""
        SELECT
            calendar.id,
            calendar.date,
            activities.id,
            activities.name,
            activities.type,
            activities.format,
            activities.duration
        FROM calendar
        JOIN activities
            ON calendar.activity_id = activities.id
        WHERE calendar.date BETWEEN ? AND ?
        ORDER BY calendar.date
    """, (start_date, end_date))

    activities = cursor.fetchall()

    conn.close()

    return activities


# ============================================================
# AJOUT AU CALENDRIER
# ============================================================

def add_to_calendar(
    activity_id,
    selected_date
):
    """
    Ajoute une activité à une date
    dans la base actuellement sélectionnée.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO calendar
        (date, activity_id)
        VALUES (?, ?)
    """, (
        selected_date,
        activity_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# SUPPRESSION DU CALENDRIER
# ============================================================
def delete_from_calendar(calendar_id):
    """
    Supprime une activité du calendrier.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM calendar
        WHERE id = ?
    """, (calendar_id,))

    conn.commit()
    conn.close()

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def activity_icon(activity_type):

    icons = {
        "Course": "🏃",
        "Musculation": "🏋️",
        "Vélo": "🚴",
        "Natation": "🏊",
        "Hyrox": "🔥",
        "Randonnée": "🥾",
        "Autre": "⚡"
    }

    return icons.get(
        activity_type,
        "⚡"
    )


def format_duration(minutes):

    if minutes is None:
        return ""

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:

        if mins > 0:
            return f"{hours}h{mins:02d}"

        return f"{hours}h"

    return f"{minutes} min"


# -----------------------------------------------------------------
#  Helper : one activity cell with delete button inside the box
# -----------------------------------------------------------------
def activity_cell(activity: dict) -> None:
    """
    Render an activity inside its coloured box and put the delete
    button at the top‑right corner of that box.
    """
    icon = activity_icon(activity["type"])
    duration = format_duration(activity["duration"])

    # ---- outer container (the whole box) ----
    container = st.container()
    with container:
        # ---- Row 1 : delete button (top‑right) ----
        # we create two columns; the right one is tiny and holds the button
        _, btn_col = st.columns([0.9, 0.1])
        with btn_col:
            if st.button("✕",
                       key=f"delete_{activity['calendar_id']}",
                       help="Supprimer cette séance"):
                delete_from_calendar(activity["calendar_id"])
                st.rerun()

        # ---- Row 2 : activity description (still inside the same box) ----
        st.markdown(
            f"""
            <div style="
                background-color:#f0f2f6;
                border-radius:7px;
                padding:5px;
                margin-top:5px;
                font-size:13px;
                ">
                <b>{icon} {activity["name"]}</b><br>
                {duration}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# AFFICHAGE D'UNE ACTIVITÉ
# ============================================================

def render_activity_line(
    activity: dict
) -> None:

    icon = activity_icon(
        activity["type"]
    )

    duration = format_duration(
        activity["duration"]
    )

    txt = (
        f"**{icon} {activity['name']}** "
        f"{duration}"
    )

    container = st.container()

    with container:

        col_text, col_btn = st.columns(
            [0.9, 0.1]
        )

        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------

        with col_text:

            st.markdown(
                f"""
                <div style="
                    background-color:#f0f2f6;
                    border-radius:7px;
                    padding:5px;
                    font-size:13px;
                ">
                    {txt}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------
        # Bouton suppression
        # ----------------------------------------------------

        with col_btn:

            if st.button(
                "✕",
                key=f"delete_{activity['calendar_id']}",
                help="Supprimer cette séance"
            ):

                delete_from_calendar(
                    activity["calendar_id"]
                )

                st.rerun()


# ============================================================
# INITIALISATION SESSION STATE
# ============================================================

if "calendar_year" not in st.session_state:

    today = date.today()

    st.session_state.calendar_year = today.year
    st.session_state.calendar_month = today.month


if "selected_date" not in st.session_state:

    st.session_state.selected_date = None


# ============================================================
# NAVIGATION DU MOIS
# ============================================================

col_previous, col_title, col_next = st.columns(
    [1, 4, 1]
)


# ============================================================
# MOIS PRÉCÉDENT
# ============================================================

with col_previous:

    if st.button(
        "⬅️ Mois précédent",
        width="stretch"
    ):

        if st.session_state.calendar_month == 1:

            st.session_state.calendar_month = 12
            st.session_state.calendar_year -= 1

        else:

            st.session_state.calendar_month -= 1

        st.rerun()


# ============================================================
# TITRE DU MOIS
# ============================================================

with col_title:

    month_name = calendar.month_name[
        st.session_state.calendar_month
    ]

    month_name = month_name.capitalize()

    st.markdown(
        f"""
        <h2 style='text-align:center;'>
            {month_name} {st.session_state.calendar_year}
        </h2>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MOIS SUIVANT
# ============================================================

with col_next:

    if st.button(
        "Mois suivant ➡️",
        width="stretch"
    ):

        if st.session_state.calendar_month == 12:

            st.session_state.calendar_month = 1
            st.session_state.calendar_year += 1

        else:

            st.session_state.calendar_month += 1

        st.rerun()


# ============================================================
# ACTIVITÉS DU MOIS
# ============================================================

calendar_activities = get_calendar_activities(
    st.session_state.calendar_year,
    st.session_state.calendar_month
)

# Dictionnaire :
#
# {
#     "2026-08-10": [
#         activité,
#         activité
#     ]
# }

activities_by_date = {}

for activity in calendar_activities:

    (
        calendar_id,
        activity_date,
        activity_id,
        name,
        activity_type,
        activity_format,
        duration
    ) = activity

    if activity_date not in activities_by_date:

        activities_by_date[activity_date] = []

    activities_by_date[activity_date].append(
        {
            "calendar_id": calendar_id,
            "activity_id": activity_id,
            "name": name,
            "type": activity_type,
            "format": activity_format,
            "duration": duration
        }
    )

st.divider()

# ============================================================
# ORGANISATION PAR DATE
# ============================================================
days = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche"
]


# ============================================================
# EN-TÊTE DES JOURS
# ============================================================

header = st.columns(7)


for i, day in enumerate(days):

    with header[i]:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-weight:bold;
            ">
                {day}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# GÉNÉRATION DU CALENDRIER
# ============================================================

cal = calendar.Calendar(
    firstweekday=0
)


weeks = cal.monthdayscalendar(
    st.session_state.calendar_year,
    st.session_state.calendar_month
)


for week in weeks:

    columns = st.columns(7)


    for day_index, day_number in enumerate(week):

        with columns[day_index]:

            # ------------------------------------------------
            # Jour inexistant
            # ------------------------------------------------

            if day_number == 0:

                st.markdown(
                    "<div style='height:180px;'></div>",
                    unsafe_allow_html=True
                )

                continue


            current_date = date(
                st.session_state.calendar_year,
                st.session_state.calendar_month,
                day_number
            )


            current_date_str = (
                current_date.isoformat()
            )


            today = date.today()

            is_today = (
                current_date == today
            )


            # ------------------------------------------------
            # Affichage du jour
            # ------------------------------------------------
            if is_today:

                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ff4b4b;
                        border-radius: 10px;
                        padding: 8px;
                        min-height: 20px;
                    ">
                    <b>🔴 {day_number}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #cccccc;
                        border-radius: 10px;
                        padding: 8px;
                        min-height: 20px;
                    ">
                    <b>{day_number}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # ------------------------------------------------
            # Activités du jour
            # ------------------------------------------------

            day_activities = activities_by_date.get(
                current_date_str,
                []
            )


            for activity in day_activities:

                render_activity_line(
                    activity
                )


            # ------------------------------------------------
            # Bouton ajouter
            # ------------------------------------------------
            if st.button(
                "＋ Ajouter",
                key=f"add_{current_date_str}",
                width="stretch"
            ):

                st.session_state.selected_date = (
                    current_date_str
                )

                st.rerun()

# ============================================================
# AJOUT D'UNE ACTIVITÉ
# ============================================================

if st.session_state.selected_date:

    st.divider()

    selected_date = date.fromisoformat(
        st.session_state.selected_date
    )

    st.subheader(
        f"➕ Ajouter une séance — "
        f"{selected_date.strftime('%d/%m/%Y')}"
    )

    activities = get_activities()

    if not activities:

        st.warning(
            "Ta banque d'activités est vide. "
            "Crée d'abord une activité."
        )

    else:

        # ----------------------------------------------------
        # Préparation des options
        # ----------------------------------------------------

        activity_options = {}

        for activity in activities:

            (
                activity_id,
                name,
                activity_type,
                activity_format,
                duration,
                description
            ) = activity

            label = (
                f"{activity_icon(activity_type)} "
                f"{name} — "
                f"{format_duration(duration)}"
            )

            activity_options[label] = activity_id


        selected_label = st.selectbox(
            "Choisis une activité",
            list(activity_options.keys())
        )

        selected_activity_id = activity_options[
            selected_label
        ]

        selected_activity = get_activity(
            selected_activity_id
        )

        if selected_activity:

            (
                activity_id,
                name,
                activity_type,
                activity_format,
                duration,
                description
            ) = selected_activity

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Type",
                    activity_type
                )

            with col2:

                st.metric(
                    "Format",
                    activity_format
                )

            with col3:

                st.metric(
                    "Durée",
                    format_duration(duration)
                )

            if description:

                st.info(description)


        # ----------------------------------------------------
        # Aperçu activité
        # ----------------------------------------------------
        # ----------------------------------------------------
        # Boutons
        # ----------------------------------------------------

        col_add, col_cancel = st.columns(2)


        with col_add:

            if st.button(
                "✅ Ajouter au calendrier",
                type="primary",
                width="stretch"
            ):

                add_to_calendar(
                    selected_activity_id,
                    st.session_state.selected_date
                )


                st.success(
                    "Séance ajoutée au calendrier !"
                )


                st.session_state.selected_date = None


                st.rerun()


        with col_cancel:

            if st.button(
                "❌ Annuler",
                width="stretch"
            ):

                st.session_state.selected_date = None

                st.rerun()