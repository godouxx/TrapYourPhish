import joblib
from flask import Flask, request, jsonify
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# Charger le modèle et le vectorizer
model = joblib.load("models/ml_text_email.pkl")
text_vectoriser = joblib.load("models/text-vectoriser.pkl")
result_encoder = joblib.load("models/encoder.pkl")

# Initialiser l'API flask
app = Flask(__name__)


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

    # Prédire si c'est un spam ou non
    prediction = model.predict(X_new)[0]

    result = result_encoder.inverse_transform([prediction])[0]
    if result == "Phishing Email":
        result = True

    # Retourner le résultat
    return jsonify({"email": email_text, "phishing": result})


# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
