#configuration/branding.py

import streamlit as st
from psycopg2.extras import RealDictCursor

def get_company_name(conn, company_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name FROM contentpulse.companies 
            WHERE id = %s
        """, (company_id,))
        result = cur.fetchone()
        return result[0] if result else ""

def branding_config(conn, company_id):
    st.header("Configuration du Branding")


def branding_config(conn, company_id):
    st.header("Configuration du Branding")

    # Récupérer le nom de l'entreprise
    company_name = get_company_name(conn, company_id)

    # Récupérer les données existantes
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM contentpulse.branding 
            WHERE company_id = %s
        """, (company_id,))
        existing_data = cur.fetchone() or {}

    # Afficher le nom de l'entreprise (non éditable)
    st.text_input("Nom de l'entreprise", value=company_name, disabled=True, key=f"brand_company_name_{company_id}")

    # Autres champs du formulaire
    logo_url = st.text_input("URL du logo", value=existing_data.get('logo_url', ''), key=f"brand_logo_{company_id}")
    primary_color = st.color_picker("Couleur principale", value=existing_data.get('primary_color', '#000000'),
                                    key=f"brand_primary_{company_id}")
    secondary_color = st.color_picker("Couleur secondaire", value=existing_data.get('secondary_color', '#FFFFFF'),
                                      key=f"brand_secondary_{company_id}")

    font_options = ["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana"]
    current_font = existing_data.get('font', 'Arial')
    font = st.selectbox(
        "Police de caractère",
        options=font_options,
        index=font_options.index(current_font) if current_font in font_options else 0,
        key=f"brand_font_{company_id}"
    )

    core_values = st.text_area("Valeurs fondatrices", value=existing_data.get('core_values', ''),
                               key=f"brand_values_{company_id}")
    brand_personality = st.text_area("Personnalité de marque", value=existing_data.get('brand_personality', ''),
                                     key=f"brand_personality_{company_id}")
    tone_of_voice = st.text_area("Ton de voix", value=existing_data.get('tone_of_voice', ''),
                                 key=f"brand_tone_{company_id}")
    value_proposition = st.text_area("Proposition de valeur", value=existing_data.get('value_proposition', ''),
                                     key=f"brand_value_prop_{company_id}")
    target_audience = st.text_area("Public cible", value=existing_data.get('target_audience', ''),
                                   key=f"brand_audience_{company_id}")

    if st.button("Sauvegarder le Branding", key=f"brand_save_{company_id}"):
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contentpulse.branding
                    (company_id, company_name, logo_url, primary_color, secondary_color,
                     font, core_values, brand_personality, tone_of_voice,
                     value_proposition, target_audience)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (company_id) DO UPDATE
                    SET company_name = EXCLUDED.company_name,
                        logo_url = EXCLUDED.logo_url,
                        primary_color = EXCLUDED.primary_color,
                        secondary_color = EXCLUDED.secondary_color,
                        font = EXCLUDED.font,
                        core_values = EXCLUDED.core_values,
                        brand_personality = EXCLUDED.brand_personality,
                        tone_of_voice = EXCLUDED.tone_of_voice,
                        value_proposition = EXCLUDED.value_proposition,
                        target_audience = EXCLUDED.target_audience
                """, (
                    company_id, company_name, logo_url, primary_color, secondary_color,
                    font, core_values, brand_personality, tone_of_voice,
                    value_proposition, target_audience
                ))
            conn.commit()
            st.success("Configuration du branding sauvegardée avec succès!")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {str(e)}")