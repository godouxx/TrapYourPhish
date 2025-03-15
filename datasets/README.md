# Datasets
---

Ce répertoire contient les datasets utilisées pour les modèles de machine learning.  
  
Ces datasets proviennent de Kaggle:
- [Kaggle mail datasets](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)
- [Kaggle URL dataset](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)
  
## Dataset de mail

Pour réaliser le dataset d'entrainement du modèle de machine learning pour la
classification de mails en phishing ou non, plusieurs datasets ont été combinés.
  
Ces datasets sont:
- CEAS_08  
- Nazario  
- Nigerian Fraud  
- SpamAssasin  
  
Ces datasets ont été choisis car ils possèdent des métadonnées qui permettent 
d'obtenir de meilleures performances sur les modèles de classification.  
  
Ces métadonnées sont:
- Date  
- Envoyeur  
- Receveur  
- Sujet  
- Contenu du mail  
  
Le script python `make-dataset.py` permet de réaliser le dataset `mail-phishing.csv`,
qui est la combinaison des 4 datasets précédents, nettoyés (pas de duplicats ni de
valeurs nulles), et catégoriser en Phishing ou non.

## Dataset d'URL

Ce dataset est composé d'URL de phishing et d'URL safe. Il vient directement de
Kaggle.
