#configuration/personas.py

import streamlit as st
from psycopg2 import sql

def personas_config(conn):
    st.header("Configuration des Personas")

    # Récupérer tous les personas
    with conn.cursor() as cur:
        cur.execute("SELECT name, is_selected FROM contentpulse.personas")
        personas = cur.fetchall()

    # Si la table est vide, insérez les valeurs par défaut
    if not personas:
        default_personas = [
            "Dirigeant d'entreprise",
            "Responsable marketing",
            "Responsable des ventes",
            "Responsable IT",
            "Entrepreneur"
        ]
        with conn.cursor() as cur:
            for persona in default_personas:
                cur.execute(
                    "INSERT INTO contentpulse.personas (name, is_selected) VALUES (%s, %s)",
                    (persona, False)
                )
        conn.commit()

        # Récupérer à nouveau les personas après l'insertion
        with conn.cursor() as cur:
            cur.execute("SELECT name, is_selected FROM contentpulse.personas")
            personas = cur.fetchall()

    # Créer un dictionnaire pour stocker l'état de sélection de chaque persona
    personas_dict = {persona[0]: persona[1] for persona in personas}

    # Afficher les personas avec des cases à cocher
    st.write("Sélectionnez les personas pertinents pour votre stratégie :")
    for persona, is_selected in personas_dict.items():
        personas_dict[persona] = st.checkbox(persona, value=is_selected, key=f"persona_{persona}")

    # Ajouter un nouveau persona
    new_persona = st.text_input("Ajouter un nouveau persona")
    if st.button("Ajouter le nouveau persona"):
        if new_persona and new_persona not in personas_dict:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contentpulse.personas (name, is_selected) VALUES (%s, %s)",
                    (new_persona, True)
                )
            conn.commit()
            st.success(f"Persona '{new_persona}' ajouté avec succès!")
            st.experimental_rerun()
        else:
            st.warning("Ce persona existe déjà ou le champ est vide.")

    # Sauvegarder les changements
    if st.button("Sauvegarder les Personas"):
        with conn.cursor() as cur:
            for persona, is_selected in personas_dict.items():
                cur.execute(
                    "UPDATE contentpulse.personas SET is_selected = %s WHERE name = %s",
                    (is_selected, persona)
                )
        conn.commit()
        st.success("Configuration des personas sauvegardée avec succès!")