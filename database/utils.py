
# database/utils.py
from psycopg2 import sql


def add_custom_field_to_table(conn, field_name, field_type):
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("ALTER TABLE editorial_plan ADD COLUMN {} {}").format(
                sql.Identifier(field_name),
                sql.SQL(field_type)
            )
        )
    conn.commit()


def remove_custom_field_from_table(conn, field_name):
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("ALTER TABLE editorial_plan DROP COLUMN {}").format(
                sql.Identifier(field_name)
            )
        )
    conn.commit()