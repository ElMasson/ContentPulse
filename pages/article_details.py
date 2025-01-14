import streamlit as st
import sys
import os
from datetime import datetime

# Ajouter le chemin du projet parent au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection
from editorial_plan.utils import (
    get_article_details,
    get_branding_info,
    get_personas,
    get_build_matrix,
    get_business_objectives,
    generate_content_prompt  # Ajout de l'import
)
from content_suggestions.ai_integration import generate_ai_suggestions



def main():
    st.title("Détails de l'article")

    # Récupérer l'ID de l'article et le company_id
    article_id = st.session_state.get('selected_article_id')
    company_id = st.session_state.get('current_company_id')

    if article_id is None:
        st.error("Aucun article sélectionné.")
        if st.button("Retour au plan éditorial"):
            st.switch_page("main.py")
        return

    # Connexion à la base de données
    conn = get_connection()

    try:
        # Récupérer les détails de l'article
        article = get_article_details(conn, article_id, company_id)

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

        # Récupérer les informations nécessaires pour le prompt en incluant company_id
        branding_info = get_branding_info(conn, company_id)
        personas = get_personas(conn, company_id)
        build_matrix = get_build_matrix(conn, company_id)
        business_objectives = get_business_objectives(conn, company_id)

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

                    # Sauvegarder le contenu généré avec le company_id
                    save_generated_content(conn, article_id, company_id, generated_content)

                else:
                    st.error("Une erreur s'est produite lors de la génération du contenu. Veuillez réessayer.")

        # Bouton pour revenir au plan éditorial
        if st.button("Retour au plan éditorial"):
            st.switch_page("main.py")

    finally:
        conn.close()


def save_generated_content(conn, article_id, company_id, content):
    """Sauvegarde le contenu généré dans la base de données."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO contentpulse.generated_content 
                (article_id, company_id, content, created_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (article_id, company_id, content))
        conn.commit()
        st.success("Contenu généré sauvegardé avec succès!")
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du contenu : {str(e)}")


if __name__ == "__main__":
    main()