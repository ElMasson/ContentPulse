# auth/authentication.py

import streamlit as st
from datetime import datetime, timedelta
import hashlib
import re
from database.connection import get_connection


def is_valid_password(password):
    """Vérifie si le mot de passe respecte les critères de sécurité."""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    if not re.search(r"[A-Z]", password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r"[a-z]", password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    if not re.search(r"\d", password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, "Mot de passe valide"


def create_user(username, password, role="user"):
    """Crée un nouvel utilisateur dans la base de données."""
    conn = get_connection()
    try:
        # Vérifier si l'utilisateur existe déjà
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contentpulse.users WHERE username = %s", (username,))
            if cur.fetchone():
                return False, "Ce nom d'utilisateur existe déjà"

        # Vérifier la validité du mot de passe
        is_valid, message = is_valid_password(password)
        if not is_valid:
            return False, message

        # Hash le mot de passe et créer l'utilisateur
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO contentpulse.users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_pwd, role)
            )
            conn.commit()
        return True, "Utilisateur créé avec succès"
    except Exception as e:
        return False, f"Erreur lors de la création de l'utilisateur : {str(e)}"
    finally:
        conn.close()


def show_signup_form():
    """Affiche le formulaire d'inscription."""
    st.markdown("""
    <div class="signup-container">
        <h2>Créer un compte</h2>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Nom d'utilisateur", key="signup_username")
    password = st.text_input("Mot de passe", type="password", key="signup_password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")

    if st.button("Créer un compte"):
        if not username or not password:
            st.error("Veuillez remplir tous les champs")
            return

        if password != confirm_password:
            st.error("Les mots de passe ne correspondent pas")
            return

        success, message = create_user(username, password)
        if success:
            st.success(message)
            st.info("Vous pouvez maintenant vous connecter avec vos identifiants")
            return True
        else:
            st.error(message)
            return False


def check_password():
    """Retourne `True` si l'utilisateur a entré les bons identifiants."""

    def login_user(username, password):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
                cur.execute(
                    "SELECT id, username, role FROM contentpulse.users WHERE username = %s AND password = %s",
                    (username, hashed_pwd)
                )
                user = cur.fetchone()
                if user:
                    # Mettre à jour la date de dernière connexion
                    cur.execute(
                        "UPDATE contentpulse.users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                        (user[0],)
                    )
                    conn.commit()
                    return {"id": user[0], "username": user[1], "role": user[2]}
        except Exception as e:
            st.error(f"Erreur lors de la connexion : {str(e)}")
        finally:
            conn.close()
        return None

    def init_session_state():
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        if 'show_signup' not in st.session_state:
            st.session_state.show_signup = False

    init_session_state()

    # Si l'utilisateur est déjà connecté, vérifier si la session n'a pas expiré
    if st.session_state.user is not None:
        if st.session_state.login_time:
            if datetime.now() - st.session_state.login_time > timedelta(hours=8):
                st.session_state.user = None
                st.session_state.login_time = None
                st.warning("Votre session a expiré. Veuillez vous reconnecter.")
            else:
                return True

    # Afficher le formulaire de connexion ou d'inscription
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .stButton>button {
            width: 100%;
        }
        .signup-link {
            text-align: center;
            margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.show_signup:
        if show_signup_form():
            st.session_state.show_signup = False
            st.rerun()
        if st.button("Retour à la connexion"):
            st.session_state.show_signup = False
            st.rerun()
    else:
        with st.container():
            st.title("ContentPulse - Connexion")

            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Se connecter"):
                    user = login_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.login_time = datetime.now()
                        st.success("Connexion réussie!")
                        st.rerun()
                    else:
                        st.error("Nom d'utilisateur ou mot de passe incorrect")

            with col2:
                if st.button("Créer un compte"):
                    st.session_state.show_signup = True
                    st.rerun()

            st.markdown("---")
            st.markdown("© 2024 ContentPulse. Tous droits réservés.")

    return False