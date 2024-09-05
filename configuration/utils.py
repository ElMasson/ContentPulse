import psycopg2
from psycopg2 import sql

def create_table_if_not_exists(conn, table_name, columns):
    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                {}
            )
        """).format(
            sql.Identifier('contentpulse', table_name),
            sql.SQL(', ').join(sql.SQL('{} {}').format(sql.Identifier(col.split()[0]), sql.SQL(col.split()[1])) for col in columns)
        ))
    conn.commit()

def get_existing_data(conn, table_name, condition=None, multiple=False):
    with conn.cursor() as cur:
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier('contentpulse', table_name))
        if condition:
            query += sql.SQL(" WHERE {}").format(sql.SQL(condition))
        cur.execute(query)
        if multiple:
            return [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
        else:
            row = cur.fetchone()
            return dict(zip([column[0] for column in cur.description], row)) if row else {}

def save_data(conn, table_name, data, condition=None):
    with conn.cursor() as cur:
        if condition:
            # Update existing record
            set_clause = sql.SQL(", ").join(
                sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(k))
                for k in data.keys()
            )
            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier('contentpulse', table_name),
                set_clause,
                sql.SQL(condition)
            )
        else:
            # Insert new record
            columns = sql.SQL(", ").join(map(sql.Identifier, data.keys()))
            values = sql.SQL(", ").join(sql.Placeholder() * len(data))
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier('contentpulse', table_name),
                columns,
                values
            )
        cur.execute(query, data)
    conn.commit()