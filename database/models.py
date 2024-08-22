import psycopg2
from psycopg2 import sql


def initialize_database(conn):
    with conn.cursor() as cur:
        # Créer le schéma s'il n'existe pas
        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
            sql.Identifier('contentpulse')
        ))

        # Créer la table dans le schéma spécifié
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.editorial_plan (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                theme TEXT,
                keywords TEXT[],
                author TEXT,
                planned_publication_date DATE,
                status TEXT,
                target_persona TEXT,
                customer_journey_stage TEXT,
                main_cta TEXT,
                url TEXT,
                views INTEGER,
                engagements INTEGER,
                conversions INTEGER
            )
        """).format(sql.Identifier('contentpulse')))
    conn.commit()