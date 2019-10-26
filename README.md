# Matcha
Unit Factory educational project.

### Subject
Create a "Dating" Web Application, which allows two potential lovers to meet.
It's written in **Python Flask** framework for back-end and **Vue.js** with **Bootstrap 4** for front-end.
The main constraints for this project is no ORM, validators and User Accounts Manager.

### Prerequisites and running
install Docker.
Set environment variables inside .env file
```
cd matcha

Container for mysql
1. docker build -t mysql:latest mysql/
2. docker container run -d -p 3308:3306 --name mysql mysql

Container for server
1. docker build -t matcha:latest server/
2. docker container run -it -p 80:80 -v $(pwd):/matcha --name matcha matcha
```
