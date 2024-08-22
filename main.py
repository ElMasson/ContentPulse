import streamlit as st
import pandas as pd
from database.connection import get_connection
from database.models import initialize_database
from editorial_plan.display import display_editorial_plan
import psycopg2

# Configuration de la page Streamlit
st.set_page_config(page_title="ContentPulse", page_icon="📅", layout="wide")

# Appliquer un style personnalisé
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .st-bw {
        border-radius: 8px;
        overflow: hidden;
    }
    .st-emotion-cache-xm9au6 {
        border: 1px solid #ddd;
    }
    .st-emotion-cache-xm9au6 th {
        background-color: #009879;
        color: white;
        font-weight: bold;
    }
    .st-emotion-cache-xm9au6 tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    .sidebar-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem 0;
    }
    .sidebar-logo img {
        max-width: 80%;
        height: auto;
    }
</style>
""", unsafe_allow_html=True)

# Panneau latéral
with st.sidebar:
    # Logo
    st.markdown(
        '<div class="sidebar-logo"><img src="https://via.placeholder.com/150x150.png?text=ContentPulse" alt="ContentPulse Logo"/></div>',
        unsafe_allow_html=True)

    # Éléments de configuration
    with st.expander("Configuration"):
        st.markdown("### Branding")
        st.image("https://via.placeholder.com/30x30.png?text=B", width=30)
        st.markdown("### Listes de personas")
        st.image("https://via.placeholder.com/30x30.png?text=P", width=30)
        st.markdown("### Matrice BUILD")
        st.image("https://via.placeholder.com/30x30.png?text=M", width=30)

# Contenu principal
st.title("ContentPulse - Pilotage du Plan Éditorial")

# Connexion à la base de données et initialisation
try:
    conn = get_connection()
    initialize_database(conn)
except psycopg2.Error as e:
    st.error(f"Erreur de connexion à la base de données : {e}")
    st.stop()

# Définition des colonnes fonctionnelles souhaitées
desired_columns = [
    "Titre", "Type de contenu", "Thème", "Mots-clés", "Auteur",
    "Date de publication prévue", "Statut", "Persona cible",
    "Étape du parcours client", "Call-to-Action principal"
]

# Affichage et gestion du plan éditorial
try:
    df = display_editorial_plan(conn)

    # Supprimer la colonne 'id' si elle existe
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # Mapper les colonnes existantes aux colonnes souhaitées
    column_mapping = {}
    for i, col in enumerate(df.columns):
        if i < len(desired_columns):
            column_mapping[col] = desired_columns[i]
        else:
            column_mapping[col] = col  # Garder le nom original pour les colonnes supplémentaires

    df = df.rename(columns=column_mapping)

    # Ajouter les colonnes manquantes
    for col in desired_columns:
        if col not in df.columns:
            df[col] = ""

    # Réordonner les colonnes
    df = df[desired_columns + [col for col in df.columns if col not in desired_columns]]

    # Convertir la colonne 'Date de publication prévue' en datetime
    df['Date de publication prévue'] = pd.to_datetime(df['Date de publication prévue'], errors='coerce')

except Exception as e:
    st.warning(f"Erreur lors de la récupération du plan éditorial : {e}")
    df = pd.DataFrame(columns=desired_columns)

# Ajouter une ligne vide si le DataFrame est vide
if df.empty:
    df = pd.DataFrame([[''] * len(df.columns)], columns=df.columns)
    df['Date de publication prévue'] = pd.NaT

# Affichage de la table éditable
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Date de publication prévue": st.column_config.DateColumn(
            "Date de publication prévue",
            min_value=pd.Timestamp("2020-01-01"),
            max_value=pd.Timestamp("2030-12-31"),
            format="DD/MM/YYYY",
        ),
    }
)

# Bouton pour sauvegarder les modifications
if st.button("Sauvegarder les modifications"):
    # Ici, vous devriez ajouter la logique pour sauvegarder les modifications dans la base de données
    st.success("Modifications sauvegardées avec succès!")

# Fermeture de la connexion
if 'conn' in locals():
    conn.close()

# Instructions d'utilisation
st.markdown("""
## Comment utiliser ContentPulse

1. **Modifier une entrée** : Cliquez sur une cellule dans la table pour la modifier.
2. **Ajouter une nouvelle ligne** : Cliquez sur le bouton '+' en bas de la table pour ajouter une nouvelle ligne.
3. **Supprimer une ligne** : Cliquez sur le 'x' à gauche de la ligne que vous souhaitez supprimer.
4. **Sauvegarder les modifications** : Après avoir effectué vos modifications, cliquez sur le bouton "Sauvegarder les modifications".
5. **Configuration** : Utilisez le panneau latéral pour accéder aux paramètres de configuration (fonctionnalités à venir).

N'hésitez pas à adapter votre plan éditorial en fonction de l'évolution de votre stratégie de contenu !
""")

# Pied de page
st.markdown("---")
st.markdown("© 2024 ContentPulse. Tous droits réservés. DATANALYSIS Groupe")