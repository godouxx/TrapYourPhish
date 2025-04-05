import json
import os
import re

import joblib
import nltk
import requests
from flask import Flask, jsonify, request
from lime.lime_text import LimeTextExplainer

from mail import cleaner

# Chargement des modèles et des vectoriseurs
mail_model = joblib.load("models/opti_svm_mail.pkl")
text_vectoriser_mail = joblib.load("models/opti_tfidf_mail.pkl")

url_model = joblib.load("models/url/bow_Random_Forest.pkl")
text_vectoriser_url = joblib.load("models/url/bow_vectorizer.pkl")

# Initialiser LIME pour expliquer les textes
explainer_mail = LimeTextExplainer(class_names=["Safe", "Phishing"])
explainer_url = LimeTextExplainer(class_names=["Safe", "Phishing"])

# Téléchargement des lib de mots pour la tokenisation / lemmanisation
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')


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


def LLM_analysis(is_phishing, email, words, url_results):
    url = os.getenv("LLM_URL", "http://localhost:11434/api/chat")
    model = os.getenv("LLM_MODEL", "llama3.2")
    header = {"Content-Type": "application/json"}

    content = f'''
{{
    "email": {email},
    "phishing": {is_phishing},
    "explication_mail": {words},
    "urls": {url_results}
}}
'''

    messages = [{
        "role": "system",
        "content": """Vous êtes un assistant en cybersécurité spécialisé dans la détection de phishing

L'utilisateur fournira un e-mail, une classification et une liste de ses éléments clés accompagnée de scores d'importance (les scores positifs indiquent des éléments suspects, les scores négatifs indiquent des éléments sûrs). Votre tâche consiste à analyser l'e-mail de manière globale et à rédiger un paragraphe concis et factuel expliquant s'il est suspect ou bénin dans le contexte du phishing. De plus, pour chaque URL fournie, vous devez expliquer pourquoi elles sont considérées comme des URLs de phishing.

Lors de la rédaction du paragraphe :
- Prenez en compte tous les éléments et leurs scores pour déterminer la probabilité globale de phishing ou de sécurité. Ne mentionnez pas les scores dans le paragraphe.
- Si le json la valeur de la clé phishing est "Phishing" alors mettez en avant la contribution au phishing des mots à score positif élevé. À l'inverse, la valeur de la clé phshing est "Safe", mettez en avant la contribution à la sécurité des mots à score négatif élevé.
- Si certains éléments ont un score négatif, mentionnez-les comme facteurs atténuants, mais ne contestez pas les éléments suspects s'ils dominent.
- Intégrez les éléments de manière naturelle et fluide dans le paragraphe, sans les énumérer séparément.
- Ne faites pas d'hypothèses ni d'inventions au-delà des informations fournies.
- Soyez clair, éducatif et factuel, sans donner de conseils ou de recommandations en matière de sécurité et évitez de vous répétez
"""
    },
        {
        "role": "user",
        "content": content
    }]

    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    response = requests.post(url, headers=header, data=json.dumps(data))

    if response.status_code == 200:
        data = json.loads(response.text)
        print(data)
        return data["message"]["content"]
    else:
        return None


@ app.route("/predict", methods=["POST"])
def predict():

    # Vérifier si la requête contient du JSON
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"status": "error", "message": "Le champ 'email' vide"}), 400

    email_text = data["email"]
    urls = extract_urls(email_text)

    cleaned_text = cleaner.clean_email(email_text)

    X_mail = text_vectoriser_mail.transform([cleaned_text])
    prediction_mail = mail_model.predict(X_mail)[0]

    # Générer une explication avec LIME pour le mail
    words_lime = explainer_mail.explain_instance(
        email_text, predictor_mail, num_features=10)
    words = words_lime.as_list()

    # Prédiction et explication pour chaque URL (s'il y en a des URL)
    url_results = []
    for url in urls:
        X_url = text_vectoriser_url.transform([url])
        prediction_url = url_model.predict(X_url)[0]

        # Ajouté seulement les URL de phishing
        if prediction_url == 1:
            exp_url = explainer_url.explain_instance(
                url, predictor_url, num_features=5)
            explanation_url = exp_url.as_list()
            url_results.append({
                "url": url,
                "phishing": "Phishing",
                "explication": explanation_url
            })

    # Utilisation du LLM pour expliquer les mots dans le contexte du mail
    explaination_mail = LLM_analysis(prediction_mail, email_text, words,
                                     url_results)

    if explaination_mail is None:
        return jsonify({"status": "error", "message": "LLM can't predict"}), 501

    # Retourner le résultat du mail et des URL
    return jsonify({
        "status": "success",
        "phishing": "Phishing" if prediction_mail == 1 else "Safe",
        "explication_mail": explaination_mail,
        "urls": url_results
    })


# Lancer l'application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
