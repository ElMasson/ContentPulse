# editorial_plan/utils.py
def get_custom_fields(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT field_name, field_type FROM custom_fields")
        return cur.fetchall()