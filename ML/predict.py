import json
import re
import sys

import joblib
import nltk
from lime.lime_text import LimeTextExplainer

from mail import cleaner

# Chargement des modèles et des vectoriseurs
mail_model = joblib.load("../models/opti_svm_mail.pkl")
text_vectoriser_mail = joblib.load("../models/opti_tfidf_mail.pkl")

url_model = joblib.load("../models/url/bow_Random_Forest.pkl")
text_vectoriser_url = joblib.load("../models/url/bow_vectorizer.pkl")

# Initialiser LIME pour expliquer les textes
explainer_mail = LimeTextExplainer(class_names=["Safe", "Phishing"])
explainer_url = LimeTextExplainer(class_names=["Safe", "Phishing"])

# Téléchargement des lib de mots pour la tokenisation / lemmanisation
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')


def extract_urls(text):
    """Fonction pour extraire les URLs d'un texte"""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def predictor_mail(texts):
    """Fonction de prédiction pour LIME sur les emails"""
    x = text_vectoriser_mail.transform(texts)
    return mail_model.predict_proba(x)


def predictor_url(texts):
    """Fonction de prédiction pour LIME sur les URLs"""
    x = text_vectoriser_url.transform(texts)
    return url_model.predict_proba(x)


def predict():

    # Vérifier si la requête contient du JSON
    if len(sys.argv) < 2:
        print(json.dumps(
            {"status": "error",
             "message": "Argument email not found"}))
        sys.exit(1)

    email_text = sys.argv[1]
    urls = extract_urls(email_text)

    cleaned_text = cleaner.clean_email(email_text)

    X_mail = text_vectoriser_mail.transform([cleaned_text])

    prediction_mail = mail_model.predict(X_mail)[0]

    # Générer une explication avec LIME pour le mail
    exp_mail = explainer_mail.explain_instance(
        email_text, predictor_mail, num_features=10)
    explanation_mail = exp_mail.as_list()

    # Prédiction et explication pour chaque URL (s'il y en a des URL)
    url_results = []
    for url in urls:
        X_url = text_vectoriser_url.transform([url])
        prediction_url = url_model.predict(X_url)[0]
        exp_url = explainer_url.explain_instance(
            url, predictor_url, num_features=5)
        explanation_url = exp_url.as_list()
        url_results.append({
            "url": url,
            "phishing": "Phishing" if prediction_url == 1 else "Safe",
            "explication": explanation_url
        })

    # Retourner le résultat du mail et des URL
    print(json.dumps({
        "status": "success",
        "phishing": "Phishing" if prediction_mail == 1 else "Safe",
        "explication_mail": explanation_mail,
        "urls": url_results
    }))


# Lancer l'application
if __name__ == "__main__":
    predict()
