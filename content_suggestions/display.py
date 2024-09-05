#content_suggestions/display.py

import streamlit as st
from .suggestion_generator import generate_content_suggestions
import pandas as pd
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def add_suggestions_to_editorial_plan(engine, df):
    inserted_count = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            try:
                # Convertir la liste de mots-clés en un tableau PostgreSQL
                keywords = '{' + ','.join(f'"{k.strip()}"' for k in row['keywords'].split(',')) + '}'

                query = text("""
                    INSERT INTO contentpulse.editorial_plan
                    (title, content_type, theme, keywords, author, planned_publication_date, status, target_persona, customer_journey_stage, main_cta, url, views, engagements, conversions)
                    VALUES (:title, :content_type, :theme, :keywords::text[], :author, :planned_publication_date, :status, :target_persona, :customer_journey_stage, :main_cta, :url, :views, :engagements, :conversions)
                """)

                conn.execute(query, {
                    'title': row['title'],
                    'content_type': row['content_type'],
                    'theme': row['theme'],
                    'keywords': keywords,
                    'author': row['author'],
                    'planned_publication_date': row['planned_publication_date'],
                    'status': row['status'],
                    'target_persona': row['target_persona'],
                    'customer_journey_stage': row['customer_journey_stage'],
                    'main_cta': row['main_cta'],
                    'url': row['url'],
                    'views': row['views'],
                    'engagements': row['engagements'],
                    'conversions': row['conversions']
                })
                inserted_count += 1
                logger.info(f"Suggestion ajoutée au plan éditorial : {row['title']}")
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout de la suggestion '{row['title']}' : {e}")

    logger.info(f"Nombre total de suggestions ajoutées : {inserted_count}")
    return inserted_count


def display_content_suggestions(engine):
    st.header("Suggestions de Contenu")

    if st.button("Générer des suggestions"):
        with st.spinner("Génération des suggestions en cours..."):
            suggestions_df = generate_content_suggestions(engine)

        if suggestions_df is not None and not suggestions_df.empty:
            st.subheader("Suggestions générées :")

            # Convertir la colonne planned_publication_date en datetime
            suggestions_df['planned_publication_date'] = pd.to_datetime(suggestions_df['planned_publication_date'],
                                                                        errors='coerce')

            # Convertir la colonne keywords en chaîne de caractères
            suggestions_df['keywords'] = suggestions_df['keywords'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x)

            # Afficher le DataFrame avec des options d'édition
            edited_df = st.data_editor(
                suggestions_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "title": st.column_config.TextColumn("Titre"),
                    "content_type": st.column_config.TextColumn("Type de contenu"),
                    "theme": st.column_config.TextColumn("Thème"),
                    "keywords": st.column_config.TextColumn("Mots-clés"),
                    "author": st.column_config.TextColumn("Auteur"),
                    "planned_publication_date": st.column_config.DateColumn("Date de publication prévue"),
                    "status": st.column_config.SelectboxColumn(
                        "Statut",
                        options=["Planifié", "En cours", "Publié", "Archivé"],
                    ),
                    "target_persona": st.column_config.TextColumn("Persona cible"),
                    "customer_journey_stage": st.column_config.SelectboxColumn(
                        "Étape du parcours client",
                        options=["Découverte", "Considération", "Décision", "Fidélisation"],
                    ),
                    "main_cta": st.column_config.TextColumn("CTA principal"),
                    "url": st.column_config.TextColumn("URL"),
                    "views": st.column_config.NumberColumn("Vues", step=1),
                    "engagements": st.column_config.NumberColumn("Engagements", step=1),
                    "conversions": st.column_config.NumberColumn("Conversions", step=1),
                },
                hide_index=True,
            )

            if st.button("Ajouter les suggestions sélectionnées au plan éditorial"):
                inserted_count = add_suggestions_to_editorial_plan(engine, edited_df)
                if inserted_count > 0:
                    st.success(f"{inserted_count} suggestion(s) ont été ajoutées au plan éditorial.")
                else:
                    st.warning("Aucune suggestion n'a pu être ajoutée au plan éditorial.")
        else:
            st.error("Une erreur s'est produite lors de la génération des suggestions.")

    st.markdown("---")
    st.info(
        "Ces suggestions sont générées en tenant compte de vos personas, types de contenu, objectifs métier et de la matrice BUILD. N'hésitez pas à les adapter à vos besoins spécifiques avant de les ajouter à votre plan éditorial.")