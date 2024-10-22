#configuration/build_matrix.py

import streamlit as st
from psycopg2 import sql
def build_matrix_config(conn, company_id):
    st.header("Configuration de la Matrice BUILD")

    # Récupérer les personas sélectionnés pour cette entreprise
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name 
            FROM contentpulse.personas 
            WHERE company_id = %s AND is_selected = TRUE
        """, (company_id,))
        personas = [row[0] for row in cur.fetchall()]

    if not personas:
        st.warning("Aucun persona n'a été configuré. Veuillez d'abord configurer les personas.")
        return

    selected_persona = st.selectbox("Sélectionnez un persona", personas)

    # Récupérer les données existantes pour le persona sélectionné
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM contentpulse.build_matrix 
            WHERE company_id = %s AND persona = %s
        """, (company_id, selected_persona))
        existing_data = cur.fetchone()

    if existing_data:
        pain_points = st.text_area(
            "Points de douleur (Pain Points)",
            value=existing_data[3],
            help="Entrez les points de douleur séparés par des virgules"
        )
        pain_killers = st.text_area(
            "Solutions (Pain Killers)",
            value=existing_data[4],
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
                cur.execute("""
                    INSERT INTO contentpulse.build_matrix
                    (company_id, persona, pain_points, pain_killers)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (company_id, persona) DO UPDATE
                    SET pain_points = EXCLUDED.pain_points,
                        pain_killers = EXCLUDED.pain_killers
                """, (company_id, selected_persona, pain_points, pain_killers))
            conn.commit()
            st.success(f"Matrice BUILD pour {selected_persona} sauvegardée avec succès!")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la sauvegarde : {str(e)}")