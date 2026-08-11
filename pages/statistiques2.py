import streamlit as st
import pandas as pd
import sqlite3
import calendar
import altair as alt

from datetime import date, timedelta

# ============================================================
# CONFIGURATION
# ============================================================

DB_NAME = "training.db"

st.set_page_config(
    page_title="Statistiques",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CONNEXION BASE DE DONNÉES
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def load_training_data():

    conn = get_connection()

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

@st.cache_data
def load_segments():

    conn = get_connection()

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
# CHARGEMENT
# ============================================================

df = load_training_data()

segments_df = load_segments()


# ============================================================
# TITRE
# ============================================================

st.title("📊 Statistiques d'entraînement")

st.markdown(
    "Analyse ton volume, ta répartition, "
    "ton intensité et ta régularité."
)


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


if start_date > end_date:

    st.error(
        "La date de début doit être antérieure "
        "à la date de fin."
    )

    st.stop()


# ============================================================
# FILTRAGE DE LA PÉRIODE
# ============================================================

if df.empty:

    st.info(
        "Aucune séance n'est encore enregistrée "
        "dans ton calendrier."
    )

    st.stop()


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


        # Ordre souhaité
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
        # Donut via dataframe pour graphique
        # ----------------------------------------------------

        #st.markdown(
        #    "### 🥧 Répartition relative"
        #)
#
#
        #pie_data = (
        #    intensity_duration[
        #        intensity_duration > 0
        #    ]
        #    .to_frame("Minutes")
        #)
#
        #if not pie_data.empty:
#
        #    st.bar_chart(
        #        pie_data,
        #        width="stretch"
        #    )

        # ----------------------------------------------------
        # Donut via dataframe pour graphique
        # ----------------------------------------------------
        # ----------------------------------------------------
        # 2️⃣  Préparer le DataFrame
        # ----------------------------------------------------
        pie_df = (
            intensity_duration[intensity_duration > 0]   # garder >0
            .to_frame("Minutes")                         # DataFrame avec colonne Minutes
            .reset_index()                               # mettre l'index (intensity) en colonne
            .rename(columns={"index": "intensity"})      # nom explicite
        )

        # ----------------------------------------------------
        # 3️⃣  Titre Streamlit
        # ----------------------------------------------------
        st.markdown("### 🥧 Répartition relative")

        # ----------------------------------------------------
        # 4️⃣  Vérifier qu’on a des données
        # ----------------------------------------------------
        if not pie_df.empty:

            # ------------------------------------------------
            # 5️⃣  Créer le camembert (donut) Altair
            # ------------------------------------------------
            # 5.1 – Calculer le pourcentage (optionnel, pour affichage)
            pie_df["percent"] = (
                pie_df["Minutes"] / pie_df["Minutes"].sum()
            ) * 100

            # 5.2 – Chart
            chart = (
                alt.Chart(pie_df)
                .mark_arc(innerRadius=50)                # <‑‑ 0 → vrai camembert, >0 → donut
                .encode(
                    # Taille de chaque part
                    angle=alt.Angle("Minutes:Q", sort=None),
                    # Couleur = intensité (catégorique)
                    color=alt.Color(
                        "intensity:N",
                        title="Intensité",
                    ),
                    # Etiquette texte (pourcentage + libellé)
                    tooltip=[
                        "intensity:N",
                        "Minutes:Q",
                        alt.Tooltip("percent:Q", format=".1f", title="%")
                    ]
                )
                # Optionnel : légende + titre
                .properties(
                    width=400,
                    height=400,
                    title="Répartition des minutes par intensité"
                )
            )

            # ------------------------------------------------
            # 6️⃣  Afficher le graphique dans Streamlit
            # ------------------------------------------------
            st.altair_chart(chart, use_container_width=True)

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