import secrets
from flask import render_template, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.mail import send_email


class Ajax:
	def registration(self, form):
		errors = []

		sql = "SELECT * FROM `users` WHERE login=%s"
		cur = db.query(sql, (form["login"]))
		if cur.rowcount > 0:
			errors.append("User with this login already exists")
		sql = "SELECT * FROM `users` WHERE email=%s"
		cur = db.query(sql, (form["email"]))
		if cur.rowcount > 0:
			errors.append("User with this E-mail already exists")

		sql = "INSERT INTO `users`(login, name, surname, email, password, token) VALUES(%s, %s, %s, %s, %s, %s)"
		token = secrets.token_hex(10)
		db.query(sql, (
			form["login"],
			form["name"],
			form["surname"],
			form["email"],
			generate_password_hash(form["pass"]),
			token
		))
		send_email("Thank's for the signing-up to Matcha",
					app.config["ADMINS"][0],
					[form["email"]],
					"Unfortunately, html markup doesn't work at your mail client!",
					render_template('signup_email.html', user=form, token=token))
		return errors

	def confirmation(self, login, token):
		sql = "SELECT token FROM `users` WHERE login=%s"
		cur = db.query(sql, (login))
		if cur.fetchone() == token:
			sql = "UPDATE `users`(confirmation) WHERE id=%s VALUES(1)"
			db.query(sql, (login))
			return True
		return False
