import re

import joblib
from flask import Flask, jsonify, request
from lime.lime_text import LimeTextExplainer

# Charger le modèle et le vectorizer
mail_model = joblib.load("models/opti_svm_mail.pkl")
text_vectoriser_mail = joblib.load("models/opti_tfidf_mail.pkl")

url_model = joblib.load("models/url/bow_Random Forest.pkl")
text_vectoriser_url = joblib.load("models/url/bow_vectorizer.pkl")

# Initialiser LIME pour expliquer les textes
explainer_mail = LimeTextExplainer(class_names=["Safe", "Phishing"])
explainer_url = LimeTextExplainer(class_names=["Safe", "Phishing"])

# Initialiser l'API flask
app = Flask(__name__)


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


@app.route("/predict", methods=["POST"])
def predict():

    # Vérifier si la requête contient du JSON
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Veuillez envoyer un email dans le champ 'email'"}), 400

    email_text = data["email"]
    urls = extract_urls(email_text)

    X_mail = text_vectoriser_mail.transform([email_text])

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
    return jsonify({
        "phishing": "Phishing" if prediction_mail == 1 else "Safe",
        "explication_mail": explanation_mail,
        "urls": url_results
    })


# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
