# API
---

API du serveur

## Auth

- login
- register

## Email

- predict

## Lancement

Pour mettre en route l'interface web, vous devez rester dans le répertoire `Backend/` et utiliser la commande suivante:  

```bash
cargo run -- --prod
```

## Database

Pour initialiser la base de donnée, il faut un serveur mysql et créer la base de donnée ainsi que l'utilisateur.  
  
Ci-dessous un exemple pour créer l'utilisateur et la base de données pour ce projet :

```mysql
CREATE DATABASE trapyourphish DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'trapyourphish'@'%' IDENTIFIED BY 'SUPERPASSWORD';
GRANT USAGE ON *.* TO 'trapyourphish'@'%';
GRANT ALL PRIVILEGES ON trapyourphish.* TO 'trapyourphish'@'%';
FLUSH PRIVILEGES;
```

Les identifiants de la base de données doivent être renseignés dans le fichier `config/default.json`

## Dockerfile

Le dockerfile n'est pour l'instant pas encore fonctionnel pour l'application
