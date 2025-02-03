import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split  # , cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, ConfusionMatrixDisplay, roc_auc_score, roc_curve
import joblib as jb

# Import du dataset
phishing_data = pd.read_csv("Data/Phishing_Email.csv")

# Copie du dataset
phishing_df = phishing_data.rename(columns={'Unnamed: 0': 'ID'})

# Récupération des informations sur le dataset
print(phishing_df.head())
phishing_df.info()

# Compter le type de mail
print(f"\n\nType de mail: {phishing_df["Email Type"].value_counts()}\n")

# Tri / suppression des données nulles
print(f"Données nulles:\n{phishing_df.isna().sum()}\n")
phishing_df = phishing_df.dropna()
print(f"Données nulles:\n{phishing_df.isna().sum()}\n")
phishing_df = phishing_df[~phishing_df['Email Text'].str.contains('empty')]

# Vérification des duplicats
duplicates = phishing_df[phishing_df.duplicated(keep=False)]
print(duplicates)

# Comptage après le clean
print(f"\n\nType de mail: {phishing_df["Email Type"].value_counts()}\n")

# Affichage sous forme de graphe
plt.figure(figsize=(7, 5))
ax = sns.countplot(x="Email Type", hue="Email Type",
                   data=phishing_df, palette="viridis")

for i in range(0, len(ax.patches)):
    ax.bar_label(ax.containers[i])

plt.title("Distribution des types d'emails")
plt.xlabel("Type d'email")
plt.ylabel("Nombre")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Équilibrer les classes avec de l'undersampling
safe_mail = phishing_df[phishing_df["Email Type"] == "Safe Email"]
phish_mail = phishing_df[phishing_df["Email Type"] == "Phishing Email"]
safe_mail = safe_mail.sample(phish_mail.shape[0])

print(f"Vérification du nombre de lignes: {
      safe_mail.shape, phish_mail.shape}\n")

# Assembler les deux sous datasets
phish_eq_df = pd.concat(
    [safe_mail, phish_mail], ignore_index=True)
phish_eq_df = phish_eq_df.sample(
    frac=1, random_state=42).reset_index(drop=True)
print(f"Dataset équilibrés: {phish_eq_df.head()}")

# Encodage des types de mail
label_encoder = LabelEncoder()
phish_eq_df['Email Type'] = label_encoder.fit_transform(
    phish_eq_df['Email Type'])
print(f"Dataset encodée: {phish_eq_df}\n")
phish_eq_df.drop(columns=['ID'], inplace=True)
jb.dump(label_encoder, "models/encoder.pkl")

# Vectorisation des textes des email
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(phish_eq_df["Email Text"])  # Input du modèle
y = phish_eq_df['Email Type']  # Output du modèle (à prédire)
jb.dump(vectorizer, "models/text-vectoriser.pkl")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)
print(f"Vérification des tailles suite au split:\n- Xtrain: {X_train.shape}\tYtrain {
      y_train.shape}\n- Xtest: {X_test.shape}\tYtest: {y_test.shape}\n")

# Entrainement du modèle
classifier = LogisticRegression()
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)

# cv_scores = cross_val_score(classifier, X, y, cv=5, scoring="accuracy")

# print(f"Accuracy de chaque fold: {cv_scores}")
# print(f"Moyenne des taux de classification: {cv_scores.mean()}")

# Calcul des scores
accuracy = accuracy_score(y_test, y_pred)
y_score = classifier.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_score)
roc_auc = roc_auc_score(y_test, y_score)

# Afficher les résultats
print("\nRésultat du classifieur LogisticRegression:\n")
print(f"Accuracy: {accuracy}")
print(f"Précision: {precision_score(y_test, y_pred)}")
print(f"Recall: {recall_score(y_test, y_pred)}")
print(f"F1Score: {f1_score(y_test, y_pred)}")

ConfusionMatrixDisplay.from_predictions(
    y_test, y_pred, normalize="true", values_format=".0%")
plt.title("Matrice de confusion de LogisticRegression")
plt.show()

plt.figure()
plt.plot(fpr, tpr, label=f'{"Logistic Regression"} (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('Taux de faux positif')
plt.ylabel('Taux de vrai positif')
plt.title(f'Courbe ROC - {"Logistic Regression"}')
plt.legend(loc='lower right')
plt.show()

# Enregistrement du modèle
jb.dump(classifier, "models/ml_text_email.pkl")
