import os
import secrets
from flask import render_template, url_for, flash, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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
	def check_img_extension(filename):
		return '.' in filename and filename.rsplit('.', 1)[1] in ["png", "jpg", "jpeg"]

	@staticmethod
	def get_user_info(login):
		sql = ("SELECT id, login, email, confirmed, name, surname, gender, preferences, biography, avatar "
			   "FROM users WHERE login=%s")
		cur = db.query(sql, [login])
		return cur.fetchone()

	@staticmethod
	def email_confirmation(email, login, token):
		send_email("Thank's for the signing-up to Matcha",
				   app.config["ADMINS"][0],
				   [email],
				   "You should confirm your E-mail!",
				   render_template('signup_email.html', login=login, token=token))

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
			Account.email_confirmation(form["email"], form["login"], token)
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
							   "It seems you want to change your password?",
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
	def change(form, files=None):
		errors = []
		email_confirmed = True
		try:
			user = Account.get_user_info(session["user"])
			if user["email"] != form["email"]:
				if Account.check_email_existant(form["email"]):
					errors.append("User with this E-mail already exists")
				else:
					email_confirmed = False
			avatar_filename = user["avatar"]
			if "avatar" in files and Account.check_img_extension(files["avatar"].filename):
				avatar_filename = secure_filename(files["avatar"].filename)
				avatar_filename = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
				files["avatar"].save(avatar_filename)
			if len(errors) == 0:
				sql = ("UPDATE `users` "
					   "SET email=%s, name=%s, surname=%s, gender=%s, preferences=%s, biography=%s, confirmed=%s, avatar=%s "
					   "WHERE login=%s")
				db.query(sql, [
					form["email"],
					form["name"],
					form["surname"],
					form["gender"],
					form["preferences"],
					form["biography"],
					email_confirmed,
					avatar_filename,
					user["login"]
				])
				if not email_confirmed:
					Account.email_confirmation(form["email"], session["user"], user["token"])
					flash("You will have to confirm your new E-mail!")
		except KeyError:
			errors.append("You haven't set some values")
		return errors
