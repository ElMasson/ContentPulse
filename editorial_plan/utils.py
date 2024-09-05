# editorial_plan/utils.py

from psycopg2.extras import RealDictCursor
import logging
import pandas as pd
import ast


logger = logging.getLogger(__name__)

def get_article_details(conn, article_id):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM contentpulse.editorial_plan WHERE id = %s", (article_id,))
            return cur.fetchone()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails de l'article : {e}")
        return None

def get_branding_info(conn):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM contentpulse.branding LIMIT 1")
            return cur.fetchone()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de branding : {e}")
        return {}

def get_personas(conn):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM contentpulse.personas WHERE is_selected = TRUE")
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des personas : {e}")
        return []

def get_build_matrix(conn):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM contentpulse.build_matrix")
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la matrice BUILD : {e}")
        return []

def get_business_objectives(conn):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM contentpulse.business_objectives WHERE is_selected = TRUE")
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