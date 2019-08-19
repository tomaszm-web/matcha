import secrets
from flask import (
	render_template,
	request,
	url_for,
	session,
	flash,
	abort,
	redirect,
	send_from_directory,
	jsonify)
import requests
from app import app, socketio
from flask_socketio import emit
from app.models import Account, Chat, Notif
from .database import Database
from datetime import datetime

users_in_chat = {}


@app.route('/')
@app.route('/index')
def index():
	session['csrf_token'] = secrets.token_hex(10)
	app.jinja_env.globals['csrf_token'] = session['csrf_token']
	db = Database(app)
	account = Account(db)
	notif = Notif(db)
	if 'user' in session:
		cur_user = account.get_user_info(session["user"])
		cur_user['notifications'] = notif.get_notifications(cur_user['id'])
	else:
		cur_user = None
	users = account.get_all_users(user_match=cur_user)
	return render_template('index.html', users=users, cur_user=cur_user)


@app.route('/settings')
def settings():
	session['csrf_token'] = secrets.token_hex(10)
	app.jinja_env.globals['csrf_token'] = session['csrf_token']
	db = Database(app)
	account = Account(db)
	if "user" not in session:
		flash("You should log in to access your profile", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(session["user"])
	return render_template('settings.html', cur_user=user)


@app.route('/profile', methods=["GET"])
def profile():
	session['csrf_token'] = secrets.token_hex(10)
	app.jinja_env.globals['csrf_token'] = session['csrf_token']
	db = Database(app)
	account = Account(db)
	notif = Notif(db)
	if "user_id" not in request.args:
		flash("Invalid profile", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(id=request.args["user_id"])
	if 'user' in session:
		cur_user = account.get_user_info(session['user'])
		if user['id'] not in cur_user['checked_users'] and user['id'] != cur_user['id']:
			account.check_user(cur_user['id'], user['id'])
			notif.send_notification(user['id'], 'check_profile', cur_user)
		return render_template('profile.html', cur_user=cur_user, user=user)
	else:
		return render_template('profile.html', user=user)


@app.route('/chat', methods=["GET"])
def chat():
	if 'user' not in session:
		return redirect(url_for('index'))
	session['csrf_token'] = secrets.token_hex()
	app.jinja_env.globals['csrf_token'] = session['csrf_token']
	db = Database(app)
	account = Account(db)
	recipient = account.get_user_info(id=request.args["recipient_id"])
	if not recipient:
		flash("Wrong user id", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(session["user"])
	if recipient['id'] not in user['liked_users'] or user['id'] not in recipient['liked_users']:
		flash("You should like each other before chatting", 'danger')
		return redirect(url_for('profile', user_id=recipient['id']))
	return render_template('chat.html', cur_user=user, recipient=recipient)


@app.route('/registration', methods=["POST"])
def registration():
	try:
		db = Database(app)
		account = Account(db)
		account.registration(request.form)
	except Exception as e:
		if type(e).__name__ == "KeyError":
			cause = "You haven't set some values"
		else:
			cause = str(e)
		return jsonify({'success': False, 'cause': cause})
	return jsonify({'success': True})


@app.route('/login', methods=["POST"])
def login():
	try:
		db = Database(app)
		account = Account(db)
		account.login(request.form)
	except Exception as e:
		if type(e).__name__ == "KeyError":
			cause = "You haven't set some values"
		else:
			cause = str(e)
		return jsonify({'success': False, 'cause': cause})
	else:
		flash("You successfully logged in!", 'success')
	return jsonify({'success': True})


@app.route('/logout')
def logout():
	db = Database(app)
	if "user" in session:
		flash("You successfully logged out!", 'success')
		sql = "UPDATE `users` SET online=0 WHERE id=%s"
		db.query(sql, [session['user']])
		session.pop("user", None)
	else:
		flash("You should log in first, to be able to log out!", 'danger')
	return redirect(url_for('index'))


@app.route('/confirmation', methods=["GET"])
def confirmation():
	db = Database(app)
	account = Account(db)
	if account.confirmation(request.args.get("login"), request.args.get("token")):
		flash("Your E-mail was successfully confirmed!", 'success')
	else:
		flash("Something went wrong. Try again!", 'danger')
	return redirect(url_for('index'))


@app.route('/reset', methods=["POST"])
def reset():
	try:
		db = Database(app)
		account = Account(db)
		account.reset(request.form, action=request.form["action"])
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True})


@app.route('/change_profile_info', methods=["POST"])
def change():
	try:
		db = Database(app)
		account = Account(db)
		account.change(request.form, request.files)
	except Exception as e:
		if type(e).__name__ == "KeyError":
			flash("You haven't set some values", 'danger')
		else:
			flash(str(e), 'danger')
	else:
		flash("Your profile's info was successfully updated", 'success')
	return redirect(url_for('settings'))


@app.route('/get_user_location_by_ip', methods=["GET"])
def get_user_location_by_ip():
	try:
		ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		response = requests.get("http://api.ipstack.com/" + ip, params={
			'access_key': "57cc3adcb818a96b0af7a4020ec09453"
		})
		response.raise_for_status()
	except Exception as e:
		return jsonify({'success': False, 'cause': str(e)})
	return jsonify({'success': True, 'address': response.json()})


@app.route('/filter_users', methods=["GET", "POST"])
def filter_users():
	try:
		db = Database(app)
		account = Account(db)
		cur_user = account.get_user_info(session['user']) if 'user' in session else None
		if len(request.form) > 0:
			users = account.get_all_users(cur_user, request.form)
		else:
			users = account.get_all_users(cur_user)
		return render_template('users_list.html', cur_user=cur_user, users=users)
	except:
		return "Something went wrong!"

@app.route('/like_user_ajax', methods=["GET"])
def like_user_ajax():
	if 'user' not in session:
		jsonify({'success': False})
	try:
		db = Database(app)
		account = Account(db)
		notif = Notif(db)
		recipient = request.args.get('liked_user')
		executioner = request.args.get('like_owner')
		action = account.like_user(executioner, recipient, request.args['unlike'])
		notif.send_notification(recipient, action, account.get_user_info(executioner, extended=False))
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unlike': request.args.get('unlike')})


@app.route('/like_user', methods=["POST"])
def like_user():
	if 'user' not in session:
		flash("You should log in first", 'danger')
		redirect(url_for('index'))
	try:
		db = Database(app)
		account = Account(db)
		notif = Notif(db)
		recipient = request.form.get('liked_user')
		executioner = session['user']
		action = account.like_user(executioner, recipient, request.form.get('unlike'))
		notif.send_notification(recipient, action, account.get_user_info(executioner, extended=False))
	except Exception as e:
		flash("Something went wrong. Try again a bit later!", 'danger')
	return redirect(url_for('profile', user_id=request.form.get('liked_user')))


@app.route('/block_user', methods=["GET"])
def block_user():
	try:
		db = Database(app)
		account = Account(db)
		account.block_user(request.args['user_id'], request.args['blocked_id'], request.args['unblock'])
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unblock': request.args.get('unblock')})


@app.route('/report_user', methods=["GET"])
def report_user():
	try:
		db = Database(app)
		account = Account(db)
		account.report_user(request.args['user_id'], request.args['reported_id'], request.args['unreport'])
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unreport': request.args.get('unreport')})


# Chat
@app.route('/get_messages', methods=["GET"])
def get_messages():
	try:
		db = Database(app)
		live_chat = Chat(db)
		messages = live_chat.get_messages(request.args['sender_id'], request.args['recipient_id'])
		return jsonify({'success': True, 'messages': messages})
	except Exception as e:
		return jsonify({'success': False, 'cause': str(e)})


# Notifications
# @app.route('/send_notification', methods=["GET"])
# def send_notification():
# 	try:
# 		db = Database(app)
# 		notif = Notif(db)
# 		notif.send_notification(request.args['sender_id'], request.args['message'],)
# 		return jsonify({'success': True})
# 	except Exception:
# 		return jsonify({'success': False})


@app.route('/get_notifications', methods=["GET"])
def get_notifications():
	try:
		db = Database(app)
		notif = Notif(db)
		notifications = notif.get_notifications(request.args['user_id'])
		return jsonify({'success': True, 'notifications': notifications})
	except KeyError:
		return jsonify({'success': False})


@app.route('/del_viewed_notifs', methods=["GET"])
def del_viewed_notifs():
	try:
		db = Database(app)
		notif = Notif(db)
		notif.del_viewed_notifs(request.args.get('viewed_notifs').split(','))
		return jsonify({'success': True})
	except Exception as e:
		return jsonify({'success': False, 'cause': str(e)})


@socketio.on('connect', namespace='/private_chat')
def connect_user_to_chat():
	if 'user' in session:
		users_in_chat[str(session['user'])] = request.sid
		print(users_in_chat)


@socketio.on('private_chat event', namespace='/private_chat')
def send_message(data):
	if 'sender_id' in data and 'recipient_id' in data and 'body' in data:
		db = Database(app)
		live_chat = Chat(db)
		data['timestamp'] = datetime.now().strftime('%c')
		live_chat.send_message(data['sender_id'], data['recipient_id'], data['body'])
		emit('private_chat response', data, room=users_in_chat[data['sender_id']])
		if data['recipient_id'] in users_in_chat:
			emit('private_chat response', data, room=users_in_chat[data['recipient_id']])
		else:
			account = Account(db)
			notif = Notif(db)
			notif.send_notification(data['recipient_id'], 'message', account.get_user_info(data['sender_id']))


@socketio.on('disconnect', namespace='/private_chat')
def disconnect_user_from_chat():
	if 'user' in session:
		users_in_chat.pop(session['user'], None)
		print(users_in_chat)


@socketio.on('connect')
def connect_user():
	if 'user' in session:
		db = Database(app)
		last_login_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql = "UPDATE `users` SET online = 1, last_login = %s WHERE id=%s"
		db.query(sql, [last_login_date, session['user']])


@socketio.on('disconnect')
def disconnect_user():
	if 'user' in session:
		db = Database(app)
		sql = "UPDATE `users` SET online=0 WHERE id=%s"
		db.query(sql, [session['user']])
		session.pop("user", None)


@app.before_request
def before_request():
	if request.method == "POST" and session['csrf_token'] != request.form.get('csrf_token'):
		flash('Csrf attack!', 'danger')
		return redirect(url_for('index'))


# Files
@app.route('/uploads/<userdir>/<filename>')
@app.route('/uploads/<filename>')
def uploaded_file(filename, userdir=None):
	if userdir:
		return send_from_directory(f"../{app.config['UPLOAD_FOLDER']}/{userdir}", filename)
	return send_from_directory(f"../{app.config['UPLOAD_FOLDER']}", filename)

# todo Relative markup, bug with likes
