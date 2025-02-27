# API
---

API du serveur

## Auth

- login
- signup

## Email

- predict
- bulkpredict

## Lancement

```bash
cargo run -- --prod
```

## Database

Pour initialiser la base de donnée, il faut un serveur mysql et créer la base de donnée ainsi que l'utilisateur:

```mysql
CREATE DATABASE trapyourphish DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'trapyourphish'@'%' IDENTIFIED BY 'SUPERPASSWORD';
GRANT USAGE ON *.* TO 'trapyourphish'@'%';
GRANT ALL PRIVILEGES ON trapyourphish.* TO 'trapyourphish'@'%';
FLUSH PRIVILEGES;
```

