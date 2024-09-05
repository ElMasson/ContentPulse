import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()

GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def perform_google_search(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        search_results = response.json()
        return search_results.get('items', [])
    except requests.RequestException as e:
        st.error(f"Erreur lors de la recherche Google : {str(e)}")
        return []


def extract_search_content(search_results):
    content = []
    for item in search_results[:5]:  # Limiter à 5 résultats
        title = item.get('title', '')
        snippet = item.get('snippet', '')
        link = item.get('link', '')
        content.append(f"Titre: {title}\nExtrait: {snippet}\nLien: {link}\n")
    return "\n".join(content)


def internet_search(query, article_context):
    search_results = perform_google_search(query)
    if not search_results:
        return "Aucun résultat de recherche trouvé."

    search_content = extract_search_content(search_results)

    prompt = f"""
    Contexte de l'article : {article_context}

    Résultats de recherche Internet :
    {search_content}

    En utilisant spécifiquement les informations fournies par les résultats de recherche ci-dessus, 
    générez un paragraphe de contenu pertinent pour l'article. 
    Intégrez des faits, des chiffres ou des points clés des résultats de recherche.
    Assurez-vous que le contenu est directement lié aux résultats de recherche et au contexte de l'article.
    Citez au moins une source spécifique des résultats de recherche.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Vous êtes un assistant qui génère du contenu basé uniquement sur les résultats de recherche fournis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10000,
            temperature=0.3
        )
        generated_content = response.choices[0].message.content.strip()
        return generated_content
    except Exception as e:
        st.error(f"Erreur lors de la génération du contenu avec GPT-4 : {str(e)}")
        return None


def display_internet_search_results(article_context):
    st.subheader("Recherche Internet et Génération de Contenu")
    query = st.text_input("Entrez votre requête de recherche")
    if st.button("Rechercher et Générer du Contenu"):
        st.write(f"Requête : {query}")
        st.write(f"GOOGLE_CSE_ID : {GOOGLE_CSE_ID[:5]}...")  # Affiche les 5 premiers caractères
        st.write(f"GOOGLE_API_KEY : {GOOGLE_API_KEY[:5]}...")  # Affiche les 5 premiers caractères

        with st.spinner("Recherche en cours et génération de contenu..."):
            search_results = perform_google_search(query)
            if search_results:
                st.write("Résultats de la recherche Google :")
                for result in search_results[:3]:
                    st.write(f"- {result.get('title')} : {result.get('link')}")

                # Le reste du code reste inchangé
            else:
                st.error("Aucun résultat de recherche trouvé. Veuillez essayer une autre requête.")