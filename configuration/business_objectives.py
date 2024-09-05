#configuration/business_objectives.py

import streamlit as st
from .utils import create_table_if_not_exists, get_existing_data, save_data


def business_objectives_config(conn):
    st.header("Configuration des Objectifs Métier")

    create_table_if_not_exists(conn, 'business_objectives', [
        'name TEXT UNIQUE NOT NULL',
        'is_selected BOOLEAN DEFAULT FALSE'
    ])

    objectives = get_existing_data(conn, 'business_objectives', multiple=True)

    st.write("Sélectionnez les objectifs métier du plan éditorial :")
    for objective in objectives:
        is_selected = st.checkbox(objective['name'], value=objective['is_selected'])

        # Mise à jour de la sélection dans la base de données
        if is_selected != objective['is_selected']:
            save_data(conn, 'business_objectives', {'is_selected': is_selected},
                      condition=f"name = '{objective['name']}'")

    # Ajouter un nouvel objectif
    new_objective = st.text_input("Ajouter un nouvel objectif métier")
    if st.button("Ajouter le nouvel objectif"):
        if new_objective:
            data = {
                'name': new_objective,
                'is_selected': True
            }
            save_data(conn, 'business_objectives', data)
            st.success(f"Objectif '{new_objective}' ajouté avec succès!")
            st.experimental_rerun()
        else:
            st.warning("Veuillez entrer un nom pour le nouvel objectif.")

    # Sauvegarder les changements
    if st.button("Sauvegarder les Objectifs"):
        st.success("Configuration des objectifs métier sauvegardée avec succès!")