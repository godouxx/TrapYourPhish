# Script pour tester les modèles de machines learning sur différents paramètres
import os
import re
import string
import sys

import joblib
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)


def clean_email(text):
    """Fonction pour clean le texte de l'email avec des techniques de NLP"""
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    text = text.lower()  # Minuscule
    text = re.sub(r"http\S+|www\S+|https\S+", '', text,
                  flags=re.MULTILINE)  # Supprimer URLs
    text = re.sub(r'@\S+', '', text)  # Supprimer les mentions (@user)
    text = re.sub(r'#\S+', '', text)  # Supprimer les hashtags
    text = re.sub(r'\d+', '', text)  # Supprimer les nombres
    # Supprimer ponctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenisation et traitement en une seule étape
    words = word_tokenize(text)
    words = [lemmatizer.lemmatize(
        word) for word in words if word not in stop_words and len(word) > 2]

    return " ".join(words)


# Télécharger les ressources nécessaires
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')


def test_dataset(dataset, df_name):
    print(f"Test: {df_name}")
    df = pd.read_csv("test/Ling.csv")
    df = df.dropna()
    print(df.info())
    print(df.head())

    duplicates = df[df.duplicated(keep=False)]
    df = df[df.duplicated(keep=False)]
    print(f"\n\nDonnées dupliquées: \n{duplicates}")
    print(df['label'].value_counts())

    df["subject"] = df["subject"].apply(clean_email)
    df["body"] = df["body"].apply(clean_email)

    df["text"] = "Subject: " + df["subject"] + "\n\n" + df["body"]

    vectoriser = ["bow", "tfidf"]
    classifiers = ["Logistic Regression", "Random Forest",
                   "Support Vector Machine", "Gradient Boosting"]

    for vect in vectoriser:
        vectorizer = joblib.load("models/mail/"+vect+"_vectorizer.pkl")
        for classifier in classifiers:
            model = joblib.load("models/mail/"+vect+"_" +
                                classifier.replace(' ', '_') + ".pkl")

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


# Test des datasets sur les modèles de classification de mails
test_dataset("test/Ling.csv", "Ling")
test_dataset("test/Enron.csv", "Enron")
