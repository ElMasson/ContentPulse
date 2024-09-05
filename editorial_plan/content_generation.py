# editorial_plan/content_generation.py

import streamlit as st
import pandas as pd
from datetime import datetime
import time
from content_suggestions.ai_integration import generate_ai_suggestions
from .utils import get_article_details, get_branding_info, get_personas, get_build_matrix, get_business_objectives


def generate_content_prompt(article_info, branding_info, personas, build_matrix, business_objectives):
    prompt = f"""
    Objectif : Créer un contenu pour l'article "{article_info['title']}" en respectant les contraintes suivantes :

    1. Informations sur l'article :
    - Type de contenu : {article_info['content_type']}
    - Thème : {article_info['theme']}
    - Mots-clés : {', '.join(article_info['keywords'])}
    - Persona cible : {article_info['target_persona']}
    - Étape du parcours client : {article_info['customer_journey_stage']}
    - CTA principal : {article_info['main_cta']}

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


def generate_content_page(conn, article_id):
    st.title("Génération de Contenu")

    # Récupérer les détails de l'article
    article_info = get_article_details(conn, article_id)

    if not article_info:
        st.error("Article non trouvé.")
        return

    # Afficher les détails de l'article
    st.subheader(f"Détails de l'article : {article_info['title']}")
    st.table(pd.DataFrame([article_info]))

    # Récupérer les informations nécessaires pour le prompt
    branding_info = get_branding_info(conn)
    personas = get_personas(conn)
    build_matrix = get_build_matrix(conn)
    business_objectives = get_business_objectives(conn)

    # Générer le prompt
    prompt = generate_content_prompt(article_info, branding_info, personas, build_matrix, business_objectives)

    # Afficher le prompt
    with st.expander("Voir le prompt de génération", expanded=False):
        st.text_area("Prompt", prompt, height=300, disabled=True)

    # Bouton pour générer le contenu
    if st.button("Générer le contenu"):
        with st.spinner("Génération du contenu en cours... Cela peut prendre quelques instants."):
            generated_content = generate_ai_suggestions(prompt)
            time.sleep(2)  # Pour s'assurer que le spinner s'affiche

        if generated_content:
            st.subheader("Contenu généré")
            st.markdown(generated_content)

            # Option pour télécharger le contenu généré
            st.download_button(
                label="Télécharger le contenu généré",
                data=generated_content,
                file_name=f"contenu_{article_info['title']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        else:
            st.error("Une erreur s'est produite lors de la génération du contenu. Veuillez réessayer.")

    # Bouton pour revenir au plan éditorial
    if st.button("Retour au plan éditorial"):
        st.session_state.content_generation_active = False
        st.experimental_rerun()