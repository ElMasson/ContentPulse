
# editorial_plan/add_entry.py
import streamlit as st


def add_entry(conn, data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO contentpulse.editorial_plan (title, content_type, theme, keywords, author, planned_publication_date, status, target_persona, customer_journey_stage, main_cta, url, views, engagements, conversions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['title'], data['content_type'], data['theme'], data['keywords'], data['author'], data['planned_publication_date'], data['status'], data['target_persona'], data['customer_journey_stage'], data['main_cta'], data['url'], data['views'], data['engagements'], data['conversions']))
    conn.commit()
