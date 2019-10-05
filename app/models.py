import os
import json
import secrets
import pygeoip
from datetime import datetime
from flask import render_template, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.mail import send_email
from app import app


class Account:
	def __init__(self, db):
		self.db = db

	def check_login_existent(self, login):
		sql = "SELECT * FROM `users` WHERE login=%s"
		row_num = self.db.get_row_num(sql, (login,))
		return row_num > 0

	def check_email_existent(self, email):
		sql = "SELECT * FROM `users` WHERE email=%s"
		row_num = self.db.get_row_num(sql, (email,))
		return row_num > 0

	def check_img_extension(self, filename):
		return '.' in filename and filename.rsplit('.', 1)[1] in ["png", "jpg", "jpeg"]

	def get_fame_rating(self, user_id, search_in=None):
		if not search_in:
			sql = "SELECT liked_user, COUNT(liked_user) as like_num FROM `likes` GROUP BY liked_user"
			search_in = self.db.get_all_rows(sql)
		user_like_num = 0
		max_likes = max(row['like_num'] for row in search_in)
		for row in search_in:
			if row['liked_user'] == user_id:
				user_like_num = row['like_num']
		if not max_likes:
			return 0
		return round(user_like_num / max_likes * 100)

	def get_tags(self, user_id):
		sql = ("SELECT tags.name FROM `tags` "
			   "INNER JOIN `users_tags` ON tags.id = users_tags.tag_id "
			   "WHERE users_tags.user_id = %s")
		tags = self.db.get_all_rows(sql, (user_id,))
		tags = tuple(k['name'] for k in tags)
		return tags

	def get_user_info(self, id, extended=True):
		if not id:
			return None
		sql = ("SELECT id, login, email, confirmed, name, surname, gender, preferences,"
			   "biography, avatar, photos, age, online, last_login, city, token FROM `users`  WHERE id=%s")
		user = self.db.get_row(sql, [id])
		if extended:
			user['tags'] = self.get_tags(user["id"])
			user['liked_users'] = self.get_liked_users(user['id'])
			user['blocked_users'] = self.get_blocked_users(user['id'])
			user['reported_users'] = self.get_reported_users(user['id'])
			user['checked_users'] = self.get_checked_users(user['id'])
			user['photos'] = json.loads(user['photos'])
			user['fame'] = self.get_fame_rating(user['id'])
		return user

	def create_filter_func(self, user_match):
		return lambda e: (
			e['city'] != user_match['city'],
			abs(user_match['age'] - e['age']),
			-e['fame'],
			-len(set(user_match['tags']).intersection(set(e['tags'])))
		)

	def filter_by_preferences(self, sql, user):
		matches = {}
		if user['preferences'] == 'heterosexual':
			gender = 'female' if user['gender'] == 'male' else 'male'
			matches[gender] = 'heterosexual'
		elif user['preferences'] == 'homosexual':
			matches[user['gender']] = 'homosexual'
		else:
			if user['gender'] == 'male':
				matches['male'] = 'homosexual'
				matches['female'] = 'heterosexual'
			else:
				matches['male'] = 'heterosexual'
				matches['female'] = 'homosexual'
		sql += ' WHERE '
		values = []
		for gender, preferences in matches.items():
			sql += "(gender=%s AND (preferences=%s OR preferences='bisexual')) OR "
			values.append(gender)
			values.append(preferences)
		sql = sql[:-4]
		return sql, values

	def filter_by_criterias(self, users, filters):
		filtered_users = []
		tags = filters.getlist('tags')
		for user in users:
			filter1 = not filters['age_from'] or user['age'] >= int(filters['age_from'])
			filter2 = not filters['age_to'] or user['age'] <= int(filters['age_to'])
			filter3 = not filters['fame_from'] or user['fame'] >= int(filters['fame_from'])
			filter4 = not filters['fame_to'] or user['fame'] <= int(filters['fame_to'])
			filter5 = not len(tags) or len(tags) == len(set(user['tags']).intersection(set(tags)))
			filter6 = not filters['city'] or filters['city'] == user['city']
			if filter1 and filter2 and filter3 and filter4 and filter5 and filter6:
				filtered_users.append(user)
		return filtered_users

	def get_all_users(self, user_match, filters=None):
		sql = "SELECT id, login, age, biography, avatar, city, gender, preferences FROM `users`"
		if user_match:
			sql, values = self.filter_by_preferences(sql, user_match)
			users = self.db.get_all_rows(sql, values)
		else:
			users = self.db.get_all_rows(sql)
		sql = "SELECT liked_user, COUNT(liked_user) as like_num FROM `likes` GROUP BY liked_user"
		fame_table = self.db.get_all_rows(sql)
		for user in users:
			user['fame'] = self.get_fame_rating(user['id'], search_in=fame_table)
			user['tags'] = self.get_tags(user['id'])
		if filters:
			users = self.filter_by_criterias(users, filters)
		if user_match:
			users = sorted(users, key=self.create_filter_func(user_match))
		return users

	def email_confirmation(self, email, login, token):
		send_email("Thank's for the signing-up to Matcha",
				   app.config["ADMINS"][0], [email],
				   "You should confirm your E-mail!",
				   render_template('signup_email.html', login=login, token=token))

	def insert_nonexistent_tags(self, tags):
		if not tags:
			return False
		all_tags = self.db.get_all_rows("SELECT * FROM `tags`")
		all_tags_names = (tag["name"] for tag in all_tags)
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
			return None
		self.insert_nonexistent_tags(new_tags)
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
		if self.check_login_existent(form["login"]):
			raise Exception("User with this login already exists")
		if self.check_email_existent(form["email"]):
			raise Exception("User with this E-mail already exists")
		sql = "INSERT INTO `users`(login, name, surname, email, password, token) VALUES(%s, %s, %s, %s, %s, %s)"
		user_token = secrets.token_hex(10)
		self.db.query(sql, (
			form["login"],
			form["name"],
			form["surname"],
			form["email"],
			generate_password_hash(form["pass"]),
			user_token
		))
		self.email_confirmation(form["email"], form["login"], user_token)

	def login(self, form):
		sql = "SELECT id, password, confirmed FROM `users` WHERE login=%s"
		user = self.db.get_row(sql, [form['login']])
		if not user:
			raise Exception("Wrong login!")
		if not check_password_hash(user["password"], form["pass"]):
			raise Exception("Wrong password!")
		if not user["confirmed"]:
			raise Exception("You should confirm your E-mail first!")
		session["user"] = user['id']
		last_login_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql = "UPDATE `users` SET online = 1, last_login=%s WHERE id=%s"
		self.db.query(sql, [last_login_date, user['id']])

	def confirmation(self, login, token):
		sql = "SELECT token FROM `users` WHERE login=%s"
		user = self.db.get_row(sql, [login])
		if user and user["token"] == token:
			sql = "UPDATE `users` SET confirmed='1' WHERE login=%s"
			self.db.query(sql, [login])
			return True
		return False

	def reset(self, form, action):
		sql = "SELECT * FROM `users` WHERE email=%s"
		user = self.db.get_row(sql, [form["email"]])
		if action == "check":
			if not user:
				raise Exception("No user with such E-mail")
			send_email("Matcha: Reset password",
					   app.config["ADMINS"][0],
					   [form["email"]],
					   "It seems you want to change your password?",
					   render_template('reset_password.html', user=user))
		elif action == "reset":
			if form["token"] != user["token"]:
				raise Exception("Wrong token!")
			sql = "UPDATE `users` SET password=%s WHERE email=%s"
			self.db.query(sql, (generate_password_hash(form["pass"]), form["email"]))
			flash("You successfully updated your password!", 'success')

	def upload_photo(self, user_dir, photo):
		if photo and self.check_img_extension(photo.filename):
			photo_path = secure_filename(photo.filename)
			photo_path = os.path.join(user_dir, photo_path)
			if not os.path.exists(user_dir):
				os.mkdir(user_dir)
			if not os.path.exists(photo_path):
				photo.save(photo_path)
			return photo_path
		return None

	def update_user_files(self, user, files):
		if not files:
			return None
		user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user['login'])
		avatar_path = self.upload_photo(user_dir, files['avatar'])
		if avatar_path is not None:
			self.db.query('UPDATE users SET avatar = %s', (avatar_path,))
		photo_filenames = []
		photos = files.getlist('photos[]')
		for i, photo in enumerate(photos):
			photo_path = self.upload_photo(user_dir, photo)
			photo_filenames.append(photo_path if photo_path else user['photos'][i])
		if len(photo_filenames) > 0:
			self.db.query('UPDATE users SET photos = %s WHERE id = %s', (json.dumps(photo_filenames), user['id']))

	def get_changed_values(self, prev_val, new_val):
		"""Checks which values were updated"""
		ignored = ('tags', 'csrf_token')
		values = [val for key, val in new_val.items() if key not in ignored and str(prev_val[key]) != val]
		sql = ', '.join(f"{key} = %s" for key, val in new_val.items() if key not in ignored and str(prev_val[key]) != val)
		need_confirmation = new_val['email'] in values
		if need_confirmation:
			sql += ", confirmed='0'"
		return sql, values, need_confirmation

	def change(self, form, files=None):
		user = self.get_user_info(session['user'])
		sql, values, need_confirmation = self.get_changed_values(user, form)
		# for a, b in form.items():
		if need_confirmation and self.check_email_existent(form["email"]):
			raise Exception("User with his E-mail already exists")
		if len(values) > 0:
			sql = f"UPDATE `users` SET {sql} WHERE id=%s"
			values.append(user['id'])
			self.db.query(sql, values)
		self.update_users_tags(user, form.getlist('tags'))
		self.update_user_files(user, files)
		if need_confirmation:
			self.email_confirmation(form["email"], user['login'], user["token"])
			flash("You will have to confirm your new E-mail!", 'success')

	def get_liked_users(self, user_id):
		sql = "SELECT * FROM `likes` WHERE like_owner=%s"
		response = self.db.get_all_rows(sql, [user_id])
		liked_users = (k["liked_user"] for k in response)
		return liked_users

	def get_blocked_users(self, user_id):
		sql = "SELECT * FROM `blocked` WHERE user_id=%s"
		response = self.db.get_all_rows(sql, [user_id])
		blocked_users = (k["blocked_id"] for k in response)
		return blocked_users

	def get_reported_users(self, user_id):
		sql = "SELECT * FROM `reports` WHERE user_id=%s"
		response = self.db.get_all_rows(sql, [user_id])
		reported_users = (k["reported_id"] for k in response)
		return reported_users

	def get_checked_users(self, user_login):
		sql = "SELECT * FROM `checked_profile` WHERE checking=%s"
		response = self.db.get_all_rows(sql, [user_login])
		liked_users = (k["checked_user"] for k in response)
		return liked_users

	def like_user(self, like_owner, like_to, unlike):
		if unlike == "True":
			sql = "DELETE FROM `likes` WHERE like_owner=%s AND liked_user=%s"
			action = 'unlike'
		else:
			sql = "SELECT * FROM `likes` WHERE like_owner=%s AND liked_user=%s"
			if self.db.get_row_num(sql, (like_to, like_owner)) > 0:
				action = 'like_back'
			else:
				action = 'like'
			sql = "INSERT INTO `likes` SET like_owner=%s, liked_user=%s"
		self.db.query(sql, (like_owner, like_to))
		return action

	def block_user(self, user_id, blocked_id, unblock):
		if unblock == 'true':
			sql = "DELETE FROM `blocked` WHERE user_id=%s AND blocked_id=%s"
		else:
			sql = "INSERT INTO `blocked` SET user_id=%s, blocked_id=%s"
		self.db.query(sql, (user_id, blocked_id))

	def report_user(self, user_id, reported_id, unreport):
		if unreport == 'true':
			sql = "DELETE FROM `reports` WHERE user_id=%s AND reported_id=%s"
		else:
			sql = "INSERT INTO `reports` SET user_id=%s, reported_id=%s"
		self.db.query(sql, (user_id, reported_id))

	def check_user(self, checking, checked_user):
		sql = "INSERT INTO `checked_profile` SET checking=%s, checked_user=%s"
		self.db.query(sql, (checking, checked_user))


class Chat:
	def __init__(self, db):
		self.db = db
		self.timestamp_format = "%c"

	def __del__(self):
		del self.db

	def send_message(self, sender_id, recipient_id, message_text):
		sql = "INSERT INTO `messages` SET sender_id=%s, recipient_id=%s, body=%s"
		self.db.query(sql, (sender_id, recipient_id, message_text))

	def get_messages(self, user_id, recipient_id):
		sql = ("SELECT * FROM `messages` WHERE (sender_id=%s AND recipient_id=%s)"
			   "OR (sender_id=%s AND recipient_id=%s) ORDER BY timestamp")
		messages = self.db.get_all_rows(sql, (user_id, recipient_id, recipient_id, user_id))
		for message in messages:
			message['timestamp'] = datetime.strftime(message['timestamp'], self.timestamp_format)
		return messages


class Notif:
	def __init__(self, db):
		self.db = db
		self.timestamp_format = "%c"

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
			'message': url_for('chat', recipient_id=executive_user['id'])
		}
		sql = "INSERT INTO `notifications` (user_id, message, link) VALUES (%s, %s, %s)"
		link = 'message' if notif_type == 'message' else 'user_action'
		self.db.query(sql, (recipient_id, notifications[notif_type], links[link]))

	def get_notifications(self, user_id):
		sql = "SELECT * FROM `notifications` WHERE user_id=%s AND viewed=0 ORDER BY date_created DESC"
		notifications = self.db.get_all_rows(sql, [user_id])
		for notif in notifications:
			notif['date_created'] = datetime.strftime(notif['date_created'], self.timestamp_format)
		return notifications

	def del_viewed_notifs(self, viewed_notifs):
		arr_len = len(viewed_notifs)
		sql = "DELETE FROM `notifications` WHERE id IN ("
		for i in range(arr_len):
			sql += "%s, "
		sql = sql[:-2] + ")"
		self.db.query(sql, viewed_notifs)
