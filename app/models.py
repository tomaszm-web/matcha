import os
import json
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
	def get_tags(user_id):
		sql = ("SELECT tags.name FROM `tags` "
			   "INNER JOIN `users_tags` ON tags.id = users_tags.tag_id "
			   "WHERE users_tags.user_id = %s")
		tags = db.get_all_rows(sql, [user_id])
		tags = [k['name'] for k in tags]
		return tags

	@staticmethod
	def get_user_info(login=None, id=None):
		if not login and not id:
			return None
		sql = ("SELECT id, login, email, confirmed, name, surname, gender, preferences,"
			   "biography, avatar, photos, age FROM `users`")
		if login:
			sql += " WHERE login=%s"
			user = db.get_row(sql, [login])
		elif id:
			sql += " WHERE id=%s"
			user = db.get_row(sql, [id])
		user['tags'] = Account.get_tags(user["id"])
		user['liked_users'] = Account.get_liked_users(user['id'])
		user['photos'] = json.loads(user['photos'])
		user['notifications'] = Notif.get_notifications(user['id'])
		return user

	@staticmethod
	def get_all_users(sorted=None):
		sql = "SELECT id, login, name, surname, gender, preferences, biography, avatar FROM `users`"
		users = db.get_all_rows(sql)
		for user in users:
			user["tags"] = Account.get_tags(user["id"])
		return users

	@staticmethod
	def email_confirmation(email, login, token):
		send_email("Thank's for the signing-up to Matcha",
				   app.config["ADMINS"][0],
				   [email],
				   "You should confirm your E-mail!",
				   render_template('signup_email.html', login=login, token=token))

	@staticmethod
	def insert_unexistant_tags(tags):
		if not tags:
			return False
		all_tags = db.get_all_rows("SELECT * FROM `tags`")
		all_tags_names = [tag["name"] for tag in all_tags]
		sql = "INSERT INTO `tags` (name) VALUES"
		tag_list = []
		for tag_name in tags:
			if tag_name not in all_tags_names:
				sql += " (%s),"
				tag_list.append(tag_name)
		if len(tag_list):
			db.query(sql[:-1], tag_list)

	@staticmethod
	def update_users_tags(user, new_tags):
		if new_tags and user['tags'] == new_tags:
			return
		Account.insert_unexistant_tags(new_tags)
		all_tags = db.get_all_rows("SELECT * FROM `tags`")

		sql = "DELETE FROM `users_tags` WHERE user_id=%s"
		db.query(sql, [user["id"]])
		sql = "INSERT INTO `users_tags` (user_id, tag_id) VALUES"
		tag_list = []
		for tag in new_tags:
			sql += " (%s, %s),"
			tag_id = next(item["id"] for item in all_tags if item["name"] == tag)
			tag_list.append(user["id"])
			tag_list.append(tag_id)
		if len(tag_list):
			db.query(sql[:-1], tag_list)

	@staticmethod
	def registration(form):
		errors = []
		try:
			if Account.check_login_existant(form["login"]):
				errors.append("User with this login already exists")
			if Account.check_email_existant(form["email"]):
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
		except KeyError:
			errors.append("You haven't set some values")
		return errors

	@staticmethod
	def login(form):
		errors = []
		try:
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
				flash("You successfully logged in!", 'success')
		except KeyError:
			errors.append("You haven't set some values")
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
					flash("You successfully updated your password!", 'success')
		except KeyError:
			errors.append("You haven't set some values")
		return errors

	@staticmethod
	def upload_photo(user_dir, photo):
		if photo and Account.check_img_extension(photo.filename):
			photo_path = secure_filename(photo.filename)
			photo_path = os.path.join(user_dir, photo_path)
			if not os.path.exists(user_dir):
				os.mkdir(user_dir)
			if not os.path.exists(photo_path):
				photo.save(photo_path)
			return photo_path
		return False

	@staticmethod
	def update_user_files(user, files, to_update):
		if not files:
			return False
		user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user['login'])
		avatar_path = Account.upload_photo(user_dir, files['avatar'])
		if avatar_path:
			to_update['sql'] += ', avatar=%s' if len(to_update['values']) else 'avatar=%s'
			to_update['values'].append(avatar_path)

		photos_filenames = []
		photos = files.getlist('photos[]')
		for i, photo in enumerate(photos):
			photo_path = Account.upload_photo(user_dir, photo)
			photos_filenames.append(photo_path if photo_path else user['photos'][i])
		if len(photos_filenames):
			to_update['sql'] += ', photos=%s' if len(to_update['values']) else 'photos=%s'
			to_update['values'].append(json.dumps(photos_filenames))

	@staticmethod
	def get_changed_values(prev_val, new_val):
		sql = ''
		values = []
		ignored_values = ['login', 'tags']
		for key, val in new_val.items():
			if key not in ignored_values and prev_val[key] != val:
				sql += (key + '=%s, ')
				values.append(val)
		if 'email' in values:
			sql += "confirmed='0', "
		if len(values):
			sql = sql[:-2]
		return {'sql': sql, 'values': values}

	@staticmethod
	def change(form, files=None):
		user = Account.get_user_info(session["user"])
		to_update = Account.get_changed_values(user, form)
		if 'email' in to_update['values'] and Account.check_email_existant(form["email"]):
			raise Exception("User with his E-mail already exists")
		Account.update_users_tags(user, form.getlist('tags'))
		Account.update_user_files(user, files, to_update)
		if len(to_update['values']) > 0:
			sql = "UPDATE `users` SET " + to_update['sql'] + " WHERE id=%s"
			to_update['values'].append(user['id'])
			db.query(sql, to_update['values'])
		if 'confirmed' in to_update:
			Account.email_confirmation(form["email"], session["user"], user["token"])
			flash("You will have to confirm your new E-mail!", 'success')

	@staticmethod
	def get_liked_users(user_login):
		sql = "SELECT * FROM `likes` WHERE like_owner=%s"
		response = db.get_all_rows(sql, [user_login])
		liked_users = [k["liked_user"] for k in response]
		return liked_users

	@staticmethod
	def like_user(like_owner, like_to):
		sql = "INSERT INTO `likes` SET like_owner = %s, liked_user = %s"
		db.query(sql, [like_owner, like_to])


class Chat:
	@staticmethod
	def send_message(sender_id, recipient_id, message_text):
		sql = "INSERT INTO `messages` SET sender_id=%s, recipient_id=%s, body=%s"
		db.query(sql, (sender_id, recipient_id, message_text))

	@staticmethod
	def get_messages(user_id, recipient_id):
		sql = ("SELECT * FROM `messages` WHERE (sender_id=%s AND recipient_id=%s)"
			   "OR (sender_id=%s AND recipient_id=%s) ORDER BY timestamp")
		messages = db.get_all_rows(sql, (user_id, recipient_id, recipient_id, user_id))
		return messages


class Notif:
	@staticmethod
	def send_notification(user_id, message_text):
		sql = "INSERT INTO `notifications` (user_id, message) VALUES (%s, %s)"
		db.query(sql, (user_id, message_text))

	@staticmethod
	def get_notifications(user_id):
		sql = "SELECT * FROM `notifications` WHERE user_id=%s AND viewed=0 ORDER BY date_created"
		notifications = db.get_all_rows(sql, [user_id])
		notifications = [k['message'] for k in notifications]
		return notifications

# 	todo redo errors implementation(Return after the first error)
