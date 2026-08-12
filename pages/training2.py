import streamlit as st
import pandas as pd

from database2 import (
    add_activity,
    get_activities,
    get_activity,
    delete_activity,
    add_segment,
    get_segments,
    init_database
)

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
    page_title="Base d'entraînements",
    page_icon="🏃",
    layout="wide"
)


## ============================================================
## SÉLECTION DE LA DATABASE
## ============================================================
#
#DATABASES = {
#    "Clément": "training_clement.db",
#    "Utilisateur 2": "training_user2.db",
#    "Utilisateur 3": "training_user3.db",
#    "Utilisateur 4": "training_user4.db"
#}
#
#
#st.subheader("👤 Profil utilisateur")
#
#selected_profile = st.selectbox(
#    "Choisis ta base de données",
#    list(DATABASES.keys()),
#    key="training_database_selector"
#)
#
#DB_NAME = DATABASES[selected_profile]
#
#
## ============================================================
## INITIALISATION DE LA DATABASE
## ============================================================
#
#init_database(DB_NAME)
#
#
#st.info(
#    f"📂 Base utilisée : **{DB_NAME}**"
#)

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
# PAGE : BANQUE D'ACTIVITÉS
# ============================================================

st.title("🏋️ Banque d'activités")

st.markdown(
    "Crée ici les séances que tu pourras ensuite "
    "placer dans ton calendrier."
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
# CRÉATION D'UNE ACTIVITÉ
# ============================================================

st.header("➕ Créer une activité")


activity_name = st.text_input(
    "Nom de l'activité",
    placeholder="Exemple : Seuil 3 × 10 min"
)


activity_type = st.selectbox(
    "Type d'activité",
    [
        "Course",
        "Musculation",
        "Vélo",
        "Natation",
        "Hyrox",
        "Randonnée",
        "Autre"
    ]
)


# ============================================================
# FORMAT
if activity_type == "Course":

    activity_format = st.selectbox(
        "Format de la séance",
        [
            "Endurance Z2",
            "Sortie longue",
            "Seuil",
            "Intervalles",
            "VMA / Haute intensité",
            "Fartlek",
            "Autre"
        ]
    )

elif activity_type == "Musculation":

    activity_format = st.selectbox(
        "Format de la séance",
        [
            "Full Body",
            "Haut du corps",
            "Bas du corps",
            "Push",
            "Pull",
            "Legs",
            "Autre"
        ]
    )

elif activity_type == "Vélo":

    activity_format = st.selectbox(
        "Format de la séance",
        [
            "Endurance",
            "Intervalles",
            "Sortie longue",
            "Récupération",
            "Autre"
        ]
    )

elif activity_type == "Natation":

    activity_format = st.selectbox(
        "Format de la séance",
        [
            "Endurance",
            "Technique",
            "Intervalles",
            "Autre"
        ]
    )

elif activity_type == "Hyrox":

    activity_format = st.selectbox(
        "Format de la séance",
        [
            "Spécifique",
            "Conditioning",
            "Circuit",
            "Simulation",
            "Autre"
        ]
    )

else:

    activity_format = st.text_input(
        "Format",
        placeholder="Exemple : randonnée 15 km"
    )

description = st.text_area(
    "Description",
    placeholder="Décris brièvement la séance..."
)


# ============================================================
# DURÉE ACTIVITÉ NON COURSE
# ============================================================

if activity_type != "Course":

    duration = st.number_input(
        "Durée de l'activité (min)",
        min_value=1,
        max_value=1440,
        value=60,
        step=5
    )


# ============================================================
# STRUCTURE COURSE
# ============================================================

segments = []

if activity_type == "Course":

    st.subheader("🏃 Structure de la séance")

    st.caption(
        "Décompose ta séance en différents segments "
        "pour permettre ensuite le calcul du temps passé "
        "dans chaque zone."
    )


    # ========================================================
    # INITIALISATION SESSION STATE
    # ========================================================

    if "training_segments" not in st.session_state:

        st.session_state.training_segments = []


    if "show_repeat_form" not in st.session_state:

        st.session_state.show_repeat_form = False


    # ========================================================
    # AFFICHAGE DES SEGMENTS
    # ========================================================

    for i, segment in enumerate(
        st.session_state.training_segments
    ):

        st.markdown(
            f"**Segment {i + 1}**"
        )


        col1, col2, col3, col4 = st.columns(
            [2, 1, 2, 0.5]
        )


        with col1:

            segment_name = st.text_input(
                "Nom",
                value=segment["name"],
                key=f"segment_name_{i}"
            )


        with col2:

            segment_duration = st.number_input(
                "Durée (min)",
                min_value=1,
                value=segment["duration"],
                step=1,
                key=f"segment_duration_{i}"
            )


        with col3:

            intensities = [
                "Z2",
                "Seuil",
                "Haute intensité",
                "Récupération"
            ]

            segment_intensity = st.selectbox(
                "Intensité",
                intensities,
                index=intensities.index(
                    segment["intensity"]
                ),
                key=f"segment_intensity_{i}"
            )


        with col4:

            if st.button(
                "🗑️",
                key=f"delete_segment_{i}"
            ):

                st.session_state.training_segments.pop(i)

                st.rerun()


        # Mise à jour
        segment["name"] = segment_name
        segment["duration"] = segment_duration
        segment["intensity"] = segment_intensity


    # ========================================================
    # AJOUT SEGMENTS
    # ========================================================

    col_add, col_repeat = st.columns(
        [1, 2]
    )


    # Segment unique
    with col_add:

        if st.button(
            "➕ Ajouter un segment"
        ):

            st.session_state.training_segments.append({
                "name": "Nouveau segment",
                "duration": 5,
                "intensity": "Z2"
            })

            st.rerun()


    # Segment répété
    with col_repeat:

        if st.button(
            "➕ Ajouter un segment répété"
        ):

            st.session_state.show_repeat_form = True

            st.rerun()


    # ========================================================
    # FORMULAIRE SEGMENT RÉPÉTÉ
    # ========================================================

    if st.session_state.get(
        "show_repeat_form"
    ):

        st.subheader(
            "🔁 Répéter un segment"
        )


        with st.form(
            "repeat_form"
        ):

            rep_name = st.text_input(
                "Nom du segment",
                value="Nouveau segment",
                key="rep_name"
            )


            rep_duration = st.number_input(
                "Durée (min)",
                min_value=1,
                value=5,
                step=1,
                key="rep_duration"
            )


            rep_intensity = st.selectbox(
                "Intensité",
                [
                    "Z2",
                    "Seuil",
                    "Haute intensité",
                    "Récupération"
                ],
                key="rep_intensity"
            )


            rep_count = st.number_input(
                "Répéter ce segment",
                min_value=1,
                max_value=30,
                value=2,
                step=1,
                key="rep_count"
            )


            submitted = st.form_submit_button(
                "Ajouter"
            )


            cancelled = st.form_submit_button(
                "Annuler"
            )


        if submitted:

            for _ in range(
                int(rep_count)
            ):

                st.session_state.training_segments.append({
                    "name": rep_name,
                    "duration": rep_duration,
                    "intensity": rep_intensity
                })


            st.session_state.show_repeat_form = False

            st.rerun()


        if cancelled:

            st.session_state.show_repeat_form = False

            st.rerun()


    # ----------------------------------------------
    # Résumé de la séance
    # ----------------------------------------------

    if st.session_state.training_segments:

        total_duration = sum(
            segment["duration"]
            for segment
            in st.session_state.training_segments
        )

        z2_duration = sum(
            segment["duration"]
            for segment
            in st.session_state.training_segments
            if segment["intensity"] == "Z2"
        )

        threshold_duration = sum(
            segment["duration"]
            for segment
            in st.session_state.training_segments
            if segment["intensity"] == "Seuil"
        )

        high_intensity_duration = sum(
            segment["duration"]
            for segment
            in st.session_state.training_segments
            if segment["intensity"] == "Haute intensité"
        )

        recovery_duration = sum(
            segment["duration"]
            for segment
            in st.session_state.training_segments
            if segment["intensity"] == "Récupération"
        )

        st.markdown("### 📊 Résuméééééé")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Durée totale",
            f"{total_duration} min"
        )

        col2.metric(
            "Z2",
            f"{z2_duration} min"
        )

        col3.metric(
            "Seuil",
            f"{threshold_duration} min"
        )

        col4.metric(
            "Haute intensité",
            f"{high_intensity_duration} min"
        )


# ============================================================
# ENREGISTREMENT
# ============================================================

st.divider()


if st.button(
    "💾 Enregistrer l'activité",
    type="primary"
):

    if not activity_name.strip():

        st.error(
            "Veuillez donner un nom à l'activité."
        )


    elif (
        activity_type == "Course"
        and not st.session_state.get(
            "training_segments"
        )
    ):

        st.error(
            "Ajoute au moins un segment "
            "à ta séance de course."
        )


    else:

        # ====================================================
        # DURÉE
        # ====================================================

        if activity_type == "Course":

            duration = sum(
                segment["duration"]
                for segment
                in st.session_state.training_segments
            )


        # ====================================================
        # CRÉATION ACTIVITÉ
        # ====================================================

        activity_id = add_activity(
            DB_NAME,
            activity_name,
            activity_type,
            activity_format,
            duration,
            description
        )


        # ====================================================
        # SEGMENTS
        # ====================================================

        if activity_type == "Course":

            for i, segment in enumerate(
                st.session_state.training_segments
            ):

                add_segment(
                    DB_NAME,
                    activity_id,
                    i + 1,
                    segment["name"],
                    segment["duration"],
                    segment["intensity"]
                )


            st.session_state.training_segments = []


        st.success(
            f"✅ Activité « {activity_name} » "
            f"enregistrée dans {DB_NAME} !"
        )


        st.rerun()


# ============================================================
# BANQUE EXISTANTE
# ============================================================

st.divider()

st.header("📚 Mes activités")


activities = get_activities(
    DB_NAME
)


if not activities:

    st.info(
        "Aucune activité enregistrée "
        "pour le moment."
    )


else:

    for activity in activities:

        (
            activity_id,
            name,
            activity_type,
            activity_format,
            duration,
            description
        ) = activity


        with st.expander(
            f"{name} — "
            f"{activity_type} — "
            f"{duration} min"
        ):

            col1, col2 = st.columns(
                [4, 1]
            )


            with col1:

                st.write(
                    f"**Type :** "
                    f"{activity_type}"
                )


                st.write(
                    f"**Format :** "
                    f"{activity_format}"
                )


                st.write(
                    f"**Durée :** "
                    f"{duration} min"
                )


                if description:

                    st.write(
                        f"**Description :** "
                        f"{description}"
                    )


            # ==================================================
            # SEGMENTS COURSE
            # ==================================================

            if activity_type == "Course":

                segments_db = get_segments(
                    DB_NAME,
                    activity_id
                )

                if segments_db:

                    st.markdown(
                        "#### Structure"
                    )

                    segment_data = []

                    for segment in segments_db:

                        (
                            segment_id,
                            order,
                            segment_name,
                            segment_duration,
                            intensity
                        ) = segment

                        segment_data.append({
                            "Segment": segment_name,
                            "Durée (min)": segment_duration,
                            "Intensité": intensity
                        })

                    st.dataframe(
                        pd.DataFrame(segment_data),
                        hide_index=True,
                        use_container_width=True
                    )

            # ==================================================
            # SUPPRESSION
            # ==================================================

            if st.button(
                "🗑️ Supprimer",
                key=f"delete_activity_{activity_id}"
            ):

                delete_activity(
                    DB_NAME,
                    activity_id
                )

                st.success(
                    f"{name} supprimée."
                )

                st.rerun()