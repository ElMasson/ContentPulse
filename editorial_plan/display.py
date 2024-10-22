import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import logging
from content_suggestions.suggestion_generator import generate_content_suggestions
import ast
from .utils import clean_and_convert_to_int, parse_keywords

logger = logging.getLogger(__name__)

def format_keywords(keywords):
    if isinstance(keywords, list):
        return keywords
    elif isinstance(keywords, str):
        try:
            return ast.literal_eval(keywords)
        except:
            return [k.strip() for k in keywords.split(',')]
    return [] if pd.isna(keywords) else [str(keywords)]

def get_editorial_plan(conn, company_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.editorial_plan WHERE company_id = %s", (company_id,))
        rows = cur.fetchall()
    df = pd.DataFrame(rows if rows else [])
    if 'keywords' in df.columns and not df.empty:
        df['keywords'] = df['keywords'].apply(format_keywords)
    return df

def save_editorial_plan(conn, df, company_id):
    try:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                if pd.isna(row.get('id')):  # Nouvelle entrée
                    cur.execute("""
                        INSERT INTO contentpulse.editorial_plan
                        (company_id, title, content_type, theme, keywords, author, 
                         planned_publication_date, status, target_persona, 
                         customer_journey_stage, main_cta, url, views, 
                         engagements, conversions)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        company_id,
                        str(row['title']),
                        str(row['content_type']),
                        str(row['theme']) if pd.notna(row['theme']) else None,
                        parse_keywords(row['keywords']),
                        str(row['author']) if pd.notna(row['author']) else None,
                        pd.to_datetime(row['planned_publication_date']).date() if pd.notna(row['planned_publication_date']) else None,
                        str(row['status']),
                        str(row['target_persona']),
                        str(row['customer_journey_stage']),
                        str(row['main_cta']) if pd.notna(row['main_cta']) else None,
                        str(row['url']) if pd.notna(row['url']) else None,
                        clean_and_convert_to_int(row['views']),
                        clean_and_convert_to_int(row['engagements']),
                        clean_and_convert_to_int(row['conversions'])
                    ))
                else:  # Mise à jour
                    cur.execute("""
                        UPDATE contentpulse.editorial_plan
                        SET title = %s, content_type = %s, theme = %s, keywords = %s,
                            author = %s, planned_publication_date = %s, status = %s,
                            target_persona = %s, customer_journey_stage = %s,
                            main_cta = %s, url = %s, views = %s, engagements = %s,
                            conversions = %s
                        WHERE id = %s AND company_id = %s
                    """, (
                        str(row['title']),
                        str(row['content_type']),
                        str(row['theme']) if pd.notna(row['theme']) else None,
                        parse_keywords(row['keywords']),
                        str(row['author']) if pd.notna(row['author']) else None,
                        pd.to_datetime(row['planned_publication_date']).date() if pd.notna(row['planned_publication_date']) else None,
                        str(row['status']),
                        str(row['target_persona']),
                        str(row['customer_journey_stage']),
                        str(row['main_cta']) if pd.notna(row['main_cta']) else None,
                        str(row['url']) if pd.notna(row['url']) else None,
                        clean_and_convert_to_int(row['views']),
                        clean_and_convert_to_int(row['engagements']),
                        clean_and_convert_to_int(row['conversions']),
                        int(row['id']),
                        company_id
                    ))
        conn.commit()
        logger.info("Plan éditorial sauvegardé avec succès")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de la sauvegarde du plan éditorial : {e}")
        raise

def delete_selected_rows(conn, selected_ids, company_id):
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM contentpulse.editorial_plan WHERE id = ANY(%s) AND company_id = %s",
                (selected_ids, company_id)
            )
        conn.commit()
        logger.info(f"Suppression de {len(selected_ids)} lignes réussie")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de la suppression des lignes : {e}")
        raise

def get_branding_info(conn, company_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.branding WHERE company_id = %s", (company_id,))
        return cur.fetchone()

def get_personas(conn, company_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM contentpulse.personas WHERE company_id = %s AND is_selected = TRUE",
            (company_id,)
        )
        return cur.fetchall()

def get_build_matrix(conn, company_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM contentpulse.build_matrix WHERE company_id = %s",
            (company_id,)
        )
        return cur.fetchall()

def get_business_objectives(conn, company_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM contentpulse.business_objectives WHERE company_id = %s AND is_selected = TRUE",
            (company_id,)
        )
        return cur.fetchall()

def display_editorial_plan(conn, company_id):
    st.header("Plan Éditorial")

    # Récupérer le plan éditorial existant
    df = get_editorial_plan(conn, company_id)

    # Ajouter un bouton pour générer des suggestions de contenu
    if st.button("Générer des suggestions de contenu"):
        with st.spinner("Génération des suggestions en cours..."):
            suggestions = generate_content_suggestions(conn, company_id)
            if suggestions is not None:
                suggestions['company_id'] = company_id
                suggestions['keywords'] = suggestions['keywords'].apply(format_keywords)
                df = pd.concat([df, suggestions], ignore_index=True)
                save_editorial_plan(conn, df, company_id)
                st.success("Nouvelles suggestions générées et ajoutées au plan éditorial!")
            else:
                st.error("Impossible de générer des suggestions de contenu pour le moment.")

    # Afficher le plan éditorial avec des options d'édition
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "company_id": st.column_config.NumberColumn("Company ID", disabled=True),
            "title": st.column_config.TextColumn("Titre"),
            "content_type": st.column_config.TextColumn("Type de contenu"),
            "theme": st.column_config.TextColumn("Thème"),
            "keywords": st.column_config.ListColumn("Mots-clés"),
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
            "views": st.column_config.NumberColumn("Vues", step=1, default=None),
            "engagements": st.column_config.NumberColumn("Engagements", step=1, default=None),
            "conversions": st.column_config.NumberColumn("Conversions", step=1, default=None),
        },
        hide_index=True,
        key="editorial_plan_editor"
    )

    # Menu déroulant pour sélectionner un article
    if not edited_df.empty:
        selected_title = st.selectbox(
            "Sélectionner un article pour voir les détails",
            options=edited_df['title'].tolist()
        )

        if selected_title:
            selected_article = edited_df[edited_df['title'] == selected_title].iloc[0]
            if st.button(f"Voir les détails de '{selected_title}'"):
                st.session_state.selected_article_id = str(selected_article['id'])
                st.switch_page("pages/article_details.py")

    # Bouton pour supprimer les lignes sélectionnées
    selected_rows = st.session_state.editorial_plan_editor.get("selected_rows", [])
    if st.button("Supprimer les lignes sélectionnées") and selected_rows:
        selected_ids = [edited_df.iloc[row]["id"] for row in selected_rows]
        delete_selected_rows(conn, selected_ids, company_id)
        st.success(f"{len(selected_rows)} ligne(s) supprimée(s) avec succès!")
        st.rerun()

    # Bouton pour sauvegarder les modifications
    if st.button("Sauvegarder les modifications"):
        save_editorial_plan(conn, edited_df, company_id)
        st.success("Plan éditorial mis à jour avec succès!")