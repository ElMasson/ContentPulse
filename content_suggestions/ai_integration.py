#content_suggestions/ai_integration.py

import logging
import os
from openai import OpenAI

# Configurez le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configurez votre clé API OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_suggestions(prompt):
    try:
        logger.info("Tentative de génération de suggestions avec OpenAI")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en marketing de contenu qui génère des suggestions de contenu pour un plan éditorial."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=10000
        )
        logger.info("Suggestions générées avec succès")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur lors de la génération des suggestions : {e}")
        return None