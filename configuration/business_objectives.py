#configuration/business_objectives.py

import streamlit as st

def business_objectives_config(conn, company_id):
    st.header("Configuration des Objectifs Métier")

    # Récupérer les objectifs existants
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, is_selected 
            FROM contentpulse.business_objectives 
            WHERE company_id = %s
            ORDER BY name
        """, (company_id,))
        objectives = cur.fetchall()

    # Si pas d'objectifs, créer les défauts
    if not objectives:
        default_objectives = [
            "Augmenter le trafic",
            "Générer des leads",
            "Améliorer la notoriété de la marque"
        ]
        with conn.cursor() as cur:
            for objective in default_objectives:
                cur.execute("""
                    INSERT INTO contentpulse.business_objectives (company_id, name, is_selected)
                    VALUES (%s, %s, FALSE)
                """, (company_id, objective))
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, is_selected 
                FROM contentpulse.business_objectives 
                WHERE company_id = %s
                ORDER BY name
            """, (company_id,))
            objectives = cur.fetchall()

    objectives_dict = {obj[0]: obj[1] for obj in objectives}

    st.write("Sélectionnez les objectifs métier du plan éditorial :")
    for objective in objectives_dict:
        objectives_dict[objective] = st.checkbox(
            objective,
            value=objectives_dict[objective],
            key=f"objective_{company_id}_{objective}"
        )

    new_objective = st.text_input(
        "Ajouter un nouvel objectif métier",
        key=f"new_objective_{company_id}"
    )

    if st.button("Ajouter", key=f"add_objective_{company_id}"):
        if new_objective:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contentpulse.business_objectives (company_id, name, is_selected)
                    VALUES (%s, %s, TRUE)
                """, (company_id, new_objective))
            conn.commit()
            st.success(f"Objectif '{new_objective}' ajouté avec succès!")
            st.rerun()
        else:
            st.warning("Veuillez entrer un nom pour le nouvel objectif.")

    if st.button("Sauvegarder", key=f"save_objectives_{company_id}"):
        with conn.cursor() as cur:
            for objective, is_selected in objectives_dict.items():
                cur.execute("""
                    UPDATE contentpulse.business_objectives 
                    SET is_selected = %s 
                    WHERE company_id = %s AND name = %s
                """, (is_selected, company_id, objective))
        conn.commit()
        st.success("Configuration des objectifs métier sauvegardée avec succès!")