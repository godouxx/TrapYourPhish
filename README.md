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

Le fichier `src/training-model.py` permet de comparer les performances de 4 algorithmes de machine learning et 2 algorithmes de vectorisation sur l'entrainement d'un modèle de détection de mail de phishing.  
Le fichier `src/optimizing-model.py` permet la recherche de paramètres optimum pour l'algorithme le plus performant trouver dans `src/training-model.py` (le State Vector Machine).  
**Attention ces 2 algorithmes sont particulièrement long à executer, et peuvent prendre plusieurs heures...**  
  
Le fichier `src/check-mail.py` est une API permettant de réaliser une requête HTTP POST, pour envoyer le contenu d'un mail, et en retour savoir s'il s'agit d'un mail de phishing ou non.

Exemple de requête avec CURL:
```bash
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d '{"email": "Buy cheap viagra now, click on this link !!!"}'
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
