import streamlit as st
import json
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from io import BytesIO
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_lottie import st_lottie
import requests
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv

load_dotenv()


# --- Configuration page ---
st.set_page_config(page_title="Plateforme Intelligente", layout="wide")  
st.markdown("""
    <h1 style="
        text-align: center;
        font-size: 48px;
        background: linear-gradient(to right, #61289a, #38afee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    ">
        Prédiction de la durée de vie restante
    </h1>
""", unsafe_allow_html=True)
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://i.pinimg.com/736x/9a/27/a8/9a27a8a15876db90e855f9e5b52ae1cd.jpg");
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    /* === Boutons === */
    .stButton > button {
        background-color: transparent !important;
        color: #6c63ff !important;
        border: 2px solid #6c63ff !important;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        transition: all 0.4s ease;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #6c63ff !important;
        color: white !important;
        transform: scale(1.05);
        box-shadow: 0 0 10px #6c63ff;
        border-color: #4f46e5 !important;
    }

    /* === Champs de texte (input / textarea) === */
    input[type="text"], input[type="email"], textarea, .stTextInput>div>div>input {
        background-color: transparent !important;
        border: 2px solid #6c63ff !important;
        color: #000000 !important;
        border-radius: 12px !important;
        padding: 0.5em !important;
        font-weight: bold;
        transition: all 0.4s ease-in-out;
    }
    input[type="text"]:focus, input[type="email"]:focus, textarea:focus {
        outline: none !important;
        box-shadow: 0 0 10px #6c63ff !important;
        transform: scale(1.02);
    }

    /* === Téléversement de fichier === */
    .stFileUploader > div:first-child {
        border: 2px solid #6c63ff !important;
        background-color: transparent !important;
        border-radius: 12px !important;
        transition: all 0.4s ease;
    }
    .stFileUploader > div:first-child:hover {
        box-shadow: 0 0 10px #6c63ff !important;
        transform: scale(1.02);
    }

    /* === Texte dans les inputs === */
    ::placeholder {
        color: #aaa !important;
    }

    </style>
""", unsafe_allow_html=True)

# --- Charger la config ---
# Cette partie charge le chemin du fichier d'entraînement depuis un fichier de configuration.
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    file_path = config.get("file_path2", "")
except Exception as e:
    st.error(f"Erreur de lecture config.json : {e}")
    st.stop()

# Fonction de style - utilisée pour colorer les cellules selon la classification
def color_classification(val):
    if str(val).lower() == "bon":
        return "background-color: lightgreen; color: black"
    elif str(val).lower() == "moyen":
        return "background-color: khaki; color: black"
    else:
        return "background-color: lightcoral; color: white"
# === Fonction Lottie ===
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")

# --- Choix du mode ---
# Cette partie permet à l'utilisateur de choisir entre le mode utilisateur ou administrateur.
mode = st.sidebar.selectbox("Choisissez le mode d'accès", ["Utilisateur", "Administrateur"])
admin_acces = False

if mode == "Administrateur":    
    st.markdown("""
    <style>
    div[data-testid="stBlock"] > div:has(div[data-testid="stLottieAnimation"]) {
        background-color: rgba(0,0,0,0) !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 auto;
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    if lottie_animation:
        st_lottie(lottie_animation, height=300)
        

    try:
        with open("password_config.json", "r") as f:
            pw_config = json.load(f)
        admin_password = pw_config.get("admin_password", "")
    except:
        st.error("⚠ Impossible de lire password_config.json.")
        st.stop()


    password = st.sidebar.text_input("Mot de passe", type="password")
    if not password:
        st.warning("🔒 Veuillez entrer le mot de passe.")
        st.stop()
    elif password != admin_password:
        st.error("❌ Mot de passe incorrect.")
        st.stop()
    admin_acces = True

# --- Charger données d'entraînement ---
# Ici on charge le fichier Excel d'entraînement pour le modèle de prédiction.

try:
    train_data = pd.read_excel(file_path)
except Exception as e:
    st.error(f"Erreur de chargement du fichier d'entraînement : {e}")
    st.stop()
    # === Style CSS pour agrandir et espacer les options ===
# === Style CSS pour agrandir et espacer les options ===
st.markdown("""
    <style>
    .sidebar .element-container label {
        font-size: 20px !important;
    }

    div[role="radiogroup"] > label {
        margin-bottom: 15px !important;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    selected = option_menu(
        menu_title="",  # Titre du menu
        options=["Accueil", "Assistant Commande", "Chatbot"],  # Pages
        icons=["house", "box", "robot", "bar-chart", "download"],  # Icônes Bootstrap
        menu_icon="cast",  # Icône principale
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#6c63ff", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px"},
            "nav-link-selected": {"background-color": "#6c63ff", "color": "white"},
        }
    )

# === 1. Accueil ===
if selected == "Accueil":
    st.markdown("<h1 style='text-align: center; color: #7B68EE;'>Bienvenue</h1>", unsafe_allow_html=True)
    st.markdown("""
<style>
div[data-testid="stBlock"] > div:has(div[data-testid="stLottieAnimation"]) {
    background-color: rgba(0, 0, 0, 0) !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 auto;
    display: flex;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)


    if lottie_animation:
        st_lottie(lottie_animation, height=300)


# --- Téléversement ---
# Cette section permet à l'utilisateur de téléverser un fichier Excel contenant ses équipements.
uploaded_file = st.file_uploader("📂 Téléversez votre fichier Excel contenant les équipements", type=["xlsx"])
if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)

        if data.empty:
            st.error("Le fichier Excel est vide.")
            st.stop()

        if 'Date affect.' not in data.columns:
            st.error("La colonne 'Date affect.' est introuvable. Elle est soit manquante, soit a été renommée.")
            st.stop()

        # Colonnes de critères de performance
        criteria_columns = [
            'DEX - Device (DEX - Device)', 'Device — Boot duration (DEX - Device)',
            'Device — Logon (DEX - Device)', 'Device — Logon duration (DEX - Device)',
            'Device — Extended logon duration (DEX - Device)', 'Device — Agents crashes (DEX - Device)',
            'Device — High CPU and memory time (DEX - Device)', 'Device — CPU usage (DEX - Device)',
            'Device — Memory usage (DEX - Device)', 'Device — Application crashes (DEX - Device)'
        ]
        present_criteria = [col for col in criteria_columns if col in data.columns]
        if not present_criteria:
            st.error("Les colonnes liées aux critères de performance sont absentes.")
            st.write("Colonnes attendues :", criteria_columns)
            st.write("Assurez-vous que le fichier contient les colonnes attendues et qu'elles n'ont pas été renommées.")
            st.stop()

        # --- Prétraitement des données ---
        # Cette partie calcule l’âge de l’équipement et la moyenne des critères.
        data['Date affect.'] = pd.to_datetime(data['Date affect.'], errors='coerce')
        data["Âge d'équipement"] = (pd.to_datetime("today") - data['Date affect.']).dt.days / 365
        data["Moyenne critères"] = data[criteria_columns].mean(axis=1)

        st.subheader("📝 Aperçu du fichier téléversé")
        st.markdown("Ci-dessous les 5 premières lignes de votre fichier pour vérification.")
        st.dataframe(data.head())

        # --- Entraînement du modèle ---
        # Le modèle est entraîné sur les données historiques pour prédire la durée de vie restante.
        if not all(col in train_data.columns for col in ["Moyenne critères", "Âge d'équipement", "duree_vie_restante"]):
            st.error("Le fichier d'entraînement doit contenir : Moyenne critères, Âge d'équipement, duree_vie_restante")
            st.stop()

        X = train_data[["Moyenne critères", "Âge d'équipement"]]
        y = train_data["duree_vie_restante"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        mae = mean_absolute_error(y_test, model.predict(X_test))

        # --- Prédictions sur le fichier de l'utilisateur ---
        data["duree_restante"] = model.predict(data[["Moyenne critères", "Âge d'équipement"]])

        def mois_en_annees_mois(mois):
            mois = int(round(mois))
            return f"{mois // 12} an(s) {mois % 12} mois"

        data["age d'équipement (années, mois)"] = data["Âge d'équipement"].apply(lambda x: mois_en_annees_mois(x * 12))
        data["duree restante (années, mois)"] = data["duree_restante"].apply(lambda x: mois_en_annees_mois(x * 12))

        # --- Classification finale ---
        # Cette étape attribue une classe à chaque équipement selon ses performances et son âge.
        def classifier(row):
            age = row["Âge d'équipement"]
            score = row["Moyenne critères"]
            age_class = "Bon" if age < 4 else "Moyen" if age <= 5 else "Mauvais"
            perf_class = "Bon" if score >= 8 else "Moyen" if score >= 5 else "Mauvais"
            if age_class == "Bon" and perf_class == "Bon":
                return "Bon"
            elif age_class == "Moyen" or perf_class == "Moyen":
                return "Moyen"
            else:
                return "Mauvais"

        data["Classification finale"] = data.apply(classifier, axis=1)

        # --- Export Excel ---
        output = BytesIO()
        data.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # --- Interface Administrateur ---
        if admin_acces:
            st.success(f"Modèle entraîné (MAE : {round(mae, 2)} mois)")
            st.subheader("📊 Aperçu")


            st.download_button("📥 Télécharger les résultats", data=output,
                               file_name="résultats_rul.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # --- Filtres latéraux ---
            st.sidebar.header("Filtres")
            filtered = data.copy()
            if "Device type" in data.columns:
                filt = st.sidebar.multiselect("Type", options=data["Device type"].dropna().unique())
                if filt:
                    filtered = filtered[filtered["Device type"].isin(filt)]

            class_filt = st.sidebar.multiselect("Classification", options=data["Classification finale"].unique())
            if class_filt:
                filtered = filtered[filtered["Classification finale"].isin(class_filt)]

            # --- Indicateurs clés ---
            st.metric("📦 Nombre total d'équipements", len(filtered))
            st.metric("🧠 MAE (mois)", round(mae, 2))
            st.metric("📅 Âge moyen (ans)", round(filtered["Âge d'équipement"].mean(), 1))

            # --- Graphiques ---
            fig1 = px.histogram(filtered, x="Classification finale", title="Répartition des classes", color_discrete_sequence=["skyblue"])
            fig2 = px.scatter(filtered, x="age d'équipement (années, mois)", y="Moyenne critères", color="Classification finale", title="Performance vs Âge")
            fig3 = px.histogram(filtered, x="duree restante (années, mois)", nbins=20, title="Distribution durée restante")

            # --- Onglets d'affichage ---
            tab1, tab2, tab3 = st.tabs(["📋 Données", "📊 Graphiques", "📤 Export"])
            with tab1:
                st.dataframe(filtered)
            with tab2:
                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.plotly_chart(fig3, use_container_width=True)
            with tab3:
                st.download_button("📥 Télécharger Excel", data=output,
                                   file_name="résultats_rul.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # --- Interface Utilisateur ---
        elif mode == "Utilisateur" or "Administrateur":
            st.subheader("🔎 Recherche d'un équipement")
            st.markdown("Entrez le numéro de série d’un équipement pour consulter ses prévisions.")
            id_column = "N° série"

            if id_column in data.columns:
                id_input = st.text_input("Veuillez entrer le numéro de série de l'équipement :")
                if id_input:
                    equipement = data[data[id_column] == id_input]
                    if not equipement.empty:
                        st.success("✅ Équipement trouvé. Voici les prévisions :")
                        columns_to_show = [id_column, "Device model","Date affect.","Moyenne critères", 
                                           "age d'équipement (années, mois)", "Classification finale",
                                           "duree restante (années, mois)"]
                        styled = equipement[columns_to_show].style.map(
                            color_classification, subset=["Classification finale"]
                            )

                        st.write(styled)
                    else:
                        st.warning("⚠️ Aucun équipement trouvé avec ce numéro.")
            else:
                st.error(f"La colonne '{id_column}' est manquante dans le fichier.")
    except Exception as e:
        st.error(f"Erreur de traitement du fichier : {e}")
        

# === Fonction d'envoi d'email ===
def envoyer_email(nom, email_utilisateur, message_commande):
    sender_email = "berradaniema@gmail.com"
    expediteur_email = os.getenv("EMAIL")
    mot_de_passe = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["Subject"] = f"Nouvelle commande de {nom}"
    message["From"] = sender_email
    message["To"] = receiver_email

    body = f"""
    Nouvelle commande reçue via le chatbot :

    Nom : {nom}
    Email : {email_utilisateur}

    Commande :
    {message_commande}
    """
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")
        return False



# === 2. Assistant Commande ===
if selected == "Assistant Commande":
    st.subheader("📦 Assistant de commande")
    # Ajoute ici ta logique de prédiction / fichiers
    st.markdown("Entrez votre commande d'équipement ci-dessous. Elle sera envoyée à l'administrateur par email.")

    nom_user = st.text_input("Votre nom", key="nom_input")
    email_user = st.text_input("Votre adresse email", key="email_input")
    commande_text = st.text_area("📝 Détail de la commande (modèle, quantité, urgence, etc.)", key="commande_input")

    if st.button("📩 Envoyer la commande", key="envoyer_btn"):
        if not nom_user or not email_user or not commande_text:
            st.warning("Veuillez remplir tous les champs.")
        else:
            success = envoyer_email(nom_user, email_user, commande_text)
            if success:
                st.success("✅ Email envoyé avec succès.")
            else:
                st.error("❌ Une erreur est survenue lors de l'envoi de l'email.")

# === 3. Chatbot (Local, sans OpenAI) ===

elif selected == "Chatbot":
    st.subheader("🤖 Chatbot")
    # Chatbot UI

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_msg = st.chat_input("Posez une question...")

    def repondre(message):
        message = message.lower()
    
        if "bonjour" in message or "salut" in message:
            return "Bonjour 👋 ! Comment puis-je vous aider ?"
    
        elif "commande" in message:
            return "Pour passer une commande, allez à la section 'Assistant Commande'."
    
        elif "merci" in message:
            return "Avec plaisir 😊"
    
        elif "aide" in message:
            return "Je suis là pour vous aider. Que voulez-vous savoir ?"
    
        elif "classification mauvais" in message or "état mauvais" in message:
            mauvais = data[data["Classification finale"] == "Mauvais"]
            if not mauvais.empty:
                return "Voici les équipements ayant une classification 'Mauvais' :\n" + \
                   "\n".join(mauvais["N° série"].tolist())
        elif "classification bon" in message or "état bon" in message:
            mauvais = data[data["Classification finale"] == "Bon"]
            if not mauvais.empty:
                return "Voici les équipements ayant une classification 'Bon' :\n" + \
                    "\n".join(mauvais["N° série"].tolist())
        elif "classification moyen" in message or "état moyen" in message:
            moyen = data[data["Classification finale"] == "Moyen"]
            if not moyen.empty:
                return "Voici les équipements ayant une classification 'Moyen' :\n" + \
               "\n".join(moyen["N° série"].tolist())
            else:
                return "Aucun équipement avec cette classification n'a été trouvé."
    
        else:
            return "Je suis un chatbot simple. Posez-moi des questions basiques !"

      

    for m in st.session_state.chat:
        st.chat_message(m["role"]).write(m["message"])

    if user_msg:
        st.session_state.chat.append({"role": "user", "message": user_msg})
        st.chat_message("user").write(user_msg)

        bot_reply = repondre(user_msg)
        st.session_state.chat.append({"role": "assistant", "message": bot_reply})
        st.chat_message("assistant").write(bot_reply)
        
        