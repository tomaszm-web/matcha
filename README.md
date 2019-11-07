# Matcha
Unit Factory educational project.

It is a "Dating" Web Application, which allows two potential lovers to meet. It's written in **Python 
Flask** framework for back-end and **Vue.js** with **Bootstrap4** for front-end.

### Constraints
No ORM, validators and User Accounts Manager.

### Requirements
* Docker installed and docker daemon running: https://www.docker.com/
* Set email and password inside **.env** file to make email sender work

### Installation and running
Docker should be installed and run
```
sh install.sh
```
Wait ~10 seconds until mysql container starts working
Open this link **docker-host-ip:80**
Enjoy _Matcha_

You can also uninstall all images and containers by writing:
```
sh uninstall.sh
```

### Usage
You can search for your potential lovers using advanced search
![Matcha](static/img/screenshot1.jpg?raw=true)

You should like the user and he/she will receive the notification and will be able to like you back.
![Matcha](https://https://github.com/o4eredko/matcha/app/static/img/screenshot2.jpg)

After you like each other, you can text in the chat.
![Matcha](https://https://github.com/o4eredko/matcha/app/static/img/screenshot3.jpg)
