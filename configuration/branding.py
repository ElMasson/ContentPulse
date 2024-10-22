#configuration/branding.py

import streamlit as st
from .utils import create_table_if_not_exists, get_existing_data, save_data

def branding_config(conn):
    st.header("Configuration du Branding")

    create_table_if_not_exists(conn, 'branding', [
        'company_name TEXT',
        'logo_url TEXT',
        'primary_color TEXT',
        'secondary_color TEXT',
        'font TEXT',
        'core_values TEXT',
        'brand_personality TEXT',
        'tone_of_voice TEXT',
        'value_proposition TEXT',
        'target_audience TEXT'
    ])

    existing_data = get_existing_data(conn, 'branding', company_id)

    company_name = st.text_input("Nom de l'entreprise", value=existing_data.get('company_name', ''))
    logo_url = st.text_input("URL du logo", value=existing_data.get('logo_url', ''))
    primary_color = st.color_picker("Couleur principale", value=existing_data.get('primary_color', '#000000'))
    secondary_color = st.color_picker("Couleur secondaire", value=existing_data.get('secondary_color', '#FFFFFF'))
    font = st.selectbox("Police de caractère", ["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana"],
                        index=["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana"].index(
                            existing_data.get('font', 'Arial')) if existing_data.get('font') else 0)
    core_values = st.text_area("Valeurs fondatrices", value=existing_data.get('core_values', ''))
    brand_personality = st.text_area("Personnalité de marque", value=existing_data.get('brand_personality', ''))
    tone_of_voice = st.text_area("Ton de voix", value=existing_data.get('tone_of_voice', ''))
    value_proposition = st.text_area("Proposition de valeur", value=existing_data.get('value_proposition', ''))
    target_audience = st.text_area("Public cible", value=existing_data.get('target_audience', ''))

    if st.button("Sauvegarder le Branding"):
        data = {
            'company_id': company_id,  # Ajouter l'ID de l'entreprise
            'company_name': company_name,
            'logo_url': logo_url,
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'font': font,
            'core_values': core_values,
            'brand_personality': brand_personality,
            'tone_of_voice': tone_of_voice,
            'value_proposition': value_proposition,
            'target_audience': target_audience
        }
        save_data(conn, 'branding', data)
        st.success("Configuration du branding sauvegardée avec succès!")