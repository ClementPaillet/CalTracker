import streamlit as st
import pandas as pd
import sqlite3
import calendar

from datetime import date, datetime, timedelta


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
# BASE DE DONNÉES
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


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
            activities.duration AS duration
        FROM calendar
        JOIN activities
            ON calendar.activity_id = activities.id
        ORDER BY calendar.date
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    if not df.empty:

        df["date"] = pd.to_datetime(df["date"])

        df["duration"] = pd.to_numeric(
            df["duration"],
            errors="coerce"
        ).fillna(0)

    return df


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def format_duration(minutes):

    minutes = int(round(minutes))

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:

        if mins > 0:
            return f"{hours}h{mins:02d}"

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


# ============================================================
# TITRE
# ============================================================

st.title("📊 Statistiques d'entraînement")

st.markdown(
    "Analyse ton volume, ta répartition et l'évolution "
    "de ton entraînement."
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


if period_type == "Cette semaine":

    # Lundi de la semaine
    start_date = today - timedelta(
        days=today.weekday()
    )

    end_date = start_date + timedelta(days=6)


elif period_type == "Ce mois":

    start_date = today.replace(day=1)

    last_day = calendar.monthrange(
        today.year,
        today.month
    )[1]

    end_date = today.replace(
        day=last_day
    )


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
# FILTRAGE
# ============================================================

df_period = df[
    (df["date"].dt.date >= start_date)
    &
    (df["date"].dt.date <= end_date)
].copy()


# ============================================================
# MESSAGE SI AUCUNE DONNÉE
# ============================================================

if df_period.empty:

    st.info(
        "Aucune séance enregistrée pendant cette période."
    )

    st.stop()


# ============================================================
# KPI PRINCIPAUX
# ============================================================

total_sessions = len(df_period)

total_duration = df_period["duration"].sum()

average_duration = (
    total_duration / total_sessions
    if total_sessions > 0
    else 0
)

number_of_sports = df_period["type"].nunique()


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
        number_of_sports
    )


# ============================================================
# COMPARAISON PÉRIODE PRÉCÉDENTE
# ============================================================

previous_start, previous_end = get_previous_period(
    start_date,
    end_date
)


df_previous = df[
    (df["date"].dt.date >= previous_start)
    &
    (df["date"].dt.date <= previous_end)
].copy()


if not df_previous.empty:

    previous_sessions = len(df_previous)

    previous_duration = df_previous["duration"].sum()

    session_delta = (
        (
            total_sessions
            - previous_sessions
        )
        / previous_sessions
        * 100
        if previous_sessions > 0
        else None
    )

    duration_delta = (
        (
            total_duration
            - previous_duration
        )
        / previous_duration
        * 100
        if previous_duration > 0
        else None
    )

    st.caption(
        f"Comparaison avec la période précédente : "
        f"{previous_start.strftime('%d/%m/%Y')} → "
        f"{previous_end.strftime('%d/%m/%Y')}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if session_delta is not None:

            st.metric(
                "Évolution du nombre de séances",
                total_sessions,
                f"{session_delta:+.1f}%"
            )

    with col2:

        if duration_delta is not None:

            st.metric(
                "Évolution du temps d'entraînement",
                format_duration(total_duration),
                f"{duration_delta:+.1f}%"
            )


# ============================================================
# RÉPARTITION PAR TYPE
# ============================================================

st.divider()

st.subheader("📊 Répartition des entraînements")


col1, col2 = st.columns(2)


# ------------------------------------------------------------
# NOMBRE DE SÉANCES
# ------------------------------------------------------------

sessions_by_type = (
    df_period
    .groupby("type")
    .size()
    .sort_values(ascending=False)
)


with col1:

    st.markdown("### Nombre de séances")

    st.bar_chart(
        sessions_by_type,
        use_container_width=True
    )


# ------------------------------------------------------------
# TEMPS
# ------------------------------------------------------------

duration_by_type = (
    df_period
    .groupby("type")["duration"]
    .sum()
    .sort_values(ascending=False)
)


with col2:

    st.markdown("### Temps d'entraînement")

    st.bar_chart(
        duration_by_type,
        use_container_width=True
    )


# ============================================================
# TABLEAU RÉCAPITULATIF PAR SPORT
# ============================================================

summary = (
    df_period
    .groupby("type")
    .agg(
        Séances=("type", "size"),
        Temps=("duration", "sum")
    )
    .reset_index()
)


summary["Part du volume"] = (
    summary["Temps"]
    / summary["Temps"].sum()
    * 100
)


summary["Temps"] = summary["Temps"].apply(
    format_duration
)


summary["Part du volume"] = (
    summary["Part du volume"]
    .round(1)
    .astype(str)
    + " %"
)


summary["Type"] = summary["type"].apply(
    lambda x:
    f"{activity_icon(x)} {x}"
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
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ANALYSE COURSE
# ============================================================

running = df_period[
    df_period["type"].str.lower() == "course"
].copy()


if not running.empty:

    st.divider()

    st.subheader("🏃 Analyse de la course")

    running_sessions = len(running)

    running_duration = running["duration"].sum()


    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Séances de course",
            running_sessions
        )

    with col2:

        st.metric(
            "Temps total de course",
            format_duration(running_duration)
        )


    # ========================================================
    # RÉCUPÉRATION DES SEGMENTS
    # ========================================================

    conn = get_connection()

    activity_ids = tuple(
        running["activity_id"]
        .tolist()
    )


    if len(activity_ids) == 1:

        query = """
            SELECT
                activity_id,
                segment_type,
                duration
            FROM session_segments
            WHERE activity_id = ?
        """

        segments = pd.read_sql_query(
            query,
            conn,
            params=(activity_ids[0],)
        )

    else:

        placeholders = ",".join(
            ["?"] * len(activity_ids)
        )

        query = f"""
            SELECT
                activity_id,
                segment_type,
                duration
            FROM session_segments
            WHERE activity_id IN ({placeholders})
        """

        segments = pd.read_sql_query(
            query,
            conn,
            params=activity_ids
        )


    conn.close()


    if not segments.empty:

        segments["duration"] = pd.to_numeric(
            segments["duration"],
            errors="coerce"
        ).fillna(0)


        # ----------------------------------------------------
        # NORMALISATION DES ZONES
        # ----------------------------------------------------

        def normalize_zone(value):

            if value is None:
                return "Autre"

            value = str(value).lower()

            if "z2" in value:

                return "Z2"

            if "seuil" in value:

                return "Seuil"

            if (
                "haute" in value
                or "intens" in value
                or "vo2" in value
            ):

                return "Haute intensité"

            return "Autre"


        segments["Zone"] = (
            segments["segment_type"]
            .apply(normalize_zone)
        )


        zone_duration = (
            segments
            .groupby("Zone")["duration"]
            .sum()
        )


        # ----------------------------------------------------
        # GRAPHIQUE
        # ----------------------------------------------------

        st.markdown(
            "### Répartition de l'intensité"
        )

        st.bar_chart(
            zone_duration,
            use_container_width=True
        )


        # ----------------------------------------------------
        # POURCENTAGES
        # ----------------------------------------------------

        total_zone_duration = (
            zone_duration.sum()
        )


        if total_zone_duration > 0:

            cols = st.columns(
                len(zone_duration)
            )

            for i, (zone, duration) in enumerate(
                zone_duration.items()
            ):

                percentage = (
                    duration
                    / total_zone_duration
                    * 100
                )

                with cols[i]:

                    st.metric(
                        zone,
                        format_duration(duration),
                        f"{percentage:.1f}%"
                    )


    else:

        st.info(
            "Aucun segment d'intensité n'est disponible "
            "pour les séances de course de cette période."
        )


# ============================================================
# ÉVOLUTION HEBDOMADAIRE
# ============================================================

st.divider()

st.subheader("📈 Évolution hebdomadaire")


df_period["Semaine"] = (
    df_period["date"]
    .dt.to_period("W-MON")
    .apply(lambda x: x.start_time)
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

    st.markdown("### Temps d'entraînement")

    st.line_chart(
        weekly["Minutes"],
        use_container_width=True
    )


with col2:

    st.markdown("### Nombre de séances")

    st.bar_chart(
        weekly["Séances"],
        use_container_width=True
    )


# ============================================================
# ÉVOLUTION DE LA COURSE
# ============================================================

if not running.empty:

    running["Semaine"] = (
        running["date"]
        .dt.to_period("W-MON")
        .apply(lambda x: x.start_time)
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
        use_container_width=True
    )


# ============================================================
# RÉGULARITÉ
# ============================================================

st.divider()

st.subheader("📅 Régularité")


# Nombre de semaines avec au moins une séance

weeks_with_training = (
    df_period["Semaine"]
    .nunique()
)


total_weeks = (
    (
        pd.Timestamp(end_date)
        - pd.Timestamp(start_date)
    ).days
    // 7
) + 1


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Semaines actives",
        f"{weeks_with_training}/{total_weeks}"
    )


with col2:

    sessions_per_week = (
        total_sessions
        / weeks_with_training
        if weeks_with_training > 0
        else 0
    )

    st.metric(
        "Séances / semaine",
        f"{sessions_per_week:.1f}"
    )


with col3:

    hours_per_week = (
        total_duration
        / 60
        / weeks_with_training
        if weeks_with_training > 0
        else 0
    )

    st.metric(
        "Heures / semaine",
        f"{hours_per_week:.1f} h"
    )


# ============================================================
# CALENDRIER D'ACTIVITÉ
# ============================================================

st.markdown(
    "### 📆 Activité jour par jour"
)


daily = (
    df_period
    .groupby(
        df_period["date"].dt.date
    )
    .agg(
        Séances=("type", "size"),
        Minutes=("duration", "sum")
    )
)


# Recréer toutes les dates de la période
all_dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)


daily = daily.reindex(
    all_dates.date,
    fill_value=0
)


st.bar_chart(
    daily["Minutes"],
    use_container_width=True
)


# ============================================================
# DÉTAIL DES SÉANCES
# ============================================================

st.divider()

st.subheader("📋 Détail des séances")


display_df = df_period.copy()


display_df["Date"] = (
    display_df["date"]
    .dt.strftime("%d/%m/%Y")
)


display_df["Durée"] = (
    display_df["duration"]
    .apply(format_duration)
)


display_df["Activité"] = (
    display_df["type"].apply(
        lambda x:
        f"{activity_icon(x)} {x}"
    )
)


display_df = display_df[
    [
        "Date",
        "Activité",
        "name",
        "format",
        "Durée"
    ]
]


display_df.columns = [
    "Date",
    "Type",
    "Séance",
    "Format",
    "Durée"
]


display_df = display_df.sort_values(
    "Date",
    ascending=False
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
) 
