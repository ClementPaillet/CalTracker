# ──────────────────────────────────────────────────────────────
# app.py  –  Page Streamlit « Créer / éditer un profil »
# ──────────────────────────────────────────────────────────────
import json
import os
import shutil
from pathlib import Path

import streamlit as st

# -----------------------------------------------------------------
# 1️⃣ Chemins & fonctions utilitaires
# -----------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
USERS_FILE = BASE_DIR / "users.json"
TEMPLATE_DB = BASE_DIR / "training_teuteu.db"   # modèle fourni
st.markdown(str(USERS_FILE))

def load_users() -> dict:
    """Lit le fichier JSON et renvoie un dict (vide si le fichier n’existe pas)."""
    if USERS_FILE.is_file():
        with USERS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(data: dict) -> None:
    """Écrit le dict dans le JSON avec indentation + encodage UTF‑8."""
    with USERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def copy_training_db(new_login: str) -> None:
    """Copie le modèle en le renommant : training_<login>.db."""
    target = BASE_DIR / f"training_{new_login}.db"
    if not target.exists():
        shutil.copy2(TEMPLATE_DB, target)
    else:
        # On ne veut pas écraser un DB déjà existant (cas d’un re‑upload)
        st.warning(f"Le fichier {target.name} existe déjà, il n’a pas été écrasé.")
        

# -----------------------------------------------------------------
# 2️⃣ Chargement du dictionnaire utilisateurs
# -----------------------------------------------------------------
users = load_users()

# -----------------------------------------------------------------
# 3️⃣ Interface Streamlit
# -----------------------------------------------------------------
st.title("🛠️ Créez ou éditez votre profil")
st.caption("Les changements sont sauvegardés immédiatement dans `users.json`.")

# ---- Formulaire ----
with st.form(key="profile_form"):
    # 1️⃣ Clé du profil (login) – doit être unique
    login = st.text_input(
        "Identifiant (login) – *unique*",
        value="",
        help="Nom d’utilisateur qui servira de clé dans le JSON. Ex : `teuteu`, `nico`."
    ).strip()

    # Si le login existe déjà, on pré‑remplir les champs avec les données actuelles
    existing = users.get(login, {})

    # 2️⃣ Champs du profil (on garde le même ordre que votre JSON)
    col1, col2 = st.columns(2)

    with col1:
        prenom = st.text_input("Prénom", value=existing.get("prenom", ""))
        surnom = st.text_input("Surnom", value=existing.get("surnom", ""))
        age    = st.number_input("Âge", min_value=0, max_value=130,
                                 value=existing.get("age", 0), step=1)
        taille = st.number_input("Taille (cm)", min_value=0, max_value=300,
                                 value=existing.get("taille_cm", 0), step=1)
    with col2:
        nom    = st.text_input("Nom", value=existing.get("nom", ""))
        poids  = st.number_input("Poids (kg)", min_value=0, max_value=300,
                                 value=existing.get("poids_kg", 0), step=1)
        sexe   = st.selectbox("Sexe", ["H", "F", "Autre"],
                              index=0 if existing.get("sexe") in ["H","F","Autre"] else 0,
                              placeholder=existing.get("sexe", "H"))
        bodycount = st.number_input("Body‑count", min_value=0, max_value=500,
                                    value=existing.get("bodycount", 0), step=1)

    emoji = st.text_input("Emoji (ou plusieurs)", value=existing.get("emoji", ""))
    description = st.text_area(
        "Description",
        value=existing.get("description", ""),
        height=120
    )

    # Bouton de soumission
    submitted = st.form_submit_button("Enregistrer")

# -----------------------------------------------------------------
# 4️⃣ Traitement du formulaire
# -----------------------------------------------------------------
if submitted:
    if not login:
        st.error("⚠️ Le champ « Identifiant » est obligatoire.")
        st.stop()

    # Construction du nouveau profil (dictionnaire)
    new_profile = {
        "nom": nom,
        "prenom": prenom,
        "surnom": surnom,
        "age": int(age),
        "taille_cm": int(taille),
        "poids_kg": int(poids),
        "sexe": sexe,
        "bodycount": int(bodycount),
        "emoji": emoji,
        "description": description,
    }

    # -----------------------------------------------------------------
    # a) Création vs Édition
    # -----------------------------------------------------------------
    is_creation = login not in users

    # Met à jour le dict global
    users[login] = new_profile
    save_users(users)          # ← persiste le tout

    # -----------------------------------------------------------------
    # b) Si création → copier le DB modèle
    # -----------------------------------------------------------------
    if is_creation:
        try:
            copy_training_db(login)
            st.success(f"✅ Profil **{login}** créé ! Le fichier `training_{login}.db` a été généré.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la copie du fichier DB : {e}")
    else:
        st.success(f"✅ Profil **{login}** mis à jour !")

    # Optionnel : afficher le profil en JSON pour vérification
    st.subheader("Profil actuel")
    st.json(new_profile)

# -----------------------------------------------------------------
# 5️⃣ Option d’affichage de tous les profils (lecture uniquement)
# -----------------------------------------------------------------
if st.checkbox("📋 Afficher la liste de tous les profils"):
    st.subheader("Tous les profils")
    st.json(users)

# -----------------------------------------------------------------
# 6️⃣ Sécurité & bonnes pratiques (à mettre en production)
# -----------------------------------------------------------------
# - Utiliser `st.secrets` ou une variable d’environnement pour le chemin du dossier.
# - Protéger l’accès : authentification, contrôle d’accès, etc.
# - Verrouillage de fichier (`filelock`) si plusieurs utilisateurs peuvent écrire
#   simultanément.
# - Nettoyer les entrées (ex. `login.lower().strip()` pour éviter les doublons
#   “TeUteU” / “teuteu”).