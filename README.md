Projet d'Atelier Pratiques Cybersécurité 2 (8INF870) à l'UQAC.

## Présentation

Ce projet a pour but de permettre de sensibiliser et d'expliquer les emails de Phishing. Pour cela, les emails sont dans un premier temps analysés par des modèles de machine learning, puis dans un second temps, un algorithme d'intelligence artificielle explicatif (XAI) nommé LIME va retourner les mots clés ayant permis la catégorisation ainsi que la pondération de ces mots.

*Dans le futur, une vraie explication sera réalisée grâce à un LLM qui aura pour rôle d'expliquer à partir des mots clés en quoi cet email est du phishing ou non.*

## Téléchargement du projet

Pour récupérer ce projet vous aurez besoin de l'outils git et de git lfs.

```bash
sudo apt-get update
sudo apt install git git-lfs
git clone https://github.com/godouxx/TrapYourPhish.git
cd TrapYourPhish/
git lfs pull
```

## Installation

> [!IMPORTANT]
> Pour le moment ce projet est uniquement fonctionnel sur un environnement Linux

Les étapes suivantes permettent de déployer & exécuter ce projet

### 1. Création de l'environnement Python **(Minimum Python3.10)**

> [!NOTE]
> Pour cette étape, la présence de Python est supposé, sinon `sudo apt install python3 python3-venv python3-pip` permettra de l'installer sur une distribution dérivant de Debian (Ubuntu, Debian, Linux Mint...)

Dans un premier temps, le projet nécessite la création d'un environnement virtuel Python.

> [!CAUTION]
> L'environnement virtuel Python doit être créer à la racine du projet

```bash
python3 -m venv .venv
```

Puis installer les dépendances nécessaires :
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Mise en place de la base de données

Une base de données MySQL ou MariaDB doit être mise en place pour sauvegarder les comptes utilisateurs et leur historique d'emails.

Dans un premier temps, un serveur MySQL ou MariaDB doit être installé :
```bash
sudo apt install mariadb-server
sudo systemctl start mariadb.service
```

> [!NOTE]
> Si vous souhaitez installer le serveur sur une autre machine, vous devez vérifier que les ports du serveur SQL sont bien ouverts

Dans un second temps, l'utilisateur et la base de donnée doivent être créés.
```bash
sudo mysql
```

```mysql
CREATE DATABASE trapyourphish DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'trapyourphish'@'%' IDENTIFIED BY 'SUPERPASSWORD';
GRANT USAGE ON *.* TO 'trapyourphish'@'%';
GRANT ALL PRIVILEGES ON trapyourphish.* TO 'trapyourphish'@'%';
FLUSH PRIVILEGES;
```

> [!CAUTION]
> Si votre base de données est sur une autre machine ou que vous avez modifié les configurations pour l'utilisateur / la base de données MySQL, vous devez modifier les identifiants dans le fichier de configuration pour le backend `Backend/config/default.json`.

### 3. Mise en place du backend / front-end

Le backend utilise le langage [Rust](https://www.rust-lang.org/), il est donc nécessaire de [l'installer](https://www.rust-lang.org/tools/install) 
L'installation standard est suffisante pour l'installation de rust pour notre projet:

```bash
sudo apt install curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.bashrc
```
Puis aller dans le répertoBackend :end:
```bash
cd Backend
```

Et lancer le prograRust :ust:
```bash
cargo run -- --prod
```

> [!TIP]
> Si vous avez une erreur parlant de lib openssl manquante, il faudra installer le paquet suivant sous Ubuntu `sudo apt-get install libssl-dev pkg-config`

Ce programme devrait installer les dépendances nécessaires dans un premier temps, puis la ligne suivante devrait apparaitre:
```bash
2025-03-11T15:39:37.298327Z  INFO actix_server::server: starting service: "actix-web-service-0.0.0.0:8080", workers: 12, listening on: 0.0.0.0:8080
```

Signifiant que le serveur web est bien en cours d'exécution, vous pouvez vous rendre sur votre navigateur sur l'URL http://localhost:8080, qui vous permettra d'accéder à l'interface web du projet.

## Utilisation de l'interface web

Pour analyser un email, vous devez, dans un premier temps, créer un compte.  
Pour cela, vous pouvez soit cliquer sur l'icône de personnage en blanc (haut à droite de la barre de navigation) ou vous rendre sur l'URL http://localhost/auth/register  
Une fois votre compte créé, connectez-vous, puis vous pourrez accéder à la page d'analyse d'email (http://localhost:8080/predict) ou à l'historique (http://localhost:8080/history).
