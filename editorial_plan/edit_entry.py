
# editorial_plan/edit_entry.py
import streamlit as st


def edit_entry(conn, id, data):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE contentpulse.editorial_plan
            SET title=%s, content_type=%s, theme=%s, keywords=%s, author=%s, planned_publication_date=%s, status=%s, target_persona=%s, customer_journey_stage=%s, main_cta=%s, url=%s, views=%s, engagements=%s, conversions=%s
            WHERE id=%s
        """, (data['title'], data['content_type'], data['theme'], data['keywords'], data['author'], data['planned_publication_date'], data['status'], data['target_persona'], data['customer_journey_stage'], data['main_cta'], data['url'], data['views'], data['engagements'], data['conversions'], id))
    conn.commit()
