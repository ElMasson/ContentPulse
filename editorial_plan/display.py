#editorial_plan/display.py

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

def parse_keywords(keywords):
    return format_keywords(keywords)

def clean_and_convert_to_int(value):
    if pd.isna(value) or value == '' or value == ' ""':
        return None
    try:
        return int(value)
    except ValueError:
        return None

def get_editorial_plan(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.editorial_plan")
        rows = cur.fetchall()
    df = pd.DataFrame(rows)
    if 'keywords' in df.columns:
        df['keywords'] = df['keywords'].apply(format_keywords)
    return df

def save_editorial_plan(conn, df):
    try:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                if pd.isna(row['id']):  # Nouvelle entrée
                    cur.execute("""
                        INSERT INTO contentpulse.editorial_plan
                        (title, content_type, theme, keywords, author, planned_publication_date, status, target_persona, customer_journey_stage, main_cta, url, views, engagements, conversions)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
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
                        clean_and_convert_to_int(row['conversions'])
                    ))
                else:  # Mise à jour d'une entrée existante
                    cur.execute("""
                        UPDATE contentpulse.editorial_plan
                        SET title = %s, content_type = %s, theme = %s, keywords = %s, author = %s,
                            planned_publication_date = %s, status = %s, target_persona = %s,
                            customer_journey_stage = %s, main_cta = %s, url = %s,
                            views = %s, engagements = %s, conversions = %s
                        WHERE id = %s
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
                        int(row['id'])
                    ))
        conn.commit()
        logger.info("Plan éditorial sauvegardé avec succès")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de la sauvegarde du plan éditorial : {e}")
        raise

def delete_selected_rows(conn, selected_ids):
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contentpulse.editorial_plan WHERE id = ANY(%s)", (selected_ids,))
        conn.commit()
        logger.info(f"Suppression de {len(selected_ids)} lignes réussie")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de la suppression des lignes : {e}")
        raise

def get_editorial_plan(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.editorial_plan")
        rows = cur.fetchall()
    df = pd.DataFrame(rows)
    if 'keywords' in df.columns:
        df['keywords'] = df['keywords'].apply(format_keywords)
    return df


def get_branding_info(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.branding LIMIT 1")
        return cur.fetchone()

def get_personas(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.personas WHERE is_selected = TRUE")
        return cur.fetchall()

def get_build_matrix(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.build_matrix")
        return cur.fetchall()

def get_business_objectives(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contentpulse.business_objectives WHERE is_selected = TRUE")
        return cur.fetchall()

def generate_content_prompt(article, branding_info, personas, build_matrix, business_objectives):
    prompt = f"""
    Objectif : Créer un contenu pour l'article "{article['title']}" en respectant les contraintes suivantes :

    1. Informations sur l'article :
    - Type de contenu : {article['content_type']}
    - Thème : {article['theme']}
    - Mots-clés : {', '.join(article['keywords'])}
    - Persona cible : {article['target_persona']}
    - Étape du parcours client : {article['customer_journey_stage']}
    - CTA principal : {article['main_cta']}

    2. Branding :
    - Nom de l'entreprise : {branding_info['company_name']}
    - Valeurs fondatrices : {branding_info['core_values']}
    - Personnalité de marque : {branding_info['brand_personality']}
    - Ton de voix : {branding_info['tone_of_voice']}
    - Proposition de valeur : {branding_info['value_proposition']}

    3. Personas :
    {', '.join([p['name'] for p in personas])}

    4. Matrice BUILD :
    {'; '.join([f"{bm['persona']} - Pain points: {bm['pain_points']}, Pain killers: {bm['pain_killers']}" for bm in build_matrix])}

    5. Objectifs métier :
    {', '.join([bo['name'] for bo in business_objectives])}

    Veuillez générer un contenu détaillé pour cet article en respectant toutes les contraintes mentionnées ci-dessus.
    Le contenu doit être structuré, engageant et adapté au format spécifié.
    """
    return prompt

def display_article_details(conn):
    st.title("Détails de l'article")

    # Récupérer l'ID de l'article depuis les paramètres de requête
    query_params = st.query_params()
    article_id = query_params.get("article_id", [None])[0]

    if article_id is None:
        st.error("Aucun article sélectionné.")
        return

    # Récupérer les détails de l'article
    article = get_article_details(conn, article_id)

    if article is None:
        st.error("Article non trouvé.")
        return

    # Afficher les détails de l'article
    st.subheader(article['title'])

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Type de contenu :** {article['content_type']}")
        st.write(f"**Thème :** {article['theme']}")
        st.write(f"**Mots-clés :** {', '.join(article['keywords'])}")
        st.write(f"**Auteur :** {article['author']}")
        st.write(
            f"**Date de publication prévue :** {article['planned_publication_date'].strftime('%d/%m/%Y') if article['planned_publication_date'] else 'Non définie'}")

    with col2:
        st.write(f"**Statut :** {article['status']}")
        st.write(f"**Persona cible :** {article['target_persona']}")
        st.write(f"**Étape du parcours client :** {article['customer_journey_stage']}")
        st.write(f"**CTA principal :** {article['main_cta']}")
        st.write(f"**URL :** {article['url'] if article['url'] else 'Non définie'}")

    # Métriques
    st.subheader("Métriques")
    col1, col2, col3 = st.columns(3)
    col1.metric("Vues", article['views'] if article['views'] is not None else "N/A")
    col2.metric("Engagements", article['engagements'] if article['engagements'] is not None else "N/A")
    col3.metric("Conversions", article['conversions'] if article['conversions'] is not None else "N/A")

    # Génération de contenu
    st.subheader("Génération de contenu")

    # Récupérer les informations nécessaires pour le prompt
    branding_info = get_branding_info(conn)
    personas = get_personas(conn)
    build_matrix = get_build_matrix(conn)
    business_objectives = get_business_objectives(conn)

    # Générer le prompt
    prompt = generate_content_prompt(article, branding_info, personas, build_matrix, business_objectives)

    # Afficher le prompt
    with st.expander("Voir le prompt de génération", expanded=False):
        st.text_area("Prompt", prompt, height=300, disabled=True)

    # Bouton pour générer le contenu
    if st.button("Générer le contenu"):
        with st.spinner("Génération du contenu en cours... Cela peut prendre quelques instants."):
            generated_content = generate_ai_suggestions(prompt)

        if generated_content:
            st.subheader("Contenu généré")
            st.markdown(generated_content)

            # Option pour télécharger le contenu généré
            st.download_button(
                label="Télécharger le contenu généré",
                data=generated_content,
                file_name=f"contenu_{article['title']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        else:
            st.error("Une erreur s'est produite lors de la génération du contenu. Veuillez réessayer.")

    # Bouton pour revenir au plan éditorial
    if st.button("Retour au plan éditorial"):
        st.experimental_set_query_params()
        st.experimental_rerun()

def generate_content_with_gpt4(prompt):
    try:
        logger.info("Début de la génération de contenu avec GPT-4")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en marketing de contenu. Suivez attentivement les instructions du prompt pour générer le contenu demandé."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20000,
            temperature=0.7
        )
        logger.info("Contenu généré avec succès")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur lors de la génération du contenu : {e}")
        return None


def display_article_details(conn, article_id):
    df = get_editorial_plan(conn)
    article_info = df[df['id'] == article_id].iloc[0].to_dict()

    st.subheader(f"Détails de l'article : {article_info['title']}")

    # Afficher les informations de l'article
    st.table(pd.DataFrame([article_info]))

    # Récupérer les informations nécessaires pour le prompt
    branding_info = get_branding_info(conn)
    personas = get_personas(conn)
    build_matrix = get_build_matrix(conn)
    business_objectives = get_business_objectives(conn)

    # Générer et afficher le prompt
    prompt = generate_content_prompt(article_info, branding_info, personas, build_matrix, business_objectives)
    st.subheader("Prompt pour la génération de contenu")
    st.text_area("Prompt", prompt, height=300)

    # Générer le contenu basé sur le prompt
    if st.button("Générer le contenu"):
        with st.spinner("Génération du contenu en cours... Cela peut prendre quelques instants."):
            generated_content = generate_content_with_gpt4(prompt)
            time.sleep(2)  # Petite pause pour s'assurer que le spinner s'affiche

        if generated_content:
            st.subheader("Contenu généré")
            st.markdown(generated_content)

            # Ajouter un bouton pour télécharger le contenu généré
            st.download_button(
                label="Télécharger le contenu généré",
                data=generated_content,
                file_name=f"contenu_{article_info['title']}.txt",
                mime="text/plain"
            )
        else:
            st.error("Une erreur s'est produite lors de la génération du contenu. Veuillez réessayer.")


def display_editorial_plan(conn):
    st.header("Plan Éditorial")

    # Récupérer le plan éditorial existant
    df = get_editorial_plan(conn)

    # S'assurer que toutes les entrées de la colonne 'keywords' sont des listes
    df['keywords'] = df['keywords'].apply(format_keywords)

    # Ajouter un bouton pour générer des suggestions de contenu
    if st.button("Générer des suggestions de contenu"):
        with st.spinner("Génération des suggestions en cours..."):
            suggestions = generate_content_suggestions(conn)
        if suggestions is not None:
            suggestions['keywords'] = suggestions['keywords'].apply(format_keywords)
            df = pd.concat([df, suggestions], ignore_index=True)
            save_editorial_plan(conn, df)
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
    selected_title = st.selectbox("Sélectionner un article pour voir les détails", options=edited_df['title'].tolist())

    if selected_title:
        selected_article = edited_df[edited_df['title'] == selected_title].iloc[0]
        if st.button(f"Voir les détails de '{selected_title}'"):
            st.session_state.selected_article_id = str(selected_article['id'])
            st.switch_page("pages/article_details.py")

    # Bouton pour supprimer les lignes sélectionnées
    selected_rows = st.session_state.editorial_plan_editor.get("selected_rows", [])
    if st.button("Supprimer les lignes sélectionnées") and selected_rows:
        selected_ids = [edited_df.iloc[row]["id"] for row in selected_rows]
        delete_selected_rows(conn, selected_ids)
        st.success(f"{len(selected_rows)} ligne(s) supprimée(s) avec succès!")
        st.experimental_rerun()

    # Bouton pour sauvegarder les modifications
    if st.button("Sauvegarder les modifications"):
        save_editorial_plan(conn, edited_df)
        st.success("Plan éditorial mis à jour avec succès!")