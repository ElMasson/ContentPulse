#database/models.py

import logging
from psycopg2 import sql

logger = logging.getLogger(__name__)

def execute_query(conn, query, params=None):
    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
        conn.commit()
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête : {e}")
        conn.rollback()
        raise

def create_schema_if_not_exists(conn):
    execute_query(conn, "CREATE SCHEMA IF NOT EXISTS contentpulse")
    logger.info("Schema 'contentpulse' créé ou déjà existant")

def check_editorial_plan_table(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('contentpulse.editorial_plan')")
        if cur.fetchone()[0] is None:
            logger.warning("La table editorial_plan n'existe pas. Création de la table.")
            execute_query(conn, """
                CREATE TABLE contentpulse.editorial_plan (
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
            """)
            logger.info("Table editorial_plan créée avec succès.")
        else:
            logger.info("La table editorial_plan existe déjà.")

    execute_query(conn, "GRANT ALL PRIVILEGES ON TABLE contentpulse.editorial_plan TO current_user")
    logger.info("Permissions accordées sur la table editorial_plan.")

def check_and_initialize_table(conn, table_name, create_table_query, default_data_query=None, default_data_params=None):
    logger.info(f"Vérification de la table {table_name}")
    execute_query(conn, create_table_query)
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM contentpulse.{table_name}")
        count = cur.fetchone()[0]
    if count == 0 and default_data_query:
        execute_query(conn, default_data_query, default_data_params)
        logger.info(f"Table {table_name} initialisée avec des données par défaut")
    else:
        logger.info(f"Table {table_name} contient déjà {count} entrées")

def initialize_database(conn):
    logger.info("Début de l'initialisation de la base de données")
    try:
        create_schema_if_not_exists(conn)
        check_editorial_plan_table(conn)

        # Personas
        check_and_initialize_table(
            conn, "personas",
            """
            CREATE TABLE IF NOT EXISTS contentpulse.personas (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                is_selected BOOLEAN DEFAULT FALSE
            )
            """,
            """
            INSERT INTO contentpulse.personas (name, is_selected) 
            VALUES (%s, TRUE)
            """,
            [("Dirigeant d'entreprise",), ("Responsable marketing",), ("Responsable des ventes",), ("Responsable IT",), ("Entrepreneur",)]
        )

        # Content Types
        check_and_initialize_table(
            conn, "content_types",
            """
            CREATE TABLE IF NOT EXISTS contentpulse.content_types (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                is_selected BOOLEAN DEFAULT FALSE,
                target_per_week INTEGER DEFAULT 0,
                max_frequency_per_week INTEGER DEFAULT 0,
                max_frequency_per_month INTEGER DEFAULT 0
            )
            """,
            """
            INSERT INTO contentpulse.content_types 
            (name, is_selected, target_per_week, max_frequency_per_week, max_frequency_per_month)
            VALUES (%s, TRUE, 1, 2, 8)
            """,
            [("Article de blog",), ("Page web",), ("E-book",), ("Infographie",), ("Vidéo",)]
        )

        # Build Matrix
        check_and_initialize_table(
            conn, "build_matrix",
            """
            CREATE TABLE IF NOT EXISTS contentpulse.build_matrix (
                id SERIAL PRIMARY KEY,
                persona TEXT,
                pain_points TEXT,
                pain_killers TEXT
            )
            """,
            """
            INSERT INTO contentpulse.build_matrix (persona, pain_points, pain_killers)
            VALUES ('Dirigeant d''entreprise', 'Manque de visibilité sur les performances', 'Tableau de bord personnalisé')
            """
        )

        # Business Objectives
        check_and_initialize_table(
            conn, "business_objectives",
            """
            CREATE TABLE IF NOT EXISTS contentpulse.business_objectives (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                is_selected BOOLEAN DEFAULT FALSE
            )
            """,
            """
            INSERT INTO contentpulse.business_objectives (name, is_selected) 
            VALUES (%s, TRUE)
            """,
            [("Augmenter le trafic",), ("Générer des leads",), ("Améliorer la notoriété de la marque",)]
        )

        # Branding
        check_and_initialize_table(
            conn, "branding",
            """
            CREATE TABLE IF NOT EXISTS contentpulse.branding (
                id SERIAL PRIMARY KEY,
                company_name TEXT,
                logo_url TEXT,
                primary_color TEXT,
                secondary_color TEXT,
                font TEXT,
                core_values TEXT,
                brand_personality TEXT,
                tone_of_voice TEXT,
                value_proposition TEXT,
                target_audience TEXT
            )
            """,
            """
            INSERT INTO contentpulse.branding 
            (company_name, core_values, brand_personality, tone_of_voice, value_proposition)
            VALUES 
            ('Nom de l''entreprise', 'Innovation, Qualité, Service client', 'Professionnel et innovant', 'Formel mais accessible', 'Nous aidons les entreprises à optimiser leurs processus')
            """
        )

        for table in ['personas', 'content_types', 'business_objectives']:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM contentpulse.{table} WHERE is_selected = TRUE")
                if cur.fetchone()[0] == 0:
                    cur.execute(f"UPDATE contentpulse.{table} SET is_selected = TRUE WHERE id = (SELECT id FROM contentpulse.{table} LIMIT 1)")
                    logger.info(f"Une entrée de la table {table} a été automatiquement sélectionnée")

        logger.info("Fin de l'initialisation de la base de données")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données : {e}")
        raise