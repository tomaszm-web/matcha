import os
import json
import secrets
import itertools
from datetime import datetime

from pytz import timezone
import MySQLdb.cursors
from flask import render_template, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import app, db
from app.mail import confirm_email_mail, reset_password_mail


def allowed_img_extension(filename):
	filename, file_extension = os.path.splitext(filename)
	return file_extension in ('.png', '.jpg', '.jpeg')


def upload_photo(relative_dir, photo):
	"""
	Save photo in folder from app config.
	:return:filename of new photo
	"""
	if not photo or not allowed_img_extension(photo.filename):
		return None
	photo_filename = secure_filename(photo.filename)
	absolute_dir = os.path.join(app.config['ROOT_PATH'], relative_dir)
	if not os.path.exists(absolute_dir):
		os.makedirs(absolute_dir)
	absolute_path = os.path.join(absolute_dir, photo_filename)
	if not os.path.exists(absolute_path):
		photo.save(absolute_path)
	return photo_filename


class Account:
	fields = ('id', 'login', 'name', 'surname', 'email', 'password', 'token', 'confirmed',
			  'gender', 'preferences', 'biography', 'avatar', 'photos',
			  'age', 'online', 'last_login', 'city')

	def __init__(self, user_id=None, *, extended=True):
		if user_id is None:
			return
		sql = "SELECT * FROM `users` WHERE id = %s"
		user = db.get_row(sql, (user_id,))
		assert user is not None, "No user with this id"
		(self.id, self.login, self.name, self.surname, self.email,
		 self._password, self.token, self._confirmed,
		 self.gender, self.preferences, self.biography,
		 self._avatar, self._photos, self.age, self._online,
		 self.last_login, self.city) = user
		self.fame = self.get_fame_rating(self.id) if extended else None
		self.tags = self.get_tags(self.id) if extended else None

	@classmethod
	def from_email(cls, email):
		user = db.get_row("SELECT id FROM users WHERE email = %s", (email,))
		if user is None:
			return None
		user_id, = user
		return cls(user_id)

	@classmethod
	def from_tuple(cls, src):
		user = cls()
		(user.id, user.login, user.email, user.gender, user.preferences,
		 user.biography, user.age, user.city) = src

	@property
	def confirmed(self):
		return self._confirmed

	@confirmed.setter
	def confirmed(self, value):
		db.query("UPDATE users SET confirmed = %s WHERE id = %s", (value, self.id))
		self._confirmed = value

	@property
	def password(self):
		return self._password

	@password.setter
	def password(self, value):
		db.query("UPDATE users SET password = %s WHERE id = %s", (value, self.id))
		self._password = value

	@property
	def avatar(self):
		return self._avatar

	@avatar.setter
	def avatar(self, value):
		db.query("UPDATE users SET avatar = %s WHERE id = %s", (value, self.id))
		self._avatar = value

	@property
	def photos(self):
		return json.loads(self._photos)

	@photos.setter
	def photos(self, value):
		db.query("UPDATE users SET photos = %s WHERE id = %s", (value, self.id))
		self._photos = value

	@property
	def online(self):
		return self._online

	@online.setter
	def online(self, value):
		if value == 0:
			last_login_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			sql = "UPDATE users SET online = 0, last_login = %s WHERE id = %s"
			db.query(sql, (last_login_date, self.id))
		elif value == 1:
			db.query("UPDATE users SET online = 1 WHERE id = %s", (self.id,))
		else:
			raise ValueError("Online must be equal to 0 or 1")
		self._online = value

	@property
	def liked_users(self):
		sql = "SELECT liked_user FROM `likes` WHERE like_owner=%s"
		response = db.get_all_rows(sql, (self.id,))
		return [liked_user for liked_user, in response]

	@property
	def blocked_users(self):
		sql = "SELECT blocked_id FROM `blocked` WHERE user_id=%s"
		response = db.get_all_rows(sql, (self.id,))
		return [blocked_user for blocked_user, in response]

	@property
	def reported_users(self):
		sql = "SELECT reported_id FROM `reports` WHERE user_id = %s"
		response = db.get_all_rows(sql, (self.id,))
		return [reported_user for reported_user, in response]

	@property
	def visited_users(self):
		sql = "SELECT visited FROM `visits` WHERE visitor = %s"
		response = db.get_all_rows(sql, (self.id,))
		return [visited for visited, in response]

	def info_filled(self):
		return (self.avatar is not None and self.city is not None and self.biography is not None
				and self.gender is not None and self.preferences is not None and self.age is not None)

	@classmethod
	def get_all_users(cls, user_match, filters=None, sort_by=None):
		sql = ("SELECT id FROM `users` "
			   "WHERE NOT (biography is NULL OR age IS NULL OR city IS NULL OR gender IS NULL "
			   "OR preferences IS NULL)")
		if user_match:
			sql, values = cls.filter_by_preferences(sql, user_match)
			users = db.get_all_rows(sql, values)
		else:
			users = db.get_all_rows(sql)

		users = [Account(user, extended=False) for user in users]
		fame_rates = cls.get_fame_rating()
		tags_groups = cls.get_tags()
		for user in users:
			user.fame = fame_rates.get(user.id, 0) if fame_rates else 0
			user.tags = tags_groups.get(user.id) if tags_groups else None
		if filters is not None:
			users = (user for user in users if user.filter_fit(filters))
		# sort_lambda = cls.sort_func(user_match, sort_by)
		# if sort_lambda is not None:
		# 	users = sorted(users, key=sort_lambda)
		return users

	@classmethod
	def register(cls, data):
		login = data['login']
		email = data['email']
		assert not cls.login_exist(login), "User with this login already exists"
		assert not cls.email_exist(email), "User with this E-mail already exists"
		sql = ("INSERT INTO `users` (login, name, surname, email, token, password)"
			   "VALUES (%s, %s, %s, %s, %s, %s)")
		user_token = secrets.token_hex(10)
		db.query(sql, (
			login, data['name'], data['surname'], email, user_token,
			generate_password_hash(data['pass'])))
		confirm_email_mail(email, login, user_token)

	@classmethod
	def login(cls, data):
		sql = "SELECT id, password, confirmed FROM `users` WHERE login = %s"
		response = db.get_row(sql, (data['login'],))
		assert response is not None, "Cannot find user with this login"
		user_id, password, confirmed = response
		assert check_password_hash(password, data['pass']), "Wrong password"
		assert confirmed, "You should confirm your E-mail first!"
		user = cls(user_id)
		user.online = 1
		return user

	@classmethod
	def confirm_email(cls, data):
		email = data['email']
		token = data['token']
		user = cls.from_email(email)
		assert user is not None, "No user with this E-mail"
		assert token == user.token, "Wrong token"
		user.confirmed = 1

	@classmethod
	def reset_password(cls, data):
		action = data['action']
		email = data['email']
		user = cls.from_email(email)
		assert user is not None, "No user with this E-mail"
		if action == "check":
			reset_password_mail(user)
		elif action == "reset":
			assert data['token'] == user.token, "Wrong token!"
			user.password = generate_password_hash(data['pass'])

	def get_changed_values(self, new_val):
		ignored = ('tags', 'csrf_token')
		updated = [(key, val) for key, val in new_val.items()
				   if key not in ignored and str(self.__getattribute__(key)) != val]
		values = [val for _, val in updated]
		sql = ', '.join(f"{key} = %s" for key, _ in updated)
		need_confirmation = self.email != new_val['email']
		return sql, values, need_confirmation

	def change(self, data, files=None):
		sql, values, need_confirmation = self.get_changed_values(data)
		if need_confirmation and self.email_exist(data["email"]):
			raise ValueError("User with his E-mail already exists")
		if len(values) > 0:
			values.append(self.id)
			db.query(f"UPDATE `users` SET {sql} WHERE id = %s", values)
		self.update_user_tags(data.getlist('tags'))
		self.update_user_files(files)
		if need_confirmation:
			self.confirmed = 0
			confirm_email_mail(data['email'], self.login, self.token)
			flash("You will have to confirm your new E-mail!", 'success')

	@staticmethod
	def sort_func(user_match, sort_by=None):
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
				e.city != user_match.city,
				abs(user_match.age - e.age),
				-e.fame,
				-len(set(user_match.tags).intersection(e.tags))
			)
		return None

	def filter_fit(self, filters):
		if not filters:
			return True
		tags = filters.getlist('tags')
		filter1 = not filters['age_from'] or self.age >= int(filters['age_from'])
		filter2 = not filters['age_to'] or self.age <= int(filters['age_to'])
		filter3 = not filters['fame_from'] or self.fame >= int(filters['fame_from'])
		filter4 = not filters['fame_to'] or self.fame <= int(filters['fame_to'])
		filter5 = not len(tags) or len(tags) == len(set(self.tags).intersection(set(tags)))
		filter6 = not filters['city'] or filters['city'] == self.city
		return filter1 and filter2 and filter3 and filter4 and filter5 and filter6

	def update_user_tags(self, new_tags):
		if not new_tags or self.tags == new_tags:
			return None
		all_tags = db.get_all_rows("SELECT * FROM `tags`")
		all_tags = {tag_name for _, tag_name in all_tags}
		sql = ', '.join('%s' for tag_name in new_tags if tag_name not in all_tags)
		new_tags = {new_tags}
		nonexistent_tags = new_tags - all_tags
		if nonexistent_tags:
			sql = f"INSERT INTO `tags` (name) VALUES ({sql})"
			db.query(sql, nonexistent_tags)

	# todo user.tags
	# sql = "DELETE FROM `user_tag` WHERE user_id=%s"
	# db.query(sql, (user['id'],))
	#
	# all_tags = db.get_all_rows("SELECT * FROM `tags`")
	# sql = ', '.join("(%s, %s)" for _ in range(len(new_tags)))
	# user_tag_ids = itertools.chain.from_iterable(
	# 	(user['id'], tag_id) for tag_id, tag_name in all_tags if tag_name in new_tags_set
	# )
	# if len(sql):
	# 	sql = f"INSERT INTO `user_tag` (user_id, tag_id) VALUES {sql}"
	# 	db.query(sql, user_tag_ids)

	def update_user_files(self, files):
		"""
		Uploads user avatar and 4 photos.
		In database relative paths are stored.
		"""
		if not files:
			return None
		relative_dir = os.path.join(app.config['UPLOAD_FOLDER'], self.login)
		avatar_filename = upload_photo(relative_dir, files['avatar'])
		if avatar_filename is not None:
			relative_path = os.path.join('/', relative_dir, avatar_filename)
			self.avatar = relative_path
		user_photos = [photo for photo in self.photos]
		uploaded_photos = files.getlist('photos[]')
		for i, photo in enumerate(uploaded_photos):
			if not photo:
				continue
			photo_filename = upload_photo(relative_dir, photo)
			relative_path = os.path.join('/', relative_dir, photo_filename)
			user_photos[i] = relative_path
		if user_photos != self.photos:
			self.photos = json.dumps(user_photos)

	def like_user(self, liked_user):
		if liked_user.id in self.liked_users:
			action = 'unlike'
			sql = "DELETE FROM `likes` WHERE like_owner = %s AND liked_user = %s"
		else:
			action = 'like_back' if self.id in liked_user.liked_users else 'like'
			sql = "INSERT INTO `likes` SET like_owner = %s, liked_user = %s"
		db.query(sql, (self.id, liked_user.id))
		return action

	def block_user(self, user_id, blocked_id):
		sql = "INSERT INTO `blocked` SET user_id = %s, blocked_id = %s"
		db.query(sql, (user_id, blocked_id))
		sql = ("DELETE FROM `likes` WHERE (like_owner = %s AND liked_user = %s) "
			   "OR (like_owner = %s AND liked_user = %s)")
		db.query(sql, (user_id, blocked_id, blocked_id, user_id))

	def report_user(self, user_id, reported_id, unreport):
		if unreport == 'true':
			sql = "DELETE FROM `reports` WHERE user_id=%s AND reported_id=%s"
		else:
			sql = "INSERT INTO `reports` SET user_id=%s, reported_id=%s"
		db.query(sql, (user_id, reported_id))

	def visit_user(self, visitor, visited):
		sql = "INSERT INTO `visits` SET visitor = %s, visited = %s"
		db.query(sql, (visitor, visited))

	@staticmethod
	def filter_by_preferences(sql, user):
		matches = {}
		if user.preferences == 'heterosexual':
			gender = 'female' if user.gender == 'male' else 'male'
			matches[gender] = 'heterosexual'
		elif user.preferences == 'homosexual':
			matches[user.gender] = 'homosexual'
		else:
			if user.gender == 'male':
				matches['male'] = 'homosexual'
				matches['female'] = 'heterosexual'
			else:
				matches['male'] = 'heterosexual'
				matches['female'] = 'homosexual'
		sql_part = "gender=%s AND (preferences=%s OR preferences='bisexual')"
		sql += " AND ({})".format(' OR '.join(sql_part for _ in range(len(matches))))
		values = itertools.chain.from_iterable(
			(gender, preferences) for gender, preferences in matches.items())
		return sql, values

	@staticmethod
	def login_exist(login):
		sql = "SELECT COUNT(login) as row_num FROM `users` WHERE login = %s"
		row_num, = db.get_row(sql, (login,))
		return row_num > 0

	@staticmethod
	def email_exist(email):
		sql = "SELECT COUNT(email) as row_num FROM `users` WHERE email = %s"
		row_num, = db.get_row(sql, (email,))
		return row_num > 0

	@staticmethod
	def get_fame_rating(user_id=None):
		sql = "SELECT liked_user AS user, COUNT(liked_user) AS like_num FROM `likes` GROUP BY user"
		search_in = db.get_all_rows(sql)
		if not search_in:
			return 0
		max_likes = max(like_num for _, like_num in search_in)
		if user_id:
			user_likes = [like_num for user, like_num in search_in if user == user_id]
			if not user_likes:
				return 0
			return round(user_likes[0] / max_likes * 100)
		return {user_id: round(like_num / max_likes * 100) for user_id, like_num in search_in}

	@staticmethod
	def get_tags(user_id=None):
		if user_id:
			sql = ("SELECT tags.name FROM `tags` INNER JOIN `user_tag` "
				   "ON tags.id = user_tag.tag_id WHERE user_tag.user_id = %s")
			tags = db.get_all_rows(sql, (user_id,))
			if not tags:
				return ()
			return [tag_name for tag_name, in tags]
		else:
			sql = ("SELECT user_tag.user_id, tags.name FROM tags "
				   "INNER JOIN user_tag ON tags.id = user_tag.tag_id")
			tags_groups = db.get_all_rows(sql)
			if not tags_groups:
				return None
			tags_groups = itertools.groupby(tags_groups, lambda pair: pair[0])
			return {user: list(tag for _, tag in group) for user, group in tags_groups}


class Chat:
	timestamp_format = "%H:%M %d %b %Y"
	tz = timezone('Europe/Amsterdam')

	def __init__(self, user1_id, user2_id):
		self.user1_id = user1_id
		self.user2_id = user2_id

		select_sql = "SELECT id FROM chats WHERE user1_id = %s AND user2_id = %s"
		user_pair = (user1_id, user2_id)
		response = db.get_row(select_sql, user_pair) \
				   or db.get_row(select_sql, reversed(user_pair))
		if response is None:
			insert_sql = "INSERT INTO chats (user1_id, user2_id) VALUE (%s, %s)"
			db.query(insert_sql, user_pair)
			response = db.get_row(select_sql, user_pair)
		self.id, = response

	def get_messages(self):
		sql = "SELECT * FROM `messages` WHERE chat_id = %s ORDER BY timestamp"
		messages = db.get_all_rows(sql, (self.id,), cursorclass=MySQLdb.cursors.DictCursor)
		for message in messages:
			message['timestamp'] = self.tz.localize(message['timestamp'])
			message['timestamp'] = datetime.strftime(message['timestamp'], self.timestamp_format)
		return messages

	@classmethod
	def send_message(cls, chat_id, sender_id, recipient_id, message_text):
		sql = "INSERT INTO `messages` (chat_id, sender_id, recipient_id, text) VALUES (%s, %s, %s, %s)"
		db.query(sql, (chat_id, sender_id, recipient_id, message_text))

	@classmethod
	def get_chats(cls, user_id):
		sql = ("SELECT chat_id, recipient_id, message, timestamp FROM messages "
			   "INNER JOIN chats ON messages.chat_id = chats.id "
			   "WHERE sender_id = %s OR recipient_id = %s ORDER BY timestamp DESC")
		columns = ('chat_id', 'recipient_id', 'message', 'timestamp')
		chats = db.get_all_rows(sql, (user_id, user_id))
		if not chats:
			return None
		chats = itertools.groupby(chats, lambda row: row[0])
		chats = (dict(zip(columns, message)) for _, (message, *_) in chats)
		return chats

# class Notification:
# 	def __init__(self, db):
# 		db = db
# 		self.timestamp_format = "%c"
# 		self.notifications = {
# 			'like': "You have been liked by {}",
# 			'unlike': "You have been unliked by {}",
# 			'visit': "Your profile was visited by {}",
# 			'message': "You received a message from {}",
# 			'like_back': "You have been liked back by {}"
# 		}
#
# 	def send(self, recipient, notif_type, executive_user):
# 		links = {
# 			'user_action': url_for('profile', user_id=executive_user.id),
# 			'message': url_for('chat_page', user_id=executive_user['id'])
# 		}
# 		if executive_user['id'] not in recipient['blocked_users']:
# 			sql = "INSERT INTO `notifications` (user_id, message, link) VALUES (%s, %s, %s)"
# 			link = 'message' if notif_type == 'message' else 'user_action'
# 			message = self.notifications[notif_type].format(executive_user['login'])
# 			db.query(sql, (recipient['id'], message, links[link]))
#
# 	def get(self, user_id):
# 		sql = "SELECT * FROM `notifications` WHERE user_id=%s AND viewed=0 ORDER BY date_created DESC"
# 		notifications = db.get_all_rows(sql, (user_id,), cursorclass=MySQLdb.cursors.DictCursor)
# 		for notif in notifications:
# 			notif['date_created'] = datetime.strftime(notif['date_created'], self.timestamp_format)
# 		return notifications
#
# 	def delete(self, notification_id):
# 		sql = "DELETE FROM `notifications` WHERE id = %s"
# 		db.query(sql, (notification_id,))
