import re
import joblib
import nltk
from flask import Flask, jsonify, request
from lime.lime_text import LimeTextExplainer
from mail import cleaner
from expli2 import get_explanation_from_llm

# Chargement des modèles
mail_model = joblib.load("models/mail/bow_Logistic Regression.pkl")
text_vectoriser_mail = joblib.load("models/mail/bow_vectorizer.pkl")

url_model = joblib.load("models/url/bow_Random_Forest.pkl")
text_vectoriser_url = joblib.load("models/url/bow_vectorizer.pkl")

# Initialiser LIME
explainer_mail = LimeTextExplainer(class_names=["Safe", "Phishing"])
explainer_url = LimeTextExplainer(class_names=["Safe", "Phishing"])

# NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)


def extract_urls(text):
    return re.findall(r'https?://[^\s]+', text)


def predictor_mail(texts):
    x = text_vectoriser_mail.transform(texts)
    return mail_model.predict_proba(x)


def predictor_url(texts):
    x = text_vectoriser_url.transform(texts)
    return url_model.predict_proba(x)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"status": "error", "message": "Le champ 'email' est requis"}), 400

    email_text = data["email"]
    urls = extract_urls(email_text)
    cleaned_text = cleaner.clean_email(email_text)

    X_mail = text_vectoriser_mail.transform([cleaned_text])
    prediction_mail = mail_model.predict(X_mail)[0]

    # Explication LIME
    exp_mail = explainer_mail.explain_instance(email_text, predictor_mail, num_features=10)
    explanation_mail = exp_mail.as_list()

    # Top 3 éléments suspects
    top_features = sorted(explanation_mail, key=lambda x: abs(x[1]), reverse=True)
    top_elements = [word for word, score in top_features[:3]]

    # Appel LLM
    llm_explanations = []
    for word in top_elements:
        explanation = get_explanation_from_llm(word)
        llm_explanations.append({
            "element": word,
            "explanation": explanation
            
        })

    # URLs et nnn
    url_results = []
    for url in urls:
        X_url = text_vectoriser_url.transform([url])
        prediction_url = url_model.predict(X_url)[0]
        exp_url = explainer_url.explain_instance(url, predictor_url, num_features=5)
        explanation_url = exp_url.as_list()
        url_results.append({
            "url": url,
            "phishing": "Phishing" if prediction_url == 1 else "Safe",
            "explication": explanation_url
        })

    return jsonify({
        "status": "success",
        "phishing": "Phishing" if prediction_mail == 1 else "Safe",
        "explanations_llm": llm_explanations,
        "urls": url_results
    })


if __name__ == "__main__":
    app.run(debug=True)