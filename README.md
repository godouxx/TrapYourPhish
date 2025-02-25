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

Le fichier `src/check-mail.py` est une API permettant de réaliser une requête HTTP POST, pour envoyer le contenu d'un mail, et en retour savoir s'il s'agit d'un mail de phishing ou non.

Exemple de requête avec CURL:
```bash
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d '{"email": "Buy cheap viagra now, click on this link !!! <http://notaphishing.com>"}'
```

Pour que la requête fonctionne il faut lancer le programme `src/check-mail.py`.
```bash
.venv/bin/python3 src/check-mail.py
```

**Attention, les métadonnées doivent être formattés de cette façon:**

```mail
Date: ....
From: ....
Subject: ....
To: ...


contenu du mail
```

## Machine Learning

### Phishing

Le fichier `src/Phishing-ML/training-model.py` permet de comparer les performances de 4 algorithmes de machine learning et 2 algorithmes de vectorisation sur l'entrainement d'un modèle de détection de mail de phishing.  Les modèles sont enregistrés dans le répertoire `models/phishing/`.  
Le fichier `src/Phishing-ML/optimizing-model.py` permet la recherche de paramètres optimum pour l'algorithme le plus performant (à définir à la main dans le code).  
  
**Attention ces 2 programmes sont particulièrement long à executer, et peuvent prendre plusieurs heures...**   
  
Le fichier `test/phishing-test.py` permet de réaliser des tests de performances des modèles choisi sur d'autres datasets de mail de phishing comme Enron ou Ling.  
  
## Objectifs

### Version 1 

Analyse d'email de phising venant d'un dataset et identification d'éléments clés (argent, email pas cohérent) afin d'obtenir un score de probabilité que le mail est un phising.
Pas d'interface graphique pour la première version et prise en compte uniquement d'une seule langue.

### Version 2
Etude de la faisabilité de l'ajout de l'analyse de pluri-langue.
Intégration de cette solution à une extension de navigateur (Chrome) qui permettra de vérifier si un email est un phising ou non.

### Version 3
Intégrer directement dans la boite mail (Gmail) la vérification des emails en utilisant l'API.
