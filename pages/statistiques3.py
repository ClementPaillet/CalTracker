import streamlit as st
import pandas as pd
import sqlite3
import calendar
import altair as alt

from datetime import date, timedelta
from pathlib import Path
import json


# ------------------------------------------------------------------
# 1️⃣  Chargement du fichier JSON (mise en cache)
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)   # cache pour ne charger le fichier qu'une fois
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
    page_title="Statistiques",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# DÉTECTION DES BASES DE DONNÉES
# ============================================================

# Toutes les bases du type training_xxx.db sont détectées
DATABASE_FILES = sorted(
    Path(".").glob("training_*.db")
)

if not DATABASE_FILES:

    st.error(
        "Aucune base de données trouvée.\n\n"
        "Crée au moins une base du type : "
        "`training_user1.db`"
    )

    st.stop()


# Dictionnaire :
# nom affiché -> chemin du fichier
DATABASES = {
    db.stem.replace("training_", ""): str(db)
    for db in DATABASE_FILES
}


# ============================================================
# TITRE
# ============================================================

st.title("📊 Statistiques d'entraînement")

st.markdown(
    "Analyse ton volume, ta répartition, "
    "ton intensité et ta régularité."
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
            st.markdown(f"<h1 style='font-size:48px'>{user_info.get('emoji','🧑')}</h1>", unsafe_allow_html=True)
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
            st.markdown(f"### {full_name}  \n"
                        f"*{nickname}*  \n"
                        f"**Body‑count** : {bodycount}")

            # Bloc description (markdown)
            st.markdown(f"---\n{description}\n---")

# ============================================================
# CONNEXION BASE DE DONNÉES
# ============================================================

def get_connection(db_name):
    return sqlite3.connect(db_name)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

#@st.cache_data
def load_training_data(db_name):

    conn = get_connection(db_name)

    query = """
        SELECT
            calendar.id AS calendar_id,
            calendar.date AS date,
            activities.id AS activity_id,
            activities.name AS name,
            activities.type AS type,
            activities.format AS format,
            activities.duration AS duration,
            activities.description AS description
        FROM calendar
        INNER JOIN activities
            ON calendar.activity_id = activities.id
        ORDER BY calendar.date
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    if not df.empty:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df["duration"] = pd.to_numeric(
            df["duration"],
            errors="coerce"
        ).fillna(0)

    return df


# ============================================================
# CHARGEMENT DES SEGMENTS DE COURSE
# ============================================================

#@st.cache_data
def load_segments(db_name):

    conn = get_connection(db_name)

    query = """
        SELECT
            id,
            activity_id,
            segment_order,
            name,
            duration,
            intensity
        FROM session_segments
        ORDER BY activity_id, segment_order
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    if not df.empty:

        df["duration"] = pd.to_numeric(
            df["duration"],
            errors="coerce"
        ).fillna(0)

    return df


# ============================================================
# CHARGEMENT
# ============================================================

df = load_training_data(DB_NAME)

segments_df = load_segments(DB_NAME)


# ============================================================
# OUTILS
# ============================================================

def format_duration(minutes):

    minutes = int(round(minutes))

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:

        if mins > 0:
            return f"{hours}h {mins:02d}min"

        return f"{hours}h"

    return f"{minutes} min"


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


def get_previous_period(start_date, end_date):

    duration = end_date - start_date

    previous_end = start_date - timedelta(days=1)

    previous_start = (
        previous_end - duration
    )

    return previous_start, previous_end


# ============================================================
# SÉLECTION DE LA PÉRIODE
# ============================================================

st.subheader("📅 Période analysée")

period_type = st.selectbox(
    "Choisir une période",
    [
        "Cette semaine",
        "Ce mois",
        "Cette année",
        "Personnalisée"
    ]
)

today = date.today()


# ------------------------------------------------------------
# Cette semaine
# ------------------------------------------------------------

if period_type == "Cette semaine":

    start_date = (
        today
        - timedelta(days=today.weekday())
    )

    end_date = (
        start_date
        + timedelta(days=6)
    )


# ------------------------------------------------------------
# Ce mois
# ------------------------------------------------------------

elif period_type == "Ce mois":

    start_date = today.replace(
        day=1
    )

    last_day = calendar.monthrange(
        today.year,
        today.month
    )[1]

    end_date = today.replace(
        day=last_day
    )


# ------------------------------------------------------------
# Cette année
# ------------------------------------------------------------

elif period_type == "Cette année":

    start_date = date(
        today.year,
        1,
        1
    )

    end_date = date(
        today.year,
        12,
        31
    )


# ------------------------------------------------------------
# Personnalisée
# ------------------------------------------------------------

else:

    col1, col2 = st.columns(2)

    with col1:

        start_date = st.date_input(
            "Date de début",
            value=today - timedelta(days=30)
        )

    with col2:

        end_date = st.date_input(
            "Date de fin",
            value=today
        )


# ============================================================
# VÉRIFICATION DES DATES
# ============================================================

if start_date > end_date:

    st.error(
        "La date de début doit être antérieure "
        "à la date de fin."
    )

    st.stop()


# ============================================================
# VÉRIFICATION DES DONNÉES
# ============================================================

if df.empty:

    st.info(
        "Aucune séance n'est encore enregistrée "
        "dans le calendrier de cet utilisateur."
    )

    st.stop()


# ============================================================
# FILTRAGE DE LA PÉRIODE
# ============================================================

df_period = df[
    (df["date"].dt.date >= start_date)
    &
    (df["date"].dt.date <= end_date)
].copy()


if df_period.empty:

    st.info(
        "Aucune séance enregistrée pendant "
        "la période sélectionnée."
    )

    st.stop()


# ============================================================
# KPI PRINCIPAUX
# ============================================================

total_sessions = len(df_period)

total_duration = (
    df_period["duration"].sum()
)

average_duration = (
    total_duration / total_sessions
)

number_of_types = (
    df_period["type"].nunique()
)


st.divider()

st.subheader("🏋️ Vue d'ensemble")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Séances",
        total_sessions
    )


with col2:

    st.metric(
        "Temps total",
        format_duration(total_duration)
    )


with col3:

    st.metric(
        "Durée moyenne",
        format_duration(average_duration)
    )


with col4:

    st.metric(
        "Types d'activités",
        number_of_types
    )


# ============================================================
# COMPARAISON AVEC LA PÉRIODE PRÉCÉDENTE
# ============================================================

previous_start, previous_end = (
    get_previous_period(
        start_date,
        end_date
    )
)


df_previous = df[
    (df["date"].dt.date >= previous_start)
    &
    (df["date"].dt.date <= previous_end)
].copy()


if not df_previous.empty:

    previous_sessions = len(
        df_previous
    )

    previous_duration = (
        df_previous["duration"].sum()
    )

    st.markdown(
        "### 📈 Comparaison avec la période précédente"
    )

    col1, col2 = st.columns(2)


    with col1:

        if previous_sessions > 0:

            session_change = (
                (
                    total_sessions
                    - previous_sessions
                )
                / previous_sessions
                * 100
            )

            st.metric(
                "Nombre de séances",
                total_sessions,
                f"{session_change:+.1f}%"
            )

        else:

            st.metric(
                "Nombre de séances",
                total_sessions
            )


    with col2:

        if previous_duration > 0:

            duration_change = (
                (
                    total_duration
                    - previous_duration
                )
                / previous_duration
                * 100
            )

            st.metric(
                "Temps d'entraînement",
                format_duration(
                    total_duration
                ),
                f"{duration_change:+.1f}%"
            )

        else:

            st.metric(
                "Temps d'entraînement",
                format_duration(
                    total_duration
                )
            )


# ============================================================
# RÉPARTITION PAR SPORT
# ============================================================

st.divider()

st.subheader(
    "📊 Répartition des entraînements"
)

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Nombre de séances
# ------------------------------------------------------------

sessions_by_type = (
    df_period
    .groupby("type")
    .size()
    .sort_values(
        ascending=False
    )
)


with col1:

    st.markdown(
        "### Nombre de séances"
    )

    sessions_chart = (
        sessions_by_type
        .rename("Séances")
    )

    st.bar_chart(
        sessions_chart,
        width="stretch"
    )


# ------------------------------------------------------------
# Temps d'entraînement
# ------------------------------------------------------------

duration_by_type = (
    df_period
    .groupby("type")["duration"]
    .sum()
    .sort_values(
        ascending=False
    )
)


with col2:

    st.markdown(
        "### Temps d'entraînement"
    )

    duration_chart = (
        duration_by_type
        .rename("Minutes")
    )

    st.bar_chart(
        duration_chart,
        width="stretch"
    )


# ============================================================
# TABLEAU RÉCAPITULATIF
# ============================================================

st.markdown(
    "### 📋 Synthèse par activité"
)


summary = (
    df_period
    .groupby("type")
    .agg(
        Séances=("type", "size"),
        Minutes=("duration", "sum")
    )
    .reset_index()
)


summary["Part du volume"] = (
    summary["Minutes"]
    / summary["Minutes"].sum()
    * 100
)


summary["Type"] = (
    summary["type"]
    .apply(
        lambda x:
        f"{activity_icon(x)} {x}"
    )
)


summary["Temps"] = (
    summary["Minutes"]
    .apply(format_duration)
)


summary["Part du volume"] = (
    summary["Part du volume"]
    .round(1)
    .astype(str)
    + " %"
)


summary = summary[
    [
        "Type",
        "Séances",
        "Temps",
        "Part du volume"
    ]
]


st.dataframe(
    summary,
    hide_index=True,
    width="stretch"
)


# ============================================================
# ANALYSE COURSE
# ============================================================

running = df_period[
    df_period["type"] == "Course"
].copy()


if not running.empty:

    st.divider()

    st.subheader(
        "🏃 Analyse de la course"
    )


    running_sessions = len(
        running
    )

    running_duration = (
        running["duration"].sum()
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Séances de course",
            running_sessions
        )


    with col2:

        st.metric(
            "Temps total de course",
            format_duration(
                running_duration
            )
        )


    # --------------------------------------------------------
    # Segments correspondant aux courses
    # --------------------------------------------------------

    running_activity_ids = (
        running["activity_id"]
        .unique()
    )


    running_segments = segments_df[
        segments_df["activity_id"]
        .isin(
            running_activity_ids
        )
    ].copy()


    if not running_segments.empty:

        # ----------------------------------------------------
        # Regroupement par intensité
        # ----------------------------------------------------

        intensity_duration = (
            running_segments
            .groupby("intensity")["duration"]
            .sum()
        )


        desired_order = [
            "Z2",
            "Seuil",
            "Haute intensité",
            "Récupération"
        ]


        intensity_duration = (
            intensity_duration
            .reindex(
                desired_order,
                fill_value=0
            )
        )


        # ----------------------------------------------------
        # Graphique
        # ----------------------------------------------------

        st.markdown(
            "### 🔥 Répartition des intensités"
        )


        intensity_chart = (
            intensity_duration
            .rename("Minutes")
        )


        st.bar_chart(
            intensity_chart,
            width="stretch"
        )


        # ----------------------------------------------------
        # KPIs zones
        # ----------------------------------------------------

        zone_total = (
            intensity_duration.sum()
        )


        cols = st.columns(
            len(desired_order)
        )


        for i, zone in enumerate(
            desired_order
        ):

            duration = (
                intensity_duration[
                    zone
                ]
            )


            percentage = (
                duration
                / zone_total
                * 100
                if zone_total > 0
                else 0
            )


            with cols[i]:

                st.metric(
                    zone,
                    format_duration(
                        duration
                    ),
                    f"{percentage:.1f}%"
                )


        # ----------------------------------------------------
        # Donut
        # ----------------------------------------------------

        pie_df = (
            intensity_duration[
                intensity_duration > 0
            ]
            .to_frame("Minutes")
            .reset_index()
            .rename(
                columns={
                    "index": "intensity"
                }
            )
        )


        st.markdown(
            "### 🥧 Répartition relative"
        )


        if not pie_df.empty:

            pie_df["percent"] = (
                pie_df["Minutes"]
                / pie_df["Minutes"].sum()
            ) * 100


            chart = (
                alt.Chart(pie_df)
                .mark_arc(
                    innerRadius=50
                )
                .encode(

                    angle=alt.Angle(
                        "Minutes:Q",
                        sort=None
                    ),

                    color=alt.Color(
                        "intensity:N",
                        title="Intensité"
                    ),

                    tooltip=[
                        "intensity:N",
                        "Minutes:Q",
                        alt.Tooltip(
                            "percent:Q",
                            format=".1f",
                            title="%"
                        )
                    ]
                )
                .properties(
                    width=400,
                    height=400,
                    title=(
                        "Répartition des minutes "
                        "par intensité"
                    )
                )
            )


            st.altair_chart(
                chart,
                use_container_width=True
            )


    else:

        st.info(
            "Aucun segment de course n'est "
            "disponible pour cette période."
        )


# ============================================================
# ÉVOLUTION HEBDOMADAIRE
# ============================================================

st.divider()

st.subheader(
    "📈 Évolution hebdomadaire"
)


df_period["Semaine"] = (
    df_period["date"]
    .dt.to_period("W-SUN")
    .apply(
        lambda x:
        x.start_time
    )
)


weekly = (
    df_period
    .groupby("Semaine")
    .agg(
        Séances=("type", "size"),
        Minutes=("duration", "sum")
    )
)


col1, col2 = st.columns(2)


with col1:

    st.markdown(
        "### ⏱️ Temps d'entraînement"
    )

    st.line_chart(
        weekly["Minutes"],
        width="stretch"
    )


with col2:

    st.markdown(
        "### 🏋️ Nombre de séances"
    )

    st.bar_chart(
        weekly["Séances"],
        width="stretch"
    )


# ============================================================
# VOLUME DE COURSE PAR SEMAINE
# ============================================================

if not running.empty:

    running["Semaine"] = (
        running["date"]
        .dt.to_period("W-SUN")
        .apply(
            lambda x:
            x.start_time
        )
    )


    running_weekly = (
        running
        .groupby("Semaine")["duration"]
        .sum()
    )


    st.markdown(
        "### 🏃 Volume de course par semaine"
    )


    st.line_chart(
        running_weekly,
        width="stretch"
    )


# ============================================================
# RÉGULARITÉ
# ============================================================

st.divider()

st.subheader(
    "📅 Régularité"
)


weeks_with_training = (
    df_period["Semaine"]
    .nunique()
)


total_days = (
    end_date - start_date
).days + 1


total_weeks = (
    (total_days - 1) // 7
) + 1


sessions_per_week = (
    total_sessions
    / weeks_with_training
    if weeks_with_training > 0
    else 0
)


hours_per_week = (
    total_duration
    / 60
    / weeks_with_training
    if weeks_with_training > 0
    else 0
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Semaines actives",
        f"{weeks_with_training} / {total_weeks}"
    )


with col2:

    st.metric(
        "Séances / semaine",
        f"{sessions_per_week:.1f}"
    )


with col3:

    st.metric(
        "Heures / semaine",
        f"{hours_per_week:.1f} h"
    )


# ============================================================
# ACTIVITÉ JOUR PAR JOUR
# ============================================================

st.markdown(
    "### 📆 Volume jour par jour"
)


daily = (
    df_period
    .groupby(
        df_period["date"].dt.date
    )["duration"]
    .sum()
)


all_dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)


daily = daily.reindex(
    all_dates.date,
    fill_value=0
)


daily = daily.rename(
    "Minutes"
)


st.bar_chart(
    daily,
    width="stretch"
)


# ============================================================
# DÉTAIL DES SÉANCES
# ============================================================

st.divider()

st.subheader(
    "📋 Détail des séances"
)


display_df = df_period.copy()


display_df["Date"] = (
    display_df["date"]
    .dt.strftime("%d/%m/%Y")
)


display_df["Type"] = (
    display_df["type"]
    .apply(
        lambda x:
        f"{activity_icon(x)} {x}"
    )
)


display_df["Durée"] = (
    display_df["duration"]
    .apply(
        format_duration
    )
)


display_df = display_df[
    [
        "Date",
        "Type",
        "name",
        "format",
        "Durée",
        "description"
    ]
]


display_df.columns = [
    "Date",
    "Type",
    "Séance",
    "Format",
    "Durée",
    "Description"
]


display_df = display_df.sort_values(
    "Date",
    ascending=False
)


st.dataframe(
    display_df,
    hide_index=True,
    width="stretch"
)