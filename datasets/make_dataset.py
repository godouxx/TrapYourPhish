# Création d'un dataset global regroupant les datasets dans le répertoire
import pandas as pd

ceas = pd.read_csv("datasets/mail/CEAS_08.csv")
nazario = pd.read_csv("datasets/mail/Nazario.csv")
nigerian_fraud = pd.read_csv("datasets/mail/Nigerian_Fraud.csv")
spam_assassin = pd.read_csv("datasets/mail/SpamAssasin.csv")

print("Informations sur les datasets: \n")
print(ceas.info())
print(nazario.info())
print(nigerian_fraud.info())
print(spam_assassin.info())

print("\n\nVérification du contenu des datasets: \n")
print(ceas.head())
print(nazario.head())
print(nigerian_fraud.head())
print(spam_assassin.head())

# Suppresion de la colonne URL
ceas = ceas.drop(columns=['urls'])
nazario = nazario.drop(columns=['urls'])
nigerian_fraud = nigerian_fraud.drop(columns=['urls'])
spam_assassin = spam_assassin.drop(columns=['urls'])

# Renommage de la colonne label en isPhishing
ceas = ceas.rename(columns={'label': 'isPhishing'})
nazario = nazario.rename(columns={'label': 'isPhishing'})
nigerian_fraud = nigerian_fraud.rename(columns={'label': 'isPhishing'})
spam_assassin = spam_assassin.rename(columns={'label': 'isPhishing'})

print("Informations sur les datasets: \n")
print(ceas.info())
print(nazario.info())
print(nigerian_fraud.info())
print(spam_assassin.info())

print("\n\nVérification du contenu des datasets: \n")
print(ceas.head())
print(nazario.head())
print(nigerian_fraud.head())
print(spam_assassin.head())

# Clean les lignes vides et les duplicats
print(f"Données nulles:\n{ceas.isna().sum()}\n")
print(f"Données nulles:\n{nazario.isna().sum()}\n")
print(f"Données nulles:\n{nigerian_fraud.isna().sum()}\n")
print(f"Données nulles:\n{spam_assassin.isna().sum()}\n")
ceas = ceas.dropna()
nazario = nazario.dropna()
nigerian_fraud = nigerian_fraud.dropna()
spam_assassin = spam_assassin.dropna()

print("Informations sur les datasets: \n")
print(ceas.info())
print(nazario.info())
print(nigerian_fraud.info())
print(spam_assassin.info())

print("Informations sur les duplicats: \n")
print(f"Ceas: {ceas[ceas.duplicated(keep=False)]}")
print(f"Nazario: {nazario[nazario.duplicated(keep=False)]}")
print(f"Nigerian Fraud: {
      nigerian_fraud[nigerian_fraud.duplicated(keep=False)]}")
print(f"Spam Assassin: {spam_assassin[spam_assassin.duplicated(keep=False)]}")

dataset = pd.concat([ceas, nazario, nigerian_fraud,
                    spam_assassin], ignore_index=True)
print(dataset.info())
print(dataset.head())
print(f"\n\nType de mail: {dataset["isPhishing"].value_counts()}\n")

dataset.to_csv('datasets/mail-phishing.csv', index=False)
