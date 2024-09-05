import streamlit as st
import sys
import os

# Ajouter le chemin du projet parent au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection
from editorial_plan.utils import get_article_details, get_branding_info, get_personas, get_build_matrix, get_business_objectives
from content_suggestions.ai_integration import generate_ai_suggestions
from content_suggestions.internet_search import display_internet_search_results

import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


st.set_page_config(page_title="Détails de l'article", page_icon="📄", layout="wide")


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

    Étapes de création du contenu :

    1. Réflexion sur la meilleure approche :
    [Réfléchissez à la meilleure façon d'aborder ce contenu en tenant compte de toutes les contraintes mentionnées ci-dessus.]

    2. Première version du contenu :
    [Générez une première version du contenu en vous basant sur votre réflexion.]

    3. Critique détaillée :
    [Analysez la première version en détaillant les points positifs et négatifs, en vérifiant si elle respecte bien toutes les contraintes.]

    4. Version améliorée :
    [Générez une deuxième version du contenu en tenant compte des critiques pour l'améliorer.]

    Étapes de création du contenu :

    1. Réflexion sur la meilleure approche :
    [Réfléchissez à la meilleure façon d'aborder ce contenu en tenant compte de toutes les contraintes mentionnées ci-dessus.]

    2. Première version du contenu :
    [Générez une première version du contenu en vous basant sur votre réflexion.]

    3. Critique détaillée :
    [Analysez la première version en détaillant les points positifs et négatifs, en vérifiant si elle respecte bien toutes les contraintes.]

    4. Version améliorée :
    [Générez une deuxième version du contenu en tenant compte des critiques pour l'améliorer.]

    Étapes de création du contenu :

    1. Réflexion sur la meilleure approche :
    [Réfléchissez à la meilleure façon d'aborder ce contenu en tenant compte de toutes les contraintes mentionnées ci-dessus.]

    2. Première version du contenu :
    [Générez une première version du contenu en vous basant sur votre réflexion.]

    3. Critique détaillée :
    [Analysez la première version en détaillant les points positifs et négatifs, en vérifiant si elle respecte bien toutes les contraintes.]

    4. Version améliorée :
    [Générez une deuxième version du contenu en tenant compte des critiques pour l'améliorer.]

    Veuillez fournir une réponse détaillée pour chacune de ces étapes.
    """
    return prompt


def internet_search(query):
    # Placeholder pour la fonction de recherche Internet
    return f"Résultats de recherche pour : {query}"

def document_search(query):
    # Placeholder pour la fonction de recherche dans les documents
    return f"Résultats de recherche dans les documents pour : {query}"

def main():
    st.title("Détails de l'article")

    # Récupérer l'ID de l'article
    article_id = st.session_state.get('selected_article_id')
    if article_id is None:
        st.error("Aucun article sélectionné. Veuillez retourner au plan éditorial et sélectionner un article.")
        if st.button("Retour au plan éditorial"):
            st.switch_page("main.py")
        return

    # Connexion à la base de données et récupération des données
    try:
        conn = get_connection()
        article = get_article_details(conn, article_id)
        branding_info = get_branding_info(conn)
        personas = get_personas(conn)
        build_matrix = get_build_matrix(conn)
        business_objectives = get_business_objectives(conn)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {str(e)}")
        logger.error(f"Erreur de récupération des données : {str(e)}")
        return
    finally:
        if 'conn' in locals():
            conn.close()

    if article is None:
        st.error("Article non trouvé.")
        return

    # Affichage des détails de l'article
    st.subheader(article['title'])
    st.write(f"Type de contenu : {article['content_type']}")
    st.write(f"Thème : {article['theme']}")

    # Section : Prompt généré
    st.header("Prompt généré")
    prompt = generate_content_prompt(article, branding_info, personas, build_matrix, business_objectives)
    st.text_area("Prompt", prompt, height=200, disabled=True)

    # Section : Recherche Internet
    st.header("Recherche Internet et Génération de Contenu")
    article_context = f"{article['title']} - {article['theme']}"
    display_internet_search_results(article_context)

    # Section : Recherche dans les documents
    st.header("Recherche dans les documents")
    doc_query = st.text_input("Entrez votre requête de recherche dans les documents")
    if st.button("Rechercher dans les documents"):
        with st.spinner("Recherche en cours..."):
            results = document_search(doc_query)
            st.write(results)

    # Section : Contenu généré
    st.header("Contenu généré")
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = ""

    if st.button("Générer le contenu"):
        with st.spinner("Génération du contenu en cours..."):
            generated_content = generate_ai_suggestions(prompt)
            st.session_state.generated_content = generated_content

    edited_content = st.text_area("Contenu généré (modifiable)", st.session_state.generated_content, height=300)

    # Bouton pour sauvegarder le contenu généré
    if st.button("Sauvegarder le contenu"):
        # Implémentez ici la logique pour sauvegarder le contenu édité
        st.success("Contenu sauvegardé avec succès!")
        logger.info(f"Contenu sauvegardé pour l'article {article_id}")

    # Bouton pour revenir au plan éditorial
    if st.button("Retour au plan éditorial"):
        del st.session_state['selected_article_id']
        st.switch_page("main.py")

if __name__ == "__main__":
    main()