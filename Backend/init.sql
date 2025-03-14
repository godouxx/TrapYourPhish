CREATE DATABASE trapyourphish DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'trapyourphish'@'%' IDENTIFIED BY 'SUPERPASSWORD';
GRANT USAGE ON *.* TO 'trapyourphish'@'%';
GRANT ALL PRIVILEGES ON trapyourphish.* TO 'trapyourphish'@'%';
FLUSH PRIVILEGES;
