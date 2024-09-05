#database/connection.py

import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les informations de connexion depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def get_connection():
    """
    Crée et retourne une connexion à la base de données PostgreSQL.

    Returns:
        psycopg2.extensions.connection: Un objet de connexion à la base de données.
    """
    try:
        # Établir la connexion
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            cursor_factory=DictCursor
        )

        # Configurer la connexion pour utiliser le schéma 'contentpulse'
        with conn.cursor() as cur:
            cur.execute("SET search_path TO contentpulse, public;")
        conn.commit()

        return conn
    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        raise

def close_connection(conn):
    """
    Ferme la connexion à la base de données.

    Args:
        conn (psycopg2.extensions.connection): La connexion à fermer.
    """
    if conn:
        conn.close()
        print("Connexion à la base de données fermée.")