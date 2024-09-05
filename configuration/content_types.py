#configuration/content_types.py

import streamlit as st
from psycopg2 import sql

def content_types_config(conn):
    st.header("Configuration des Types de Contenu")

    # Récupérer tous les types de contenu
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month 
            FROM contentpulse.content_types
        """)
        content_types = cur.fetchall()

    # Si la table est vide, insérez les valeurs par défaut
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
                    (name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (content_type, False, 0, 0, 0))
        conn.commit()

        # Récupérer à nouveau les types de contenu après l'insertion
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month 
                FROM contentpulse.content_types
            """)
            content_types = cur.fetchall()

    # Créer un dictionnaire pour stocker les informations de chaque type de contenu
    content_types_dict = {ct[0]: {"is_selected": ct[1], "target_per_week": ct[2], "max_frequency_per_week": ct[3],
                                  "max_frequency_per_month": ct[4]} for ct in content_types}

    st.write("Configurez les types de contenu :")
    for content_type, info in content_types_dict.items():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            info["is_selected"] = st.checkbox(content_type, value=info["is_selected"],
                                              key=f"content_type_{content_type}")

        if info["is_selected"]:
            with col2:
                info["target_per_week"] = st.number_input(f"Cible par semaine pour {content_type}", min_value=0,
                                                          value=info["target_per_week"], key=f"target_{content_type}")
            with col3:
                info["max_frequency_per_week"] = st.number_input(f"Fréq. max/semaine pour {content_type}", min_value=0,
                                                                 value=info["max_frequency_per_week"],
                                                                 key=f"freq_week_{content_type}")
            with col4:
                info["max_frequency_per_month"] = st.number_input(f"Fréq. max/mois pour {content_type}", min_value=0,
                                                                  value=info["max_frequency_per_month"],
                                                                  key=f"freq_month_{content_type}")

    # Ajouter un nouveau type de contenu
    new_content_type = st.text_input("Ajouter un nouveau type de contenu")
    if st.button("Ajouter le nouveau type de contenu"):
        if new_content_type and new_content_type not in content_types_dict:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contentpulse.content_types 
                    (name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (new_content_type, True, 0, 0, 0))
            conn.commit()
            st.success(f"Type de contenu '{new_content_type}' ajouté avec succès!")
            st.experimental_rerun()
        else:
            st.warning("Ce type de contenu existe déjà ou le champ est vide.")

    # Sauvegarder les changements
    if st.button("Sauvegarder les Types de Contenu"):
        with conn.cursor() as cur:
            for content_type, info in content_types_dict.items():
                cur.execute("""
                    UPDATE contentpulse.content_types 
                    SET is_selected = %s, 
                        target_per_week = %s, 
                        max_frequency_per_week = %s, 
                        max_frequency_per_month = %s 
                    WHERE name = %s
                """, (
                    info["is_selected"],
                    info["target_per_week"],
                    info["max_frequency_per_week"],
                    info["max_frequency_per_month"],
                    content_type
                ))
        conn.commit()
        st.success("Configuration des types de contenu sauvegardée avec succès!")