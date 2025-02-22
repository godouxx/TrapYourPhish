# Programme python pour tester si le modèle fonctionne sur d'autres datasets
import joblib
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)

df = pd.read_csv("test/Enron.csv")
df = df.dropna()
print(df.info())
print(df.head())

duplicates = df[df.duplicated(keep=False)]
print(f"\n\nDonnées dupliquées: \n{duplicates}")

print(df['label'].value_counts())

df["text"] = "Subject: " + df["subject"] + "\n\n" + df["body"]

vectoriser = ["bow", "tfidf"]
classifiers = ["Logistic Regression", "Random Forest",
               "Support Vector Machine", "Gradient Boosting"]
for vect in vectoriser:
    vectorizer = joblib.load("models/phishing/"+vect+"_vectorizer.pkl")
    for classifier in classifiers:
        model = joblib.load("models/phishing/"+vect+"_"+classifier+".pkl")

        X = vectorizer.transform(df["text"])
        y = df['label']  # Remplace 'target' par le nom de ta colonne cible

        # Faire des prédictions
        y_pred = model.predict(X)

        # Évaluer la performance du modèle
        print(f"{vect}: {classifier}")
        # Calculer la précision (accuracy)
        accuracy = accuracy_score(y, y_pred)
        print(f'Accuracy: {accuracy * 100:.2f}%')

        # Afficher le rapport de classification pour une évaluation plus complète
        print("Classification Report:")
        print(classification_report(y, y_pred))

        # Afficher la matrice de confusion
        print("Confusion Matrix:")
        print(confusion_matrix(y, y_pred))
