#configuration/personas.py
import streamlit as st

def personas_config(conn, company_id):
    st.header("Configuration des Personas")

    # Récupérer tous les personas de l'entreprise
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, is_selected 
            FROM contentpulse.personas 
            WHERE company_id = %s
            ORDER BY name
        """, (company_id,))
        personas = cur.fetchall()

    # Si pas de personas, créer les défauts
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
                cur.execute("""
                    INSERT INTO contentpulse.personas (company_id, name, is_selected)
                    VALUES (%s, %s, FALSE)
                """, (company_id, persona))
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, is_selected 
                FROM contentpulse.personas 
                WHERE company_id = %s
                ORDER BY name
            """, (company_id,))
            personas = cur.fetchall()

    personas_dict = {persona[0]: persona[1] for persona in personas}

    st.write("Sélectionnez les personas pertinents pour votre stratégie :")
    for persona in personas_dict:
        personas_dict[persona] = st.checkbox(
            persona,
            value=personas_dict[persona],
            key=f"persona_{company_id}_{persona}"
        )

    new_persona = st.text_input(
        "Ajouter un nouveau persona",
        key=f"new_persona_{company_id}"
    )

    if st.button("Ajouter", key=f"add_persona_{company_id}"):
        if new_persona and new_persona not in personas_dict:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contentpulse.personas (company_id, name, is_selected)
                    VALUES (%s, %s, TRUE)
                """, (company_id, new_persona))
            conn.commit()
            st.success(f"Persona '{new_persona}' ajouté avec succès!")
            st.rerun()
        else:
            st.warning("Ce persona existe déjà ou le champ est vide.")

    if st.button("Sauvegarder les Personas", key=f"save_personas_{company_id}"):
        with conn.cursor() as cur:
            for persona, is_selected in personas_dict.items():
                cur.execute("""
                    UPDATE contentpulse.personas 
                    SET is_selected = %s 
                    WHERE company_id = %s AND name = %s
                """, (is_selected, company_id, persona))
        conn.commit()
        st.success("Configuration des personas sauvegardée avec succès!")