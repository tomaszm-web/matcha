import os
import json
import secrets
from flask import render_template, url_for, flash, redirect, session, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.mail import send_email
from app import app


class Account:
	def __init__(self, db):
		self.db = db

	def __del__(self):
		del self.db

	def check_login_existent(self, login):
		sql = "SELECT * FROM `users` WHERE login=%s"
		row_num = self.db.get_row_num(sql, [login])
		return row_num > 0

	def check_email_existent(self, email):
		sql = "SELECT * FROM `users` WHERE email=%s"
		row_num = self.db.get_row_num(sql, [email])
		return row_num > 0

	def check_img_extension(self, filename):
		return '.' in filename and filename.rsplit('.', 1)[1] in ["png", "jpg", "jpeg"]

	def get_fame_rating(self, user_id):
		sql = "SELECT liked_user, COUNT(liked_user) as like_num FROM `likes` GROUP BY liked_user"
		response = self.db.get_all_rows(sql)
		max_likes_num = None
		user_like_num = None
		for row in response:
			if not max_likes_num or max_likes_num < row['like_num']:
				max_likes_num = row['like_num']
			if row['liked_user'] == user_id:
				user_like_num = row['like_num']
		if not max or not user_like_num:
			return 0
		return user_like_num / max_likes_num * 100

	def get_tags(self, user_id):
		sql = ("SELECT tags.name FROM `tags` "
			   "INNER JOIN `users_tags` ON tags.id = users_tags.tag_id "
			   "WHERE users_tags.user_id = %s")
		tags = self.db.get_all_rows(sql, [user_id])
		tags = [k['name'] for k in tags]
		return tags

	def get_user_info(self, login=None, id=None):
		if not login and not id:
			return None
		sql = ("SELECT id, login, email, confirmed, name, surname, gender, preferences,"
			   "biography, avatar, photos, age FROM `users`")
		if login:
			sql += " WHERE login=%s"
			user = self.db.get_row(sql, [login])
		elif id:
			sql += " WHERE id=%s"
			user = self.db.get_row(sql, [id])
		user['tags'] = self.get_tags(user["id"])
		user['liked_users'] = self.get_liked_users(user['id'])
		user['checked_users'] = self.get_checked_users(user['id'])
		user['photos'] = json.loads(user['photos'])
		user['fame'] = self.get_fame_rating(user['id'])
		# user['notifications'] = Notif.get_notifications(user['id'])
		return user

	def handle_filters(self, user):
		# todo Fame rating, location
		match = {}
		if user['preferences'] == 'heterosexual':
			match['gender'] = 'female' if user['gender'] == 'male' else 'male'
			match['preferences'] = ['heterosexual', 'bisexual']
		else:
			if user['preferences'] == 'homosexual':
				match['gender'] = user['gender']
			match['preferences'] = ['homosexual', 'bisexual']
		return match

	def get_all_users(self, user_match=None):
		# todo sort by age, fame rating
		if user_match:
			match = self.handle_filters(user_match)
			sql = ("SELECT id, login, name, surname, gender, preferences, biography, avatar FROM `users`"
				   "ORDER BY ABS(%s - age)")
			users = self.db.get_all_rows(sql, [user_match['age']])
		else:
			sql = "SELECT id, login, name, surname, gender, preferences, biography, avatar FROM `users`"
			users = self.db.get_all_rows(sql)
		for user in users:
			user["tags"] = self.get_tags(user["id"])
		return users

	def email_confirmation(self, email, login, token):
		send_email("Thank's for the signing-up to Matcha",
				   app.config["ADMINS"][0],
				   [email],
				   "You should confirm your E-mail!",
				   render_template('signup_email.html', login=login, token=token))

	def insert_unexistant_tags(self, tags):
		if not tags:
			return False
		all_tags = self.db.get_all_rows("SELECT * FROM `tags`")
		all_tags_names = [tag["name"] for tag in all_tags]
		sql = "INSERT INTO `tags` (name) VALUES"
		tag_list = []
		for tag_name in tags:
			if tag_name not in all_tags_names:
				sql += " (%s),"
				tag_list.append(tag_name)
		if len(tag_list):
			self.db.query(sql[:-1], tag_list)

	def update_users_tags(self, user, new_tags):
		if new_tags and user['tags'] == new_tags:
			return
		self.insert_unexistant_tags(new_tags)
		all_tags = self.db.get_all_rows("SELECT * FROM `tags`")

		sql = "DELETE FROM `users_tags` WHERE user_id=%s"
		self.db.query(sql, [user["id"]])
		sql = "INSERT INTO `users_tags` (user_id, tag_id) VALUES"
		tag_list = []
		for tag in new_tags:
			sql += " (%s, %s),"
			tag_id = next(item["id"] for item in all_tags if item["name"] == tag)
			tag_list.append(user["id"])
			tag_list.append(tag_id)
		if len(tag_list):
			self.db.query(sql[:-1], tag_list)

	def registration(self, form):
		errors = []
		try:
			if self.check_login_existent(form["login"]):
				errors.append("User with this login already exists")
			if self.check_email_existent(form["email"]):
				errors.append("User with this E-mail already exists")
			if len(errors) == 0:
				sql = "INSERT INTO `users`(login, name, surname, email, password, token) VALUES(%s, %s, %s, %s, %s, %s)"
				token = secrets.token_hex(10)
				self.db.query(sql, (
					form["login"],
					form["name"],
					form["surname"],
					form["email"],
					generate_password_hash(form["pass"]),
					token
				))
				self.email_confirmation(form["email"], form["login"], token)
		except KeyError:
			errors.append("You haven't set some values")
		return errors

	def login(self, form):
		errors = []
		try:
			sql = "SELECT * FROM `users` WHERE login=%s"
			user = self.db.get_row(sql, [form["login"]])
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

	def confirmation(self, login, token):
		sql = "SELECT token FROM `users` WHERE login=%s"
		user = self.db.get_row(sql, [login])
		if user and user["token"] == token:
			sql = "UPDATE `users` SET confirmed='1' WHERE login=%s"
			self.db.query(sql, [login])
			return True
		return False

	def reset(self, form, action):
		errors = []
		try:
			sql = "SELECT * FROM `users` WHERE email=%s"
			user = self.db.get_row(sql, (form["email"]))
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
					self.db.query(sql, (generate_password_hash(form["pass"]), form["email"]))
					flash("You successfully updated your password!", 'success')
		except KeyError:
			errors.append("You haven't set some values")
		return errors

	def upload_photo(self, user_dir, photo):
		if photo and self.check_img_extension(photo.filename):
			photo_path = secure_filename(photo.filename)
			photo_path = os.path.join(user_dir, photo_path)
			if not os.path.exists(user_dir):
				os.mkdir(user_dir)
			if not os.path.exists(photo_path):
				photo.save(photo_path)
			return photo_path
		return False

	def update_user_files(self, user, files, to_update):
		if not files:
			return False
		user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user['login'])
		avatar_path = self.upload_photo(user_dir, files['avatar'])
		if avatar_path:
			to_update['sql'] += ', avatar=%s' if len(to_update['values']) else 'avatar=%s'
			to_update['values'].append(avatar_path)

		photos_filenames = []
		photos = files.getlist('photos[]')
		for i, photo in enumerate(photos):
			photo_path = self.upload_photo(user_dir, photo)
			photos_filenames.append(photo_path if photo_path else user['photos'][i])
		if len(photos_filenames):
			to_update['sql'] += ', photos=%s' if len(to_update['values']) else 'photos=%s'
			to_update['values'].append(json.dumps(photos_filenames))

	def get_changed_values(self, prev_val, new_val):
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

	def change(self, form, files=None):
		user = self.get_user_info(session["user"])
		to_update = self.get_changed_values(user, form)
		if 'email' in to_update['values'] and self.check_email_existent(form["email"]):
			raise Exception("User with his E-mail already exists")
		self.update_users_tags(user, form.getlist('tags'))
		self.update_user_files(user, files, to_update)
		if len(to_update['values']) > 0:
			sql = "UPDATE `users` SET " + to_update['sql'] + " WHERE id=%s"
			to_update['values'].append(user['id'])
			self.db.query(sql, to_update['values'])
		if 'confirmed' in to_update:
			self.email_confirmation(form["email"], session["user"], user["token"])
			flash("You will have to confirm your new E-mail!", 'success')

	def get_liked_users(self, user_login):
		sql = "SELECT * FROM `likes` WHERE like_owner=%s"
		response = self.db.get_all_rows(sql, [user_login])
		liked_users = [k["liked_user"] for k in response]
		return liked_users

	def get_checked_users(self, user_login):
		sql = "SELECT * FROM `checked_profile` WHERE checking=%s"
		response = self.db.get_all_rows(sql, [user_login])
		liked_users = [k["checked_user"] for k in response]
		return liked_users

	def like_user(self, like_owner, like_to, unlike):
		if unlike == 'true':
			sql = "DELETE FROM `likes` WHERE like_owner=%s AND liked_user=%s"
			action = 'unlike'
		else:
			sql = "SELECT * FROM `likes` WHERE like_owner=%s AND liked_user=%s"
			if self.db.get_row_num(sql, [like_to, like_owner]) > 0:
				action = 'like_back'
			else:
				action = 'like'
			sql = "INSERT INTO `likes` SET like_owner=%s, liked_user=%s"
		self.db.query(sql, [like_owner, like_to])
		return action

	def check_user(self, checking, checked_user):
		sql = "INSERT INTO `checked_profile` SET checking=%s, checked_user=%s"
		self.db.query(sql, [checking, checked_user])


class Chat:
	def __init__(self, db):
		self.db = db

	def __del__(self):
		del self.db

	def send_message(self, sender_id, recipient_id, message_text):
		sql = "INSERT INTO `messages` SET sender_id=%s, recipient_id=%s, body=%s"
		self.db.query(sql, (sender_id, recipient_id, message_text))

	def get_messages(self, user_id, recipient_id):
		sql = ("SELECT * FROM `messages` WHERE (sender_id=%s AND recipient_id=%s)"
			   "OR (sender_id=%s AND recipient_id=%s) ORDER BY timestamp DESC")
		messages = self.db.get_all_rows(sql, (user_id, recipient_id, recipient_id, user_id))
		return messages


class Notif:
	def __init__(self, db):
		self.db = db

	def __del__(self):
		del self.db

	def send_notification(self, recipient_id, notif_type, executive_user):
		notifications = {
			'like': f"You have been liked by {executive_user['login']}",
			'unlike': f"You have been unliked by {executive_user['login']}",
			'check_profile': f"Your profile was checked by {executive_user['login']}",
			'message': f"You received a message from {executive_user['login']}",
			'like_back': f"You have been liked back by {executive_user['login']}"
		}
		links = {
			'user_action': url_for('profile', user_id=executive_user['id']),
			'message': url_for('chat', recipient_id_id=executive_user['id'])
		}
		sql = "INSERT INTO `notifications` (user_id, message, link) VALUES (%s, %s, %s)"
		link = 'message' if notif_type == 'message' else 'user_action'
		self.db.query(sql, (recipient_id, notifications[notif_type], links[link]))

	def get_notifications(self, user_id):
		sql = "SELECT * FROM `notifications` WHERE user_id=%s AND viewed=0 ORDER BY date_created DESC"
		notifications = self.db.get_all_rows(sql, [user_id])
		return notifications
