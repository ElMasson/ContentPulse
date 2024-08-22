import pandas as pd
import psycopg2


def display_editorial_plan(conn):
    try:
        query = "SELECT * FROM contentpulse.editorial_plan"
        df = pd.read_sql_query(query, conn)

        # Si le DataFrame est vide, créer 10 lignes vides
        if df.empty:
            empty_data = {col: [''] * 10 for col in [
                'id', 'title', 'content_type', 'theme', 'keywords', 'author',
                'planned_publication_date', 'status', 'target_persona',
                'customer_journey_stage', 'main_cta', 'url', 'views',
                'engagements', 'conversions'
            ]}
            df = pd.DataFrame(empty_data)

        return df
    except psycopg2.Error as e:
        print(f"Erreur lors de la récupération du plan éditorial : {e}")
        # Créer un DataFrame vide avec 10 lignes
        empty_data = {col: [''] * 10 for col in [
            'id', 'title', 'content_type', 'theme', 'keywords', 'author',
            'planned_publication_date', 'status', 'target_persona',
            'customer_journey_stage', 'main_cta', 'url', 'views',
            'engagements', 'conversions'
        ]}
        return pd.DataFrame(empty_data)