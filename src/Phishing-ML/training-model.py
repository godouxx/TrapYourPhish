import joblib as jb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, f1_score,
                             precision_score, recall_score, roc_auc_score,
                             roc_curve)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.svm import SVC

# Import du dataset
phishing_df = pd.read_csv("datasets/mail-phishing.csv")

# Récupération des informations sur le dataset
print(phishing_df.head())
print(phishing_df.info())

# Compter le type de mail
print(f"\n\nType de mail: {phishing_df["isPhishing"].value_counts()}\n")

# Tri / suppression des données nulles
print(f"Données nulles:\n{phishing_df.isna().sum()}\n")
phishing_df = phishing_df.dropna()
print(f"Données nulles:\n{phishing_df.isna().sum()}\n")

# Vérification des duplicats
duplicates = phishing_df[phishing_df.duplicated(keep=False)]
print(f"Données dupliquées: \n{duplicates}")

# Comptage après le clean
print(f"\n\nType de mail: {phishing_df["isPhishing"].value_counts()}\n")

# Affichage sous forme de graphe
is_phishing_counts = phishing_df['isPhishing'].value_counts()

plt.figure(figsize=(6, 4))
ax = is_phishing_counts.plot(kind='bar', color=['#ff6347', '#90ee90'])

# Ajouter le nombre au-dessus de chaque barre
for p in ax.patches:
    ax.annotate(f'{p.get_height()}',
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                fontsize=12, color='black',
                xytext=(0, 5), textcoords='offset points')

# Personnalisation du graphique
plt.title('Répartition des Mails (Phishing vs Normal)', fontsize=14)
plt.xlabel('Type de Mail', fontsize=12)
plt.ylabel('Nombre de Mails', fontsize=12)
plt.xticks([0, 1], ['Mails Phishing (1)', 'Mails Normaux (0)'], rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Affichage du graphique
plt.tight_layout()
plt.show()

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


# Création d'un texte combiner des colonnes
phish_df["text"] = "Date: " + phish_df["date"] + "\nFrom: " + phish_df["sender"] + \
    "\nSubject: " + phish_df["subject"] + "\nTo: " + \
    phish_df["receiver"] + "\n\n" + phish_df["body"]
phishing_df.drop(['sender', 'receiver', 'subject', 'body', 'date'], axis=1)


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
        "Logistic Regression": LogisticRegression(),
        "Random Forest": RandomForestClassifier(),
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
        plt.show()
        jb.dump(classifier, "models/mail/"+vectoriser_name+"_"+name+".pkl")

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
    plt.show()


train_classifier(x_count_vect, "bow", y)
train_classifier(x_tfidf_vect, "tfidf", y)
