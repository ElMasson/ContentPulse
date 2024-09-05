#configuration/build_matrix.py

import streamlit as st
from psycopg2 import sql

def build_matrix_config(conn):
    st.header("Configuration de la Matrice BUILD")

    # Récupérer les personas sélectionnés
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM contentpulse.personas WHERE is_selected = TRUE")
        personas = [row[0] for row in cur.fetchall()]

    if not personas:
        st.warning("Aucun persona n'a été configuré. Veuillez d'abord configurer les personas.")
        return

    selected_persona = st.selectbox("Sélectionnez un persona", personas)

    # Récupérer les données existantes pour le persona sélectionné
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM contentpulse.build_matrix WHERE persona = %s",
            (selected_persona,)
        )
        existing_data = cur.fetchone()

    if existing_data:
        pain_points = st.text_area(
            "Points de douleur (Pain Points)",
            value=existing_data[2],
            help="Entrez les points de douleur séparés par des virgules"
        )
        pain_killers = st.text_area(
            "Solutions (Pain Killers)",
            value=existing_data[3],
            help="Entrez les solutions séparées par des virgules"
        )
    else:
        pain_points = st.text_area(
            "Points de douleur (Pain Points)",
            help="Entrez les points de douleur séparés par des virgules"
        )
        pain_killers = st.text_area(
            "Solutions (Pain Killers)",
            help="Entrez les solutions séparées par des virgules"
        )

    if st.button("Sauvegarder la Matrice BUILD"):
        try:
            with conn.cursor() as cur:
                # Vérifier si une entrée existe déjà pour ce persona
                cur.execute(
                    "SELECT COUNT(*) FROM contentpulse.build_matrix WHERE persona = %s",
                    (selected_persona,)
                )
                if cur.fetchone()[0] > 0:
                    # Mettre à jour l'entrée existante
                    cur.execute("""
                        UPDATE contentpulse.build_matrix
                        SET pain_points = %s, pain_killers = %s
                        WHERE persona = %s
                    """, (pain_points, pain_killers, selected_persona))
                else:
                    # Insérer une nouvelle entrée
                    cur.execute("""
                        INSERT INTO contentpulse.build_matrix (persona, pain_points, pain_killers)
                        VALUES (%s, %s, %s)
                    """, (selected_persona, pain_points, pain_killers))
            conn.commit()
            st.success(f"Matrice BUILD pour {selected_persona} sauvegardée avec succès!")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la sauvegarde : {str(e)}")