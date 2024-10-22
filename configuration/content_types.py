#configuration/content_types.py
import streamlit as st

def content_types_config(conn, company_id):
    st.header("Configuration des Types de Contenu")

    # Récupérer tous les types de contenu
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month 
            FROM contentpulse.content_types
            WHERE company_id = %s
            ORDER BY name
        """, (company_id,))
        content_types = cur.fetchall()

    # Si la table est vide, insérer les valeurs par défaut
    if not content_types:
        default_types = [
            "Article de blog",
            "Page web",
            "E-book",
            "Infographie",
            "Vidéo",
            "Podcast",
            "Webinaire",
            "Étude de cas",
            "Livre blanc",
            "Newsletter",
            "Post sur les réseaux sociaux",
            "Présentation",
            "Guide pratique",
            "FAQ",
            "Témoignage client"
        ]
        with conn.cursor() as cur:
            for content_type in default_types:
                cur.execute("""
                    INSERT INTO contentpulse.content_types 
                    (company_id, name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month)
                    VALUES (%s, %s, FALSE, 0, 0, 0)
                """, (company_id, content_type))
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month 
                FROM contentpulse.content_types
                WHERE company_id = %s
                ORDER BY name
            """, (company_id,))
            content_types = cur.fetchall()

    content_types_dict = {
        ct[0]: {
            "is_selected": ct[1],
            "target_per_week": ct[2],
            "max_frequency_per_week": ct[3],
            "max_frequency_per_month": ct[4]
        } for ct in content_types
    }

    st.write("Configurez les types de contenu :")
    for content_type, info in content_types_dict.items():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            info["is_selected"] = st.checkbox(
                content_type,
                value=info["is_selected"],
                key=f"content_type_{company_id}_{content_type}"
            )

        if info["is_selected"]:
            with col2:
                info["target_per_week"] = st.number_input(
                    f"Cible/semaine",
                    min_value=0,
                    value=info["target_per_week"],
                    key=f"target_{company_id}_{content_type}"
                )
            with col3:
                info["max_frequency_per_week"] = st.number_input(
                    f"Max/semaine",
                    min_value=0,
                    value=info["max_frequency_per_week"],
                    key=f"freq_week_{company_id}_{content_type}"
                )
            with col4:
                info["max_frequency_per_month"] = st.number_input(
                    f"Max/mois",
                    min_value=0,
                    value=info["max_frequency_per_month"],
                    key=f"freq_month_{company_id}_{content_type}"
                )

    new_type = st.text_input(
        "Ajouter un nouveau type de contenu",
        key=f"new_content_type_{company_id}"
    )

    if st.button("Ajouter", key=f"add_content_type_{company_id}"):
        if new_type and new_type not in content_types_dict:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contentpulse.content_types 
                    (company_id, name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month)
                    VALUES (%s, %s, TRUE, 0, 0, 0)
                """, (company_id, new_type))
            conn.commit()
            st.success(f"Type de contenu '{new_type}' ajouté avec succès!")
            st.rerun()
        else:
            st.warning("Ce type de contenu existe déjà ou le champ est vide.")

    if st.button("Sauvegarder", key=f"save_content_types_{company_id}"):
        with conn.cursor() as cur:
            for content_type, info in content_types_dict.items():
                cur.execute("""
                    UPDATE contentpulse.content_types 
                    SET is_selected = %s,
                        target_per_week = %s,
                        max_frequency_per_week = %s,
                        max_frequency_per_month = %s
                    WHERE company_id = %s AND name = %s
                """, (
                    info["is_selected"],
                    info["target_per_week"],
                    info["max_frequency_per_week"],
                    info["max_frequency_per_month"],
                    company_id,
                    content_type
                ))
        conn.commit()
        st.success("Configuration des types de contenu sauvegardée avec succès!")