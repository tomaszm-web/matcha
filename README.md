# Matcha
Unit Factory educational project.

### Subject
Create a "Dating" Web Application, which allows two potential lovers to meet.
It's written in **Python Flask** framework for back-end and **Vue.js** with **Bootstrap 4** for front-end.
The main constraints for this project is no ORM, validators and User Accounts Manager.

### Prerequisites
Docker installed.
Set environment variables inside dockerfile

### Running the program
```
docker image build -t matcha:latest .
docker container -p 8800:80 --name matcha -v src/:/matcha matcha
```
Usage:
1. docker build -t matcha:latest .
2. docker run -p 8080:80 matcha:latest
