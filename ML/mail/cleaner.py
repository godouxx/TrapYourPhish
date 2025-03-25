# Fonctions pour nettoyer le jeu de données
# Utilisation d'un autre fichier pour simplifier l'uniformisation du nettoyage
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


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
