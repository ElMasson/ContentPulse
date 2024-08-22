
# editorial_plan/delete_entry.py
import streamlit as st


def delete_entry(conn, df):
    st.subheader("Supprimer une entrée")

    entry_id = st.selectbox("Sélectionnez l'entrée à supprimer", df['id'].tolist())

    if st.button("Supprimer"):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM editorial_plan WHERE id=%s", (entry_id,))
        conn.commit()
        st.success("Entrée supprimée avec succès!")


