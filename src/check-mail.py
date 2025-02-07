import joblib
from flask import Flask, jsonify, request
from lime.lime_text import LimeTextExplainer

# Charger le modèle et le vectorizer
model = joblib.load("models/ml_text_email.pkl")
text_vectoriser = joblib.load("models/text-vectoriser.pkl")
result_encoder = joblib.load("models/encoder.pkl")

# Initialiser LIME pour expliquer les textes
explainer = LimeTextExplainer(class_names=["Safe Email", "Phishing Email"])

# Initialiser l'API flask
app = Flask(__name__)


def predictor(texts):
    # Fonction de prédiction pour LIME (besoin d’une fonction qui prend du texte et retourne des probabilités)
    x = text_vectoriser.transform(texts)
    return model.predict_proba(x)


@app.route("/predict", methods=["POST"])
def predict():

    # Vérifier si la requête contient du JSON
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Veuillez envoyer un email dans le champ 'email'"}), 400

    # Récupérer le texte de l'e-mail
    email_text = data["email"]

    # Transformer en vecteur avec le Bag of Words
    X_new = text_vectoriser.transform([email_text])

    # Prédire si c'est un mail de phishing ou non
    prediction = model.predict(X_new)[0]
    print(prediction)

    result = result_encoder.inverse_transform([prediction])[0]
    print(result)
    if result == "Phishing Email":
        result = True

    # Générer une explication avec LIME
    exp = explainer.explain_instance(email_text, predictor, num_features=5)
    explanation = exp.as_list()

    # Retourner le résultat
    return jsonify({"email": email_text, "phishing": result, "explication": explanation})


# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
