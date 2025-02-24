import joblib
import joblib as jb
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             classification_report)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

# Import du dataset
phishing_df = pd.read_csv("datasets/url-phishing.csv")

# Récupération des informations sur le dataset
print(phishing_df.head())
print(phishing_df.info())

# Renommer la colonne label en isPhishing et convertir les valeurs en numériques
phishing_df = phishing_df.rename(columns={'Label': 'isPhishing'})
phishing_df['isPhishing'] = phishing_df['isPhishing'].replace(
    {'good': 0, 'bad': 1})

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
ax = is_phishing_counts.plot(kind='bar', color=['#90ee90', '#ff6347'])

# Ajouter le nombre au-dessus de chaque barre
for p in ax.patches:
    ax.annotate(f'{p.get_height()}',
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                fontsize=12, color='black',
                xytext=(0, 5), textcoords='offset points')

# Personnalisation du graphique
plt.title('Répartition des URLs (Phishing vs Normal)', fontsize=14)
plt.xlabel("Type d'URL", fontsize=12)
plt.ylabel("Nombre d'URL", fontsize=12)
plt.xticks([0, 1], ['URLs Normaux (0)', 'URLs Phishing (1)'], rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Affichage du graphique
plt.tight_layout()
plt.show()

# Équilibrer les classes avec de l'undersampling
safe_url = phishing_df[phishing_df["isPhishing"] == 0]
phish_url = phishing_df[phishing_df["isPhishing"] == 1]
safe_url = safe_url.sample(phish_url.shape[0])

print(f"Vérification du nombre de lignes: {
      safe_url.shape, phish_url.shape}\n")

# Assembler les deux sous datasets
phish_df = pd.concat(
    [safe_url, phish_url], ignore_index=True)
phish_df = phish_df.sample(
    frac=1, random_state=42).reset_index(drop=True)
print(f"Dataset équilibrés: {phish_df.head()}")

x = phish_df["URL"]
y = phish_df['isPhishing']  # Output du modèle (à prédire)

# Diviser les données
X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

print(f"Vérification des tailles suite au split:\n- Xtrain: {X_train.shape}\tYtrain {
      y_train.shape}\n- Xtest: {X_test.shape}\tYtest: {y_test.shape}\n")

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
plt.show()

# Sauvegarder le meilleur modèle
best_tfidf = best_model.named_steps["tfidf"]
best_svm = best_model.named_steps["svm"]
joblib.dump(best_tfidf, "models/opti_tfidf_url.pkl")
joblib.dump(best_svm, "models/opti_svm_url.pkl")
