
# custom_fields/remove_field.py
import streamlit as st
from database.utils import remove_custom_field_from_table


def remove_custom_field(conn):
    st.subheader("Supprimer un champ personnalisé")

    with conn.cursor() as cur:
        cur.execute("SELECT field_name FROM custom_fields")
        custom_fields = [row[0] for row in cur.fetchall()]

    if not custom_fields:
        st.warning("Aucun champ personnalisé à supprimer.")
        return

    field_to_remove = st.selectbox("Sélectionnez le champ à supprimer", custom_fields)

    if st.button("Supprimer le champ"):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM custom_fields WHERE field_name=%s", (field_to_remove,))
        remove_custom_field_from_table(conn, field_to_remove)
        st.success(f"Champ personnalisé '{field_to_remove}' supprimé avec succès!")

