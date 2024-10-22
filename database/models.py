import logging
import hashlib
from psycopg2 import sql

def execute_query(conn, query, params=None):
    with conn.cursor() as cur:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
    conn.commit()

def initialize_database(conn):
    # Création du schéma
    execute_query(conn, "CREATE SCHEMA IF NOT EXISTS contentpulse")

    # Table users
    execute_query(conn, """
        CREATE TABLE IF NOT EXISTS contentpulse.users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP WITH TIME ZONE
        )
    """)

    # Création de l'utilisateur admin par défaut (seulement s'il n'existe pas)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contentpulse.users WHERE username = 'admin'")
        if not cur.fetchone():
            execute_query(
                conn,
                "INSERT INTO contentpulse.users (username, password, role) VALUES (%s, %s, %s)",
                ("admin", hashlib.sha256("admin123".encode()).hexdigest(), "admin")
            )

    # Tables principales
    tables = {
        "companies": """
            CREATE TABLE IF NOT EXISTS contentpulse.companies (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "company_users": """
            CREATE TABLE IF NOT EXISTS contentpulse.company_users (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES contentpulse.users(id),
                company_id INTEGER REFERENCES contentpulse.companies(id),
                role TEXT NOT NULL,
                UNIQUE(user_id, company_id)
            )
        """,
        "editorial_plan": """
            CREATE TABLE IF NOT EXISTS contentpulse.editorial_plan (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES contentpulse.companies(id),
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
        """,
        "personas": """
            CREATE TABLE IF NOT EXISTS contentpulse.personas (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES contentpulse.companies(id),
                name TEXT NOT NULL,
                is_selected BOOLEAN DEFAULT FALSE,
                UNIQUE(company_id, name)
            )
        """,
        "content_types": """
            CREATE TABLE IF NOT EXISTS contentpulse.content_types (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES contentpulse.companies(id),
                name TEXT NOT NULL,
                is_selected BOOLEAN DEFAULT FALSE,
                target_per_week INTEGER DEFAULT 0,
                max_frequency_per_week INTEGER DEFAULT 0,
                max_frequency_per_month INTEGER DEFAULT 0,
                UNIQUE(company_id, name)
            )
        """,
        "build_matrix": """
            CREATE TABLE IF NOT EXISTS contentpulse.build_matrix (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES contentpulse.companies(id),
                persona TEXT NOT NULL,
                pain_points TEXT,
                pain_killers TEXT,
                UNIQUE(company_id, persona)
            )
        """,
        "business_objectives": """
            CREATE TABLE IF NOT EXISTS contentpulse.business_objectives (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES contentpulse.companies(id),
                name TEXT NOT NULL,
                is_selected BOOLEAN DEFAULT FALSE,
                UNIQUE(company_id, name)
            )
        """,
        "branding": """
            CREATE TABLE IF NOT EXISTS contentpulse.branding (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES contentpulse.companies(id),
                company_name TEXT,
                logo_url TEXT,
                primary_color TEXT,
                secondary_color TEXT,
                font TEXT,
                core_values TEXT,
                brand_personality TEXT,
                tone_of_voice TEXT,
                value_proposition TEXT,
                target_audience TEXT,
                UNIQUE(company_id)
            )
        """
    }

    # Créer toutes les tables en une seule transaction
    with conn.cursor() as cur:
        for query in tables.values():
            cur.execute(query)
    conn.commit()