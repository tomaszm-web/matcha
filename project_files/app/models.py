import os
import json
import secrets
import itertools
from datetime import datetime
import MySQLdb.cursors
from flask import render_template, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.mail import send_email
from app import app


class Account:
	def __init__(self, db):
		self.db = db

	def check_login_existent(self, login):
		sql = "SELECT COUNT(login) as row_num FROM `users` WHERE login = %s"
		row_num = self.db.get_row(sql, (login,))['row_num']
		return row_num > 0

	def check_email_existent(self, email):
		sql = "SELECT COUNT(email) as row_num FROM `users` WHERE email = %s"
		row_num = self.db.get_row(sql, (email,))['row_num']
		return row_num > 0

	def check_img_extension(self, filename):
		return '.' in filename and filename.rsplit('.', 1)[1] in ["png", "jpg", "jpeg"]

	def get_fame_rating(self, user_id=None):
		sql = "SELECT liked_user AS user, COUNT(liked_user) AS like_num FROM `likes` GROUP BY user"
		search_in = self.db.get_all_rows(sql, cursorclass=MySQLdb.cursors.Cursor)
		if not search_in:
			return 0
		max_likes = max(like_num for _, like_num in search_in)
		if user_id:
			user_likes = [like_num for user, like_num in search_in if user == user_id]
			if not user_likes:
				return 0
			return round(user_likes[0] / max_likes * 100)
		return {user_id: round(like_num / max_likes * 100) for user_id, like_num in search_in}

	def get_tags(self, user_id=None):
		if user_id:
			sql = ("SELECT tags.name FROM `tags` INNER JOIN `users_tags` "
				   "ON tags.id = users_tags.tag_id WHERE users_tags.user_id = %s")
			tags = self.db.get_all_rows(sql, (user_id,), cursorclass=MySQLdb.cursors.Cursor)
			if not tags:
				return None
			return [tag_name for tag_name, in tags]
		else:
			sql = "SELECT users_tags.user_id, tags.name FROM tags INNER JOIN users_tags ON tags.id = users_tags.tag_id"
			tags_groups = self.db.get_all_rows(sql, cursorclass=MySQLdb.cursors.Cursor)
			if not tags_groups:
				return None
			tags_groups = itertools.groupby(tags_groups, lambda pair: pair[0])
			return {user: list(tag for _, tag in group) for user, group in tags_groups}

	def check_user_info(self, user):
		return (
			user.get('avatar') and user.get('city') and user.get('biography') and
			user.get('gender') and user.get('preferences') and user.get('age')
		)

	def get_user_info(self, user_id, extended=True):
		sql = ("SELECT id, login, email, confirmed, name, surname, gender, preferences,"
			   "biography, avatar, photos, age, online, last_login, city, token FROM `users`  WHERE id = %s")
		user = self.db.get_row(sql, (user_id,))
		if not user:
			return None
		user['blocked_users'] = self.get_blocked_users(user['id'])
		if extended:
			user['tags'] = self.get_tags(user["id"])
			user['liked_users'] = self.get_liked_users(user['id'])
			user['reported_users'] = self.get_reported_users(user['id'])
			user['visited'] = self.get_visited_users(user['id'])
			user['photos'] = json.loads(user['photos'])
			user['fame'] = self.get_fame_rating(user['id'])
		return user

	def sort_func(self, user_match, sort_by=None):
		# todo location should be refactored. For example make 2 selects for city and country.
		if sort_by:
			if sort_by == 'age' or sort_by == 'fame':
				return lambda e: -e[sort_by]
			elif user_match is not None and sort_by == 'common_tags':
				return lambda e: -len(set(user_match['tags']).intersection(e['tags']))
			elif user_match is not None and sort_by == 'city':
				return lambda e: e['city'] != user_match['city']
		elif user_match is not None:
			return lambda e: (
				e['city'] != user_match['city'],
				abs(user_match['age'] - e['age']),
				-e['fame'],
				-len(set(user_match['tags']).intersection(e['tags']))
			)
		return None

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
		sql_part = "gender=%s AND (preferences=%s OR preferences='bisexual')"
		sql += ' AND ({})'.format(' OR '.join(sql_part for _ in range(len(matches))))
		values = itertools.chain.from_iterable((gender, preferences) for gender, preferences in matches.items())
		return sql, values

	def filter_by_criterias(self, users, filters):
		if not filters:
			return users
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

	def get_all_users(self, user_match, filters=None, sort_by=None):
		sql = ("SELECT id, login, age, biography, avatar, city, gender, preferences FROM `users` "
			   "WHERE NOT (biography is NULL OR age IS NULL OR city IS NULL OR gender IS NULL OR preferences IS NULL)")
		if user_match:
			sql, values = self.filter_by_preferences(sql, user_match)
			users = self.db.get_all_rows(sql, values)
		else:
			users = self.db.get_all_rows(sql)
		fame_rates = self.get_fame_rating()
		tags_groups = self.get_tags()
		for user in users:
			user['fame'] = fame_rates.get(user['id'], 0) if fame_rates else 0
			user['tags'] = tags_groups.get(user['id']) if tags_groups else None
		users = self.filter_by_criterias(users, filters)
		sort_lambda = self.sort_func(user_match, sort_by)
		if sort_lambda is not None:
			users = sorted(users, key=sort_lambda)
		return users

	def email_confirmation(self, email, login, token):
		send_email("Thank's for the signing-up to Matcha",
				   app.config["ADMINS"][0], [email],
				   "You should confirm your E-mail!",
				   render_template('signup_email.html', login=login, token=token))

	def update_user_tags(self, user, new_tags):
		if not new_tags or user['tags'] == new_tags:
			return None
		all_tags = self.db.get_all_rows("SELECT * FROM `tags`", cursorclass=MySQLdb.cursors.Cursor)
		all_tags = {tag_name for _, tag_name in all_tags}
		sql = ', '.join('%s' for tag_name in new_tags if tag_name not in all_tags)
		new_tags_set = set(new_tags)
		nonexistent_tags = new_tags_set - all_tags
		if nonexistent_tags:
			sql = f"INSERT INTO `tags` (name) VALUES ({sql})"
			self.db.query(sql, nonexistent_tags)

		sql = "DELETE FROM `users_tags` WHERE user_id=%s"
		self.db.query(sql, (user['id'],))

		all_tags = self.db.get_all_rows("SELECT * FROM `tags`", cursorclass=MySQLdb.cursors.Cursor)
		sql = ', '.join("(%s, %s)" for _ in range(len(new_tags)))
		user_tag_ids = itertools.chain.from_iterable(
			(user['id'], tag_id) for tag_id, tag_name in all_tags if tag_name in new_tags_set
		)
		if len(sql):
			sql = f"INSERT INTO `users_tags` (user_id, tag_id) VALUES {sql}"
			self.db.query(sql, user_tag_ids)

	def registration(self, form):
		if self.check_login_existent(form["login"]):
			raise Exception("User with this login already exists")
		if self.check_email_existent(form["email"]):
			raise Exception("User with this E-mail already exists")
		sql = "INSERT INTO `users`(login, name, surname, email, password, token) VALUES(%s, %s, %s, %s, %s, %s)"
		user_token = secrets.token_hex(10)
		self.db.query(sql, (
			form["login"], form["name"],
			form["surname"], form["email"],
			generate_password_hash(form["pass"]), user_token
		))
		self.email_confirmation(form["email"], form["login"], user_token)

	def login(self, form):
		sql = "SELECT id, password, confirmed FROM `users` WHERE login=%s"
		user = self.db.get_row(sql, [form['login']])
		if not user:
			raise ValueError("Wrong login!")
		if not check_password_hash(user["password"], form["pass"]):
			raise ValueError("Wrong password!")
		if not user["confirmed"]:
			raise ValueError("You should confirm your E-mail first!")
		session['user'] = user['id']
		last_login_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql = "UPDATE `users` SET online = 1, last_login = %s WHERE id = %s"
		self.db.query(sql, (last_login_date, user['id']))

	def confirmation(self, login, token):
		sql = "SELECT token FROM `users` WHERE login = %s"
		user = self.db.get_row(sql, (login,))
		if user and user["token"] == token:
			sql = "UPDATE `users` SET confirmed = 1 WHERE login = %s"
			self.db.query(sql, (login,))
			return True
		return False

	def reset(self, form, action):
		sql = "SELECT * FROM `users` WHERE email=%s"
		user = self.db.get_row(sql, [form["email"]])
		if action == "check":
			if not user:
				raise ValueError("No user with such E-mail")
			send_email("Matcha: Reset password", app.config["ADMINS"][0],
					   [form["email"]], "It seems you want to change your password?",
					   render_template('reset_password.html', user=user))
		elif action == "reset":
			if form["token"] != user["token"]:
				raise ValueError("Wrong token!")
			sql = "UPDATE `users` SET password=%s WHERE email=%s"
			self.db.query(sql, (generate_password_hash(form["pass"]), form["email"]))
			flash("You successfully updated your password!", 'success')

	def upload_photo(self, relative_dir, photo):
		"""
		Save photo in folder from app config.
		:return:filename of new photo
		"""
		if not photo or not self.check_img_extension(photo.filename):
			return None
		photo_filename = secure_filename(photo.filename)
		absolute_dir = os.path.join(app.config['UPLOAD_PATH'], relative_dir)
		if not os.path.exists(absolute_dir):
			os.makedirs(absolute_dir)
		absolute_path = os.path.join(absolute_dir, photo_filename)
		if not os.path.exists(absolute_path):
			photo.save(absolute_path)
		return photo_filename

	def update_user_files(self, user, files):
		"""
		Uploads user avatar and 4 photos.
		In database relative path is stored.
		"""
		if not files:
			return None
		relative_dir = os.path.join(app.config['UPLOAD_FOLDER'], user['login'])
		avatar_filename = self.upload_photo(relative_dir, files['avatar'])
		if avatar_filename is not None:
			relative_path = os.path.join('/', relative_dir, avatar_filename)
			self.db.query('UPDATE users SET avatar = %s WHERE id = %s', (relative_path, user['id']))
		photos = files.getlist('photos[]')
		photo_filenames = [photo for photo in user['photos']]
		for i, photo in enumerate(photos):
			if photo:
				photo_filename = self.upload_photo(relative_dir, photo)
				relative_path = os.path.join('/', relative_dir, photo_filename)
				photo_filenames[i] = relative_path
		if photo_filenames != user['photos']:
			self.db.query('UPDATE users SET photos = %s WHERE id = %s', (json.dumps(photo_filenames), user['id']))

	@classmethod
	def get_changed_values(cls, prev_val, new_val):
		"""Checks which values were updated"""
		ignored = ('tags', 'csrf_token')
		values = [val for key, val in new_val.items() if key not in ignored and str(prev_val[key]) != val]
		sql = ', '.join(f"{key} = %s" for key, val in new_val.items()
						if key not in ignored and str(prev_val[key]) != val)
		need_confirmation = prev_val['email'] != new_val['email']
		if need_confirmation:
			sql += ", confirmed='0'"
		return sql, values, need_confirmation

	def change(self, form, files=None):
		user = self.get_user_info(session['user'])
		sql, values, need_confirmation = self.get_changed_values(user, form)
		if need_confirmation and self.check_email_existent(form["email"]):
			raise ValueError("User with his E-mail already exists")
		if len(values) > 0:
			sql = f"UPDATE `users` SET {sql} WHERE id=%s"
			values.append(user['id'])
			self.db.query(sql, values)
		self.update_user_tags(user, form.getlist('tags'))
		self.update_user_files(user, files)
		if need_confirmation:
			self.email_confirmation(form["email"], user['login'], user["token"])
			flash("You will have to confirm your new E-mail!", 'success')

	def get_liked_users(self, user_id):
		sql = "SELECT liked_user FROM `likes` WHERE like_owner=%s"
		response = self.db.get_all_rows(sql, (user_id,), cursorclass=MySQLdb.cursors.Cursor)
		return [liked_user for liked_user, in response]

	def get_blocked_users(self, user_id):
		sql = "SELECT blocked_id FROM `blocked` WHERE user_id=%s"
		response = self.db.get_all_rows(sql, (user_id,), cursorclass=MySQLdb.cursors.Cursor)
		return [blocked_user for blocked_user, in response]

	def get_reported_users(self, user_id):
		sql = "SELECT reported_id FROM `reports` WHERE user_id = %s"
		response = self.db.get_all_rows(sql, (user_id,), cursorclass=MySQLdb.cursors.Cursor)
		return [reported_user for reported_user, in response]

	def get_visited_users(self, user_id):
		sql = "SELECT visited FROM `visits` WHERE visitor = %s"
		response = self.db.get_all_rows(sql, (user_id,), cursorclass=MySQLdb.cursors.Cursor)
		return [visited for visited, in response]

	def like_user(self, like_owner, like_to, unlike):
		if unlike:
			sql = "DELETE FROM `likes` WHERE like_owner = %s AND liked_user = %s"
			action = 'unlike'
		else:
			sql = "SELECT COUNT(id) as row_num FROM `likes` WHERE like_owner = %s AND liked_user = %s"
			if self.db.get_row(sql, (like_to, like_owner))['row_num'] > 0:
				action = 'like_back'
			else:
				action = 'like'
			sql = "INSERT INTO `likes` SET like_owner = %s, liked_user = %s"
		self.db.query(sql, (like_owner, like_to))
		return action

	def block_user(self, user_id, blocked_id):
		sql = "INSERT INTO `blocked` SET user_id = %s, blocked_id = %s"
		self.db.query(sql, (user_id, blocked_id))
		sql = "DELETE FROM `likes` WHERE (like_owner = %s AND liked_user = %s) OR (like_owner = %s AND liked_user = %s)"
		self.db.query(sql, (user_id, blocked_id, blocked_id, user_id))

	def report_user(self, user_id, reported_id, unreport):
		if unreport == 'true':
			sql = "DELETE FROM `reports` WHERE user_id=%s AND reported_id=%s"
		else:
			sql = "INSERT INTO `reports` SET user_id=%s, reported_id=%s"
		self.db.query(sql, (user_id, reported_id))

	def visit_user(self, visitor, visited):
		sql = "INSERT INTO `visits` SET visitor = %s, visited = %s"
		self.db.query(sql, (visitor, visited))


class Chat:
	def __init__(self, db):
		self.db = db
		self.timestamp_format = "%c"

	def send_message(self, sender_id, recipient_id, message_text):
		sql = "INSERT INTO `messages` (sender_id, recipient_id, body) VALUES (%s, %s, %s)"
		self.db.query(sql, (sender_id, recipient_id, message_text))

	def get_messages(self, user_id, recipient_id):
		sql = ("SELECT * FROM `messages` WHERE (sender_id=%s AND recipient_id=%s)"
			   "OR (sender_id=%s AND recipient_id=%s) ORDER BY timestamp")
		messages = self.db.get_all_rows(sql, (user_id, recipient_id, recipient_id, user_id))
		for message in messages:
			message['timestamp'] = datetime.strftime(message['timestamp'], self.timestamp_format)
		return messages


class Notification:
	def __init__(self, db):
		self.db = db
		self.timestamp_format = "%c"
		self.notifications = {
			'like': "You have been liked by {}",
			'unlike': "You have been unliked by {}",
			'visit': "Your profile was visited by {}",
			'message': "You received a message from {}",
			'like_back': "You have been liked back by {}"
		}

	def send(self, recipient, notif_type, executive_user):
		links = {
			'user_action': url_for('profile', user_id=executive_user['id']),
			'message': url_for('chat_page', recipient_id=executive_user['id'])
		}
		if executive_user['id'] not in recipient['blocked_users']:
			sql = "INSERT INTO `notifications` (user_id, message, link) VALUES (%s, %s, %s)"
			link = 'message' if notif_type == 'message' else 'user_action'
			message = self.notifications[notif_type].format(executive_user['login'])
			self.db.query(sql, (recipient['id'], message, links[link]))

	def get(self, user_id):
		sql = "SELECT * FROM `notifications` WHERE user_id=%s AND viewed=0 ORDER BY date_created DESC"
		notifications = self.db.get_all_rows(sql, [user_id])
		for notif in notifications:
			notif['date_created'] = datetime.strftime(notif['date_created'], self.timestamp_format)
		return notifications

	def delete(self, notification_id):
		sql = "DELETE FROM `notifications` WHERE id = %s"
		self.db.query(sql, (notification_id,))
