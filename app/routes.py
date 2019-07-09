from flask import (
	render_template,
	request,
	url_for,
	session,
	abort,
	flash,
	redirect,
	send_from_directory,
	jsonify)
import requests
from app import app, socketio, Map
from app.models import Account, Chat, Notif
from .database import Database
from .mail import send_email


@app.route('/')
@app.route('/index')
def index():
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
	db = Database(app)
	account = Account(db)
	notif = Notif(db)
	if "user" not in session:
		flash("You should log in to access your profile", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(session["user"])
	return render_template('settings.html', cur_user=user)


@app.route('/profile', methods=["GET"])
def profile():
	db = Database(app)
	account = Account(db)
	notif = Notif(db)
	if "user_id" not in request.args:
		flash("Invalid profile", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(id=request.args["user_id"])
	if 'user' in session:
		cur_user = account.get_user_info(session['user'])
		if user['id'] not in cur_user['checked_users']:
			account.check_user(cur_user['id'], user['id'])
			notif.send_notification(user['id'], 'check_profile', cur_user)
		like_each_other = user['id'] in cur_user['liked_users'] and cur_user['id'] in user['liked_users']
		return render_template('profile.html', cur_user=cur_user, user=user, like_each_other=like_each_other)
	else:
		return render_template('profile.html', user=user)


@app.route('/chat', methods=["GET"])
def chat():
	db = Database(app)
	account = Account(db)
	recipient = account.get_user_info(id=request.args["recipient_id"])
	if not recipient:
		flash("Wrong user id", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(session["user"])
	return render_template('chat.html', cur_user=user, recipient=recipient)


@app.route('/registration', methods=["POST"])
def registration():
	db = Database(app)
	account = Account(db)
	errors = account.registration(request.form)
	return jsonify(errors)


@app.route('/login', methods=["POST"])
def login():
	db = Database(app)
	account = Account(db)
	errors = account.login(request.form)
	return jsonify(errors)


@app.route('/logout')
def logout():
	db = Database(app)
	account = Account(db)
	notif = Notif(db)
	if "user" in session:
		flash("You successfully logged out!", 'success')
		notif.send_notification(38, 'like', account.get_user_info('o4eredko'))
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
	db = Database(app)
	account = Account(db)
	try:
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


@app.route('/filter_users', methods=["GET", "POST"])
def filter_users():
	db = Database(app)
	account = Account(db)
	cur_user = account.get_user_info(session['user']) if 'user' in session else None
	if len(request.form) > 0:
		users = account.get_all_users(cur_user, request.form)
	else:
		users = account.get_all_users(cur_user)
	return render_template('users_list.html', cur_user=cur_user, users=users)


@app.route('/like_user', methods=["GET"])
def like_user():
	db = Database(app)
	account = Account(db)
	notif = Notif(db)
	try:
		action = account.like_user(request.args['like_owner'], request.args['liked_user'], request.args['unlike'])
		if notif:
			notif.send_notification(request.args.get('liked_user'), action,
									account.get_user_info(id=request.args.get('like_owner')))
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unlike': request.args.get('unlike')})


@app.route('/block_user', methods=["GET"])
def block_user():
	db = Database(app)
	account = Account(db)
	try:
		account.block_user(request.args['user_id'], request.args['blocked_id'], request.args['unblock'])
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unblock': request.args.get('unblock')})


# Chat
@socketio.on('chat event')
def send_message(json, methods=['GET', 'POST']):
	try:
		db = Database(app)
		live_chat = Chat(db)
		if 'sender_id' in json and 'recipient_id' in json:
			live_chat.send_message(json['sender_id'], json['recipient_id'], json['body'])
			socketio.emit('chat response', json)
	except Exception:
		return


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
@app.route('/send_notification', methods=["GET"])
def send_notification():
	try:
		db = Database(app)
		notif = Notif(db)
		notif.send_notification(request.args['sender_id'], request.args['message'])
		return jsonify({'success': True})
	except Exception:
		return jsonify({'success': False})


@app.route('/get_notifications', methods=["GET"])
def get_notifications():
	try:
		db = Database(app)
		notif = Notif(db)
		notifications = notif.get_notifications(request.args['user_id'])
		return jsonify({'success': True, 'notifications': notifications})
	except KeyError:
		return jsonify({'success': False})


@socketio.on('disconnect')
def disconnect_user():
	redirect(url_for('logout'))


# Files
@app.route('/uploads/<userdir>/<filename>')
@app.route('/uploads/<filename>')
def uploaded_file(filename, userdir=None):
	if userdir:
		return send_from_directory(f"../{app.config['UPLOAD_FOLDER']}/{userdir}", filename)
	return send_from_directory(f"../{app.config['UPLOAD_FOLDER']}", filename)

# todo Create Gps positioning
