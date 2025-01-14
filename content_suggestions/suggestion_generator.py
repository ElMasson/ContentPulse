#content_suggestions/suggestion_generator.py

import logging
from .ai_integration import generate_ai_suggestions
import json
import pandas as pd
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import io

logger = logging.getLogger(__name__)

def get_data_from_db(conn, company_id):
    data = {}
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            logger.info("Récupération des données de la base de données")

            # Récupérer les personas sélectionnés pour cette entreprise
            cur.execute("""
                SELECT name FROM contentpulse.personas 
                WHERE company_id = %s AND is_selected = TRUE
            """, (company_id,))
            data['personas'] = [row['name'] for row in cur.fetchall()]

            # Récupérer les types de contenu sélectionnés avec leurs fréquences
            cur.execute("""
                SELECT name, target_per_week, max_frequency_per_week, max_frequency_per_month 
                FROM contentpulse.content_types 
                WHERE company_id = %s AND is_selected = TRUE
            """, (company_id,))
            data['content_types'] = [dict(row) for row in cur.fetchall()]

            # Récupérer la matrice BUILD
            cur.execute("""
                SELECT * FROM contentpulse.build_matrix 
                WHERE company_id = %s
            """, (company_id,))
            data['build_matrix'] = [dict(row) for row in cur.fetchall()]

            # Récupérer les objectifs métier sélectionnés
            cur.execute("""
                SELECT name FROM contentpulse.business_objectives 
                WHERE company_id = %s AND is_selected = TRUE
            """, (company_id,))
            data['business_objectives'] = [row['name'] for row in cur.fetchall()]

            # Récupérer les informations de branding
            cur.execute("""
                SELECT * FROM contentpulse.branding 
                WHERE company_id = %s LIMIT 1
            """, (company_id,))
            data['branding'] = dict(cur.fetchone() or {})

        logger.info("Données récupérées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données : {e}")
    return data

def generate_content_suggestions(conn, company_id):
    data = get_data_from_db(conn, company_id)
    logger.info(f"Données récupérées : {json.dumps(data, default=str)}")

    if not data or all(not value for value in data.values()):
        logger.error("Données insuffisantes pour générer des suggestions")
        return None

    required_keys = ['personas', 'content_types', 'business_objectives', 'build_matrix', 'branding']
    missing_keys = [key for key in required_keys if key not in data or not data[key]]
    if missing_keys:
        logger.error(f"Données manquantes : {', '.join(missing_keys)}")
        return None

    today = datetime.now().date()
    future_dates = [today + timedelta(days=i * 7) for i in range(1, 5)]  # 4 semaines dans le futur

    content_types_info = "\n".join([
        f"- {ct['name']}: cible par semaine: {ct['target_per_week']}, "
        f"fréquence max par semaine: {ct['max_frequency_per_week']}, "
        f"fréquence max par mois: {ct['max_frequency_per_month']}"
        for ct in data['content_types']
    ])

    prompt = f"""
    En tant qu'expert en marketing de contenu, générez des suggestions de contenu pour les 4 prochaines semaines basées sur les informations suivantes :

    Personas : {', '.join(data['personas'])}
    Types de contenu et leurs fréquences :
    {content_types_info}
    Objectifs métier : {', '.join(data['business_objectives'])}

    Informations de branding :
    {json.dumps(data['branding'], indent=2)}

    Matrice BUILD :
    {json.dumps(data['build_matrix'], indent=2)}

    Générez un tableau de suggestions de contenu variées qui respectent les contraintes de fréquence pour chaque type de contenu.
    Le tableau doit avoir les colonnes suivantes, séparées par des virgules et entre guillemets si nécessaire :
    "title","content_type","theme","keywords","author","planned_publication_date","status","target_persona","customer_journey_stage","main_cta","url","views","engagements","conversions"

    Assurez-vous que :
    - Chaque suggestion reflète la personnalité de la marque, son ton de voix, et sa proposition de valeur.
    - Le contenu est adapté au public cible et aux personas spécifiés.
    - Les dates de publication prévues sont dans le futur, en utilisant les dates suivantes : {', '.join([d.strftime('%Y-%m-%d') for d in future_dates])}
    - Le nombre de suggestions pour chaque type de contenu respecte les limites de fréquence spécifiées.
    - Le statut est "Planifié" pour toutes les suggestions.
    - Les champs views, engagements, et conversions sont vides.

    Répondez uniquement avec le tableau au format CSV, en commençant par la ligne d'en-tête, sans aucun texte supplémentaire.
    """

    logger.info("Envoi de la requête à l'API OpenAI")
    suggestions_csv = generate_ai_suggestions(prompt)
    if suggestions_csv:
        logger.info("Suggestions générées avec succès")
        try:
            df = pd.read_csv(io.StringIO(suggestions_csv))
            df['company_id'] = company_id  # Ajouter le company_id aux suggestions
            logger.info(f"DataFrame créé avec succès. Dimensions : {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la conversion des suggestions en DataFrame : {e}")
            return None
    else:
        logger.error("Échec de la génération des suggestions")
        return None