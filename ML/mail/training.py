# Script pour entrainer les modèles de classification de mails
import os
import re

import joblib as jb
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             classification_report, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import (GridSearchCV, cross_val_score,
                                     train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

import cleaner

# Import du dataset
phishing_df = pd.read_csv("datasets/mail-phishing.csv")

# Récupération des informations sur le dataset
print(phishing_df.head())
print(phishing_df.info())

# Compter le type de mail
print(f"\n\nType de mail: {phishing_df["isPhishing"].value_counts()}\n")

# Tri / suppression des données nulles
print(f"Données nulles (avant suppression):\n{phishing_df.isna().sum()}\n")
phishing_df = phishing_df.dropna()
print(f"Données nulles (après suppression):\n{phishing_df.isna().sum()}\n")

# Vérification des duplicats
duplicates = phishing_df[phishing_df.duplicated(keep=False)]
print(f"Données dupliquées: \n{duplicates}")

# Comptage après le clean
print(f"\n\nType de mail: {phishing_df["isPhishing"].value_counts()}\n")

# Création du répertoire de sauvegarde des images
SAVE_DIR = "images/mail"
os.makedirs("images/mail", exist_ok=True)

# Graphique de répartition
is_phishing_counts = phishing_df['isPhishing'].value_counts()
plt.figure(figsize=(6, 4))
ax = is_phishing_counts.plot(kind='bar', color=['#ff6347', '#90ee90'])

for p in ax.patches:
    ax.annotate(f'{p.get_height()}',
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                fontsize=12, color='black',
                xytext=(0, 5), textcoords='offset points')
plt.title('Répartition des Mails (Phishing vs Normal)', fontsize=14)
plt.xlabel('Type de Mail', fontsize=12)
plt.ylabel('Nombre de Mails', fontsize=12)
plt.xticks([0, 1], ['Mails Phishing (1)', 'Mails Normaux (0)'], rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(SAVE_DIR, "mail-repartition.png"), dpi=300)

# Équilibrer les classes avec de l'undersampling
safe_mail = phishing_df[phishing_df["isPhishing"] == 0]
phish_mail = phishing_df[phishing_df["isPhishing"] == 1]
phish_mail = phish_mail.sample(safe_mail.shape[0])
print(f"Vérification du nombre de lignes: {
      safe_mail.shape, phish_mail.shape}\n")

# Assembler les deux sous datasets
phish_df = pd.concat(
    [safe_mail, phish_mail], ignore_index=True)
phish_df = phish_df.sample(
    frac=1, random_state=42).reset_index(drop=True)
print(f"Dataset équilibrés: {phish_df.head()}")

# Téléchargement des lib de mots pour la tokenisation / lemmanisation
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

# NLP sur le sujet et le contenu
print(f"Preclean:\n {phish_df['body'][0]}\n\n")
phish_df["subject"] = phish_df["subject"].apply(cleaner.clean_email)
phish_df["body"] = phish_df["body"].apply(cleaner.clean_email)
print(phish_df["body"][0])

# Création d'un texte combiner des colonnes
phish_df["text"] = "Date: " + phish_df["date"] + "\nFrom: " + phish_df["sender"] + \
    "\nSubject: " + phish_df["subject"] + "\nTo: " + \
    phish_df["receiver"] + "\n\n" + phish_df["body"]
phishing_df.drop(['sender', 'receiver', 'subject', 'body', 'date'], axis=1)
phish_df.reset_index(drop=True, inplace=True)
print(phish_df.head())


def vectorise(dataframe, vectorizer, name):
    """Vectorisation du texte"""
    text_vectorized = vectorizer.fit_transform(dataframe["text"])
    jb.dump(vectorizer, name)
    return text_vectorized


# Vectorisation des différentes colonnes avec les deux algorithmes (pour les comparer ensuite)
count_vect = CountVectorizer()
x_count_vect = vectorise(phish_df, count_vect,
                         "models/mail/bow_vectorizer.pkl")  # Input du modèle

tfidf_vect = TfidfVectorizer()
x_tfidf_vect = vectorise(phish_df, tfidf_vect,
                         "models/mail/tfidf_vectorizer.pkl")  # Input du modèle

y = phish_df['isPhishing']  # Output du modèle (à prédire)


def train_classifier(x, vectoriser_name, y):
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.3, random_state=42)

    print(f"Vérification des tailles suite au split:\n- Xtrain: {X_train.shape}\tYtrain {
          y_train.shape}\n- Xtest: {X_test.shape}\tYtest: {y_test.shape}\n")

    classifiers = {
        "Logistic Regression": LogisticRegression(n_jobs=-1),
        "Random Forest": RandomForestClassifier(n_jobs=-1),
        "Support Vector Machine": SVC(kernel='linear', probability=True),
        "Gradient Boosting": GradientBoostingClassifier(),
    }

    scores = {
        'Classifier': [],
        'Accuracy': [],
        'Precision': [],
        'Recall': [],
        'F1-Score': [],
        'ROC AUC': [],
    }

    for name, classifier in classifiers.items():
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)

        # Calcul du score de validation croisée
        cv_scores = cross_val_score(classifier, x, y, cv=5, scoring="accuracy")
        print(f"Accuracy de chaque fold: {cv_scores}")
        print(f"Moyenne des taux de classification: {cv_scores.mean()}")

        # Calcul des scores
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, classifier.predict_proba(X_test)[:, 1])

        # Enregistrer les scores
        scores['Classifier'].append(name)
        scores['Accuracy'].append(accuracy)
        scores['Precision'].append(precision_score(y_test, y_pred))
        scores['Recall'].append(recall_score(y_test, y_pred))
        scores['F1-Score'].append(f1_score(y_test, y_pred))
        scores['ROC AUC'].append(roc_auc)

        # Afficher les résultats
        print(f"{name}:")
        print(f"Accuracy: {accuracy}")
        print(f"ROC AUC Score: {roc_auc:.2f}")
        ConfusionMatrixDisplay.from_predictions(
            y_test, y_pred, normalize="true", values_format=".0%")
        plt.title(f"Matrice de confusion de {name}")
        image_name = vectoriser_name + "_" + name.replace(' ', '_') + ".png"
        plt.savefig(os.path.join(SAVE_DIR, image_name), dpi=300)
        jb.dump(classifier, "models/mail/"+vectoriser_name +
                "_"+name.replace(' ', '_') + ".pkl")

        # Convertir en DataFrame
        scores_df = pd.DataFrame(scores)

    # Graphique pour comparer les métriques
    plt.figure(figsize=(18, 10))

    scores_melted = scores_df.melt(
        id_vars='Classifier', var_name='Metric', value_name='Score')

    ax = sns.barplot(x='Classifier', y='Score',
                     hue='Metric', data=scores_melted)

    for p in ax.patches:
        height = round(p.get_height(), 2)
        ax.annotate(f'{height}',
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='center',
                    xytext=(0, 10),
                    textcoords='offset points')

    plt.title('Comparaison des Scores de Classification')
    plt.xlabel('Classificateurs')
    plt.ylabel('Scores')
    plt.legend(title='Métriques')
    image_name = vectoriser_name + "_comparaison.png"
    plt.savefig(os.path.join(SAVE_DIR, image_name), dpi=300)


train_classifier(x_count_vect, "bow", y)
train_classifier(x_tfidf_vect, "tfidf", y)

# Optimisation avec un gridsearch
print("\nGridSearch optimisaton\n\n")

x = phish_df["text"]
X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

# Pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("svm", SVC(kernel="linear", probability=True))
])

# Recherche des paramètres optimum
param_grid = {
    "tfidf__max_df": [0.75, 1.0],  # Supprime les mots trop fréquents
    "tfidf__ngram_range": [(1, 1), (1, 2)],  # Unigrammes ou bigrammes
    "svm__C": [0.1, 1, 10]  # Régularisation de SVM
}

# Effectuer la recherche d'hyperparamètres avec validation croisée (n_job -1 pour du multithreading sur tous les processeurs)
grid_search = GridSearchCV(pipeline, param_grid, cv=5,
                           scoring="accuracy", verbose=2, n_jobs=-1)
grid_search.fit(X_train, y_train)

# Afficher les meilleurs paramètres et les meilleures performances
print("Meilleurs paramètres:", grid_search.best_params_)
print("Meilleur score:", grid_search.best_score_)

# Utiliser le meilleur modèle pour prédire et évaluer
best_model = grid_search.best_estimator_
y_pred_best = best_model.predict(X_test)
print("Performance du meilleur modèle:")
print(f"Accuracy: {accuracy_score(y_test, y_pred_best):.2f}")

ConfusionMatrixDisplay.from_predictions(
    y_test, y_pred_best, normalize="true", values_format=".0%")
plt.title("Matrice de confusion du meilleur modèle de SVM")
plt.savefig(os.path.join(SAVE_DIR, "best_tfidf_svm.png"), dpi=300)

# Sauvegarder le meilleur modèle
best_tfidf = best_model.named_steps["tfidf"]
best_svm = best_model.named_steps["svm"]
jb.dump(best_tfidf, "models/opti_tfidf_mail.pkl")
jb.dump(best_svm, "models/opti_svm_mail.pkl")
