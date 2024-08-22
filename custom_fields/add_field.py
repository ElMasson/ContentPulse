
# custom_fields/add_field.py
import streamlit as st
from database.utils import add_custom_field_to_table


def add_custom_field(conn):
    st.subheader("Ajouter un champ personnalisé")

    field_name = st.text_input("Nom du champ")
    field_type = st.selectbox("Type du champ", ["TEXT", "INTEGER", "FLOAT", "DATE", "BOOLEAN"])

    if st.button("Ajouter le champ"):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO custom_fields (field_name, field_type) VALUES (%s, %s)", (field_name, field_type))
        add_custom_field_to_table(conn, field_name, field_type)
        st.success(f"Champ personnalisé '{field_name}' ajouté avec succès!")

