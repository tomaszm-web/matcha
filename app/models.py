import secrets
from flask import render_template, url_for, flash, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.mail import send_email


class Account:
	@staticmethod
	def check_login_existant(login):
		sql = "SELECT * FROM `users` WHERE login=%s"
		cur = db.query(sql, [login])
		return cur.rowcount > 0

	@staticmethod
	def check_email_existant(email):
		sql = "SELECT * FROM `users` WHERE email=%s"
		cur = db.query(sql, [email])
		return cur.rowcount > 0

	@staticmethod
	def get_user_info(login):
		sql = "SELECT id, login, email, confirmed, name, surname, gender, preferences, biography FROM users WHERE login=%s"
		cur = db.query(sql, [login])
		return cur.fetchone()

	@staticmethod
	def registration(form):
		errors = []
		if Account.check_login_existant(form["login"]):
			errors.append("User with this login already exists")
		if Account.check_email_existant(form["login"]):
			errors.append("User with this E-mail already exists")
		if len(errors) == 0:
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
						render_template('signup_email.html', login=form["login"], token=token))
		return errors

	@staticmethod
	def login(form):
		errors = []
		sql = "SELECT * FROM `users` WHERE login=%s"
		cur = db.query(sql, (form["login"]))
		user = cur.fetchone()
		if not user:
			errors.append("Wrong login!")
		elif not check_password_hash(user["password"], form["pass"]):
			errors.append("Wrong password!")
		elif not user["confirmed"]:
			errors.append("You should confirm your E-mail first!")
		else:
			session["user"] = form["login"]
			flash("You successfully logged in!")
		return errors

	@staticmethod
	def confirmation(login, token):
		sql = "SELECT token FROM `users` WHERE login=%s"
		cur = db.query(sql, (login))
		if cur.fetchone()["token"] == token:
			sql = "UPDATE `users` SET confirmed=1 WHERE login=%s"
			db.query(sql, (login))
			return True
		return False

	@staticmethod
	def reset(form, action):
		errors = []
		try:
			sql = "SELECT * FROM `users` WHERE email=%s"
			cur = db.query(sql, (form["email"]))
			user = cur.fetchone()
			if action == "check":
				if not user:
					errors.append("No user with such E-mail")
				else:
					send_email("Matcha: Reset password",
								app.config["ADMINS"][0],
								[form["email"]],
								"Unfortunately, html markup doesn't work at your mail client!",
								render_template('reset_password.html', user=user))
			elif action == "reset":
				if form["token"] != user["token"]:
					errors.append("Wrong token!")
				else:
					sql = "UPDATE `users` SET password=%s WHERE email=%s"
					db.query(sql, (generate_password_hash(form["pass"]), form["email"]))
					flash("You successfully updated your password!")
		except KeyError:
			errors.append("You haven't set some values")
		return errors

	@staticmethod
	def change(form):
		errors = []
		try:
			sql = 'UPDATE `users`SET login=%s, email=%s, name=%s, surname=%s, gender=%s, preferences=%s, biography=%s WHERE id=%s'
			db.query(sql, [
				form["login"],
				form["email"],
				form["name"],
				form["surname"],
				form["gender"],
				form["preferences"],
				form["biography"],
				form["user_id"]
			])
		except KeyError:
			errors.append("You haven't set some values")
		return errors
