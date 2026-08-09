import streamlit as st
import pandas as pd

from database import (
    add_activity,
    get_activities,
    delete_activity,
    add_segment,
    get_segments
)


# ============================================================
# PAGE : BANQUE D'ACTIVITÉS
# ============================================================

def training_page():

    st.title("🏋️ Banque d'activités")

    st.markdown(
        "Crée ici les séances que tu pourras ensuite "
        "placer dans ton calendrier."
    )

    # ========================================================
    # CRÉATION D'UNE ACTIVITÉ
    # ========================================================

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

    # Formats différents selon le type
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

    # ========================================================
    # DURÉE ACTIVITÉ NON-COURSE
    # ========================================================

    if activity_type != "Course":

        duration = st.number_input(
            "Durée de l'activité (min)",
            min_value=1,
            max_value=1440,
            value=60,
            step=5
        )

    # ========================================================
    # STRUCTURE COURSE
    # ========================================================

    segments = []

    if activity_type == "Course":

        st.subheader("🏃 Structure de la séance")

        st.caption(
            "Décompose ta séance en différents segments "
            "pour permettre ensuite le calcul du temps passé "
            "dans chaque zone."
        )

        # Initialisation de la liste dans session_state
        if "training_segments" not in st.session_state:
            st.session_state.training_segments = []

        # ----------------------------------------------
        # Affichage des segments existants
        # ----------------------------------------------

        for i, segment in enumerate(
            st.session_state.training_segments
        ):

            st.markdown(f"**Segment {i + 1}**")

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
                segment_intensity = st.selectbox(
                    "Intensité",
                    [
                        "Z2",
                        "Seuil",
                        "Haute intensité",
                        "Récupération"
                    ],
                    index=[
                        "Z2",
                        "Seuil",
                        "Haute intensité",
                        "Récupération"
                    ].index(segment["intensity"]),
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

        # ----------------------------------------------
        # Ajouter un segment
        # ----------------------------------------------

        if st.button("➕ Ajouter un segment"):

            st.session_state.training_segments.append({
                "name": "Nouveau segment",
                "duration": 5,
                "intensity": "Z2"
            })

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

            st.markdown("### 📊 Résumé")

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

    # ========================================================
    # ENREGISTREMENT
    # ========================================================

    st.divider()

    if st.button(
        "💾 Enregistrer l'activité",
        type="primary"
    ):

        if not activity_name.strip():

            st.error(
                "Veuillez donner un nom à l'activité."
            )

        elif activity_type == "Course" and not st.session_state.get(
            "training_segments"
        ):

            st.error(
                "Ajoute au moins un segment à ta séance de course."
            )

        else:

            # Durée
            if activity_type == "Course":
                duration = sum(
                    segment["duration"]
                    for segment in st.session_state.training_segments
                )

            # Création activité
            activity_id = add_activity(
                activity_name,
                activity_type,
                activity_format,
                duration,
                description
            )

            # Enregistrement segments
            if activity_type == "Course":

                for i, segment in enumerate(
                    st.session_state.training_segments
                ):

                    add_segment(
                        activity_id,
                        i + 1,
                        segment["name"],
                        segment["duration"],
                        segment["intensity"]
                    )

                st.session_state.training_segments = []

            st.success(
                f"✅ Activité « {activity_name} » enregistrée !"
            )

            st.rerun()

    # ========================================================
    # BANQUE EXISTANTE
    # ========================================================

    st.divider()

    st.header("📚 Mes activités")

    activities = get_activities()

    if not activities:

        st.info(
            "Aucune activité enregistrée pour le moment."
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
                f"{name} — {activity_type} — {duration} min"
            ):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.write(
                        f"**Type :** {activity_type}"
                    )

                    st.write(
                        f"**Format :** {activity_format}"
                    )

                    st.write(
                        f"**Durée :** {duration} min"
                    )

                    if description:

                        st.write(
                            f"**Description :** {description}"
                        )

                # --------------------------------------
                # Segments course
                # --------------------------------------

                if activity_type == "Course":

                    segments_db = get_segments(
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

                # --------------------------------------
                # Suppression
                # --------------------------------------

                if st.button(
                    "🗑️ Supprimer",
                    key=f"delete_activity_{activity_id}"
                ):

                    delete_activity(activity_id)

                    st.success(
                        f"{name} supprimée."
                    )

                    st.rerun()