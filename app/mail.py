from threading import Thread

from flask_mail import Message

from flask import render_template
from app import app, mail

admin = app.config['ADMIN']


def send_async_email(application, msg):
	with application.app_context():
		mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender=sender, recipients=recipients)
	msg.body = text_body
	msg.html = html_body
	Thread(target=send_async_email, args=(app, msg)).start()


def confirm_email_mail(email, login, token):
	template = render_template('signup_email.html', email=email, login=login, token=token)
	send_email("Thank's for the signing-up to Matcha", admin, [email],
			   "You should confirm your E-mail!", template)


def reset_password_mail(user):
	template = render_template('reset_password.html', user=user)
	send_email("Matcha: Reset password", admin, [user.email],
			   "It seems you want to change your password?", template)
