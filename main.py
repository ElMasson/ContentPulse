# main.py

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
import logging

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

# Initialisation de la session state
if 'selected_article_id' not in st.session_state:
    st.session_state.selected_article_id = None

def main():
    # Connexion à la base de données et initialisation
    try:
        logger.info("Tentative de connexion à la base de données")
        conn = get_connection()
        logger.info("Connexion à la base de données réussie")
        logger.info("Début de l'initialisation de la base de données")
        initialize_database(conn)
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur de connexion ou d'initialisation de la base de données : {str(e)}")
        st.error(f"Erreur de connexion à la base de données : {str(e)}")
        return

    # Sidebar
    st.sidebar.title("ContentPulse")
    st.sidebar.image("img/logo.png", use_column_width=True)

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

    # Main content
    st.title("ContentPulse - Pilotage du Plan Éditorial")

    # Display content based on selected option
    try:
        if selected_option == "Plan Éditorial":
            display_editorial_plan(conn)
        elif selected_option == "Branding":
            branding_config(conn)
        elif selected_option == "Personas":
            personas_config(conn)
        elif selected_option == "Matrice BUILD":
            build_matrix_config(conn)
        elif selected_option == "Types de Contenu":
            content_types_config(conn)
        elif selected_option == "Objectifs Métier":
            business_objectives_config(conn)
    except Exception as e:
        logger.error(f"Error displaying section {selected_option}: {str(e)}")
        st.error(f"Une erreur s'est produite lors de l'affichage de cette section. Veuillez réessayer ou contacter l'administrateur.")

    # Pied de page
    st.markdown("---")
    st.markdown("© 2024 ContentPulse. Tous droits réservés.")

    # Afficher la version de l'application
    st.sidebar.markdown("---")
    st.sidebar.text("ContentPulse v1.4.0")

    # Fermeture de la connexion à la base de données
    close_connection(conn)

# Fonction de vérification du plan éditorial (pour le débogage)
def verify_editorial_plan(conn):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT COUNT(*) FROM contentpulse.editorial_plan")
        count = cur.fetchone()[0]
        logger.info(f"Nombre d'entrées dans le plan éditorial : {count}")
        if count > 0:
            cur.execute("SELECT * FROM contentpulse.editorial_plan LIMIT 1")
            sample = cur.fetchone()
            logger.info(f"Exemple d'entrée : {dict(sample)}")
        else:
            logger.warning("Le plan éditorial est vide")

if __name__ == "__main__":
    main()