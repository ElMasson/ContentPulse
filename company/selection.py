import streamlit as st
from database.connection import get_connection


def get_user_companies(user_id):
    """Récupère les entreprises auxquelles l'utilisateur a accès."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, cu.role
                FROM contentpulse.companies c
                JOIN contentpulse.company_users cu ON c.id = cu.company_id
                WHERE cu.user_id = %s
                ORDER BY c.name
            """, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()


def create_company(name, description, user_id):
    """Crée une nouvelle entreprise et associe l'utilisateur comme admin."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Créer l'entreprise
            cur.execute(
                "INSERT INTO contentpulse.companies (name, description) VALUES (%s, %s) RETURNING id",
                (name, description)
            )
            company_id = cur.fetchone()[0]

            # Associer l'utilisateur comme admin
            cur.execute(
                "INSERT INTO contentpulse.company_users (user_id, company_id, role) VALUES (%s, %s, 'admin')",
                (user_id, company_id)
            )
            conn.commit()
            return True, company_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def company_selector():
    """Interface de sélection d'entreprise."""
    if 'current_company_id' not in st.session_state:
        st.session_state.current_company_id = None

    user_id = st.session_state.user['id']
    companies = get_user_companies(user_id)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Sélection de l'entreprise")

    # Liste déroulante des entreprises
    company_options = {comp[1]: comp[0] for comp in companies}
    company_options["➕ Créer une nouvelle entreprise"] = "new"

    selected_company = st.sidebar.selectbox(
        "Entreprise",
        options=list(company_options.keys()),
        index=0 if st.session_state.current_company_id else 0
    )

    if selected_company == "➕ Créer une nouvelle entreprise":
        st.sidebar.markdown("### Création d'entreprise")
        company_name = st.sidebar.text_input("Nom de l'entreprise")
        company_description = st.sidebar.text_area("Description")

        if st.sidebar.button("Créer"):
            if company_name:
                success, result = create_company(company_name, company_description, user_id)
                if success:
                    st.session_state.current_company_id = result
                    st.success(f"Entreprise '{company_name}' créée avec succès!")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de la création de l'entreprise: {result}")
            else:
                st.error("Le nom de l'entreprise est requis")
    else:
        st.session_state.current_company_id = company_options[selected_company]

    return st.session_state.current_company_id