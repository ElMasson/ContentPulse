import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
from database.connection import get_connection, close_connection
from database.models import initialize_database
from editorial_plan.display import display_editorial_plan
from configuration.branding import branding_config
from configuration.personas import personas_config
from configuration.build_matrix import build_matrix_config
from configuration.content_types import content_types_config
from configuration.business_objectives import business_objectives_config
from content_suggestions.display import display_content_suggestions
from auth.authentication import check_password
import logging
from company.selection import company_selector

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(page_title="ContentPulse", page_icon="📅", layout="wide")

# CSS styles
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        color: #4F8BF9;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Vérification de l'authentification
    if not check_password():
        return

    # Connexion à la base de données et initialisation
    try:
        conn = get_connection()
        initialize_database(conn)
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {str(e)}")
        return

    # Sidebar avec sélection d'entreprise
    st.sidebar.title("ContentPulse")
    st.sidebar.image("img/logo.png", use_column_width=True)

    # Informations utilisateur
    if st.session_state.user:
        st.sidebar.markdown(f"Connecté en tant que : **{st.session_state.user['username']}**")
        if st.sidebar.button("Se déconnecter"):
            st.session_state.user = None
            st.session_state.login_time = None
            st.rerun()

    # Sélection de l'entreprise
    current_company_id = company_selector()
    if not current_company_id:
        st.info("Veuillez sélectionner ou créer une entreprise pour continuer.")
        return

    # Menu de navigation
    menu_options = [
        "Plan Éditorial",
        "Branding",
        "Personas",
        "Matrice BUILD",
        "Types de Contenu",
        "Objectifs Métier"
    ]
    selected_option = st.sidebar.radio("Navigation", menu_options)

    # Main content avec contexte d'entreprise
    st.title("ContentPulse - Pilotage du Plan Éditorial")

    # Main content avec contexte d'entreprise
    try:
        if selected_option == "Plan Éditorial":
            display_editorial_plan(conn, current_company_id)
        elif selected_option == "Branding":
            branding_config(conn, current_company_id)
        elif selected_option == "Personas":
            personas_config(conn, current_company_id)
        elif selected_option == "Matrice BUILD":
            build_matrix_config(conn, current_company_id)
        elif selected_option == "Types de Contenu":
            content_types_config(conn, current_company_id)
        elif selected_option == "Objectifs Métier":
            business_objectives_config(conn, current_company_id)
    except Exception as e:
        logger.error(f"Error displaying section {selected_option}: {str(e)}")
        st.error(f"Une erreur s'est produite lors de l'affichage de cette section.")

    close_connection(conn)

if __name__ == "__main__":
    main()