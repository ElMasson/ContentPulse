# editorial_plan/utils.py

from psycopg2.extras import RealDictCursor
import logging
import pandas as pd
import ast



logger = logging.getLogger(__name__)

def get_article_details(conn, article_id, company_id):
    """Récupère les détails d'un article en tenant compte de l'entreprise."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM contentpulse.editorial_plan 
                WHERE id = %s AND company_id = %s
            """, (article_id, company_id))
            article = cur.fetchone()
            if article and 'keywords' in article:
                article['keywords'] = format_keywords(article['keywords'])
            return article
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails de l'article : {e}")
        return None

def get_branding_info(conn, company_id):
    """Récupère les informations de branding pour une entreprise."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM contentpulse.branding 
                WHERE company_id = %s 
                LIMIT 1
            """, (company_id,))
            return cur.fetchone()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de branding : {e}")
        return {}

def get_personas(conn, company_id):
    """Récupère les personas sélectionnés pour une entreprise."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM contentpulse.personas 
                WHERE company_id = %s AND is_selected = TRUE
            """, (company_id,))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des personas : {e}")
        return []

def get_build_matrix(conn, company_id):
    """Récupère la matrice BUILD pour une entreprise."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM contentpulse.build_matrix 
                WHERE company_id = %s
            """, (company_id,))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la matrice BUILD : {e}")
        return []


def get_business_objectives(conn, company_id):
    """Récupère les objectifs métier sélectionnés pour une entreprise."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM contentpulse.business_objectives 
                WHERE company_id = %s AND is_selected = TRUE
            """, (company_id,))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des objectifs métier : {e}")
        return []

def clean_and_convert_to_int(value):
    if pd.isna(value) or value == '' or value == ' ""':
        return None
    try:
        return int(float(value))
    except ValueError:
        return None

def parse_keywords(keywords):
    if isinstance(keywords, list):
        return keywords
    elif isinstance(keywords, str):
        try:
            return ast.literal_eval(keywords)
        except:
            return [k.strip() for k in keywords.split(',') if k.strip()]
    return []

def format_keywords(keywords):
    """Formate les mots-clés en liste."""
    if isinstance(keywords, list):
        return keywords
    elif isinstance(keywords, str):
        try:
            return ast.literal_eval(keywords)
        except:
            return [k.strip() for k in keywords.split(',') if k.strip()]
    return [] if pd.isna(keywords) else [str(keywords)]

def generate_content_prompt(article, branding_info, personas, build_matrix, business_objectives):
    """Génère le prompt pour la création de contenu."""
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