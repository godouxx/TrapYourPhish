# TrapYourPhish
Projet d'Atelier Pratiques Cybersécurité 2 (8INF870) à l'UQAC.

## Installation

Pour simplifier l'installation, vous pouvez créez un environnement virtual avec Python:
```bash
python3 -m venv .venv
```

Puis il suffit d'installer les librairies nécessaires pour lancer le programme se trouvant dans le fichier `requirements.txt`:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation du programme

Le fichier `src/training-model.py` permet d'entrainer un modèle de détection de phishing et de sauvegarder le modèle entrainer dans `models/ml_text_email.pkl`.
Le fichier `src/check-mail.py` est une API permettant de réaliser une requête HTTP POST, pour envoyer le contenu d'un mail, et en retour savoir s'il s'agit d'un mail de phishing ou non.

Exemple de requête avec CURL:
```bash
curl -X POST http://127.0.0.1:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"email": "Achetez du Viagra pas cher, cliquez sur ce lien"}'
```

Pour que la requête fonctionne il faut lancer le programme `src/check-mail.py`.
```bash
.venv/bin/python3 src/check-mail.py
```

## Objectifs

### Version 1 

Analyse d'email de phising venant d'un dataset et identification d'éléments clés (argent, email pas cohérent) afin d'obtenir un score de probabilité que le mail est un phising.
Pas d'interface graphique pour la première version et prise en compte uniquement d'une seule langue.

### Version 2
Etude de la faisabilité de l'ajout de l'analyse de pluri-langue.
Intégration de cette solution à une extension de navigateur (Chrome) qui permettra de vérifier si un email est un phising ou non.

### Version 3
Intégrer directement dans la boite mail (Gmail) la vérification des emails en utilisant l'API.
