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
from app import app, Map
from app.models import Account, Chat, Notif


@app.route('/')
@app.route('/index')
def index():
	users = Account.get_all_users()
	if "user" in session:
		user = Account.get_user_info(session["user"])
	else:
		user = None
	return render_template('index.html', cur_user=user, users=users)


@app.route('/settings')
def settings():
	if "user" not in session:
		flash("You should log in to access your profile", 'danger')
		return redirect(url_for('index'))
	user = Account.get_user_info(session["user"])
	return render_template('settings.html', cur_user=user)


@app.route('/profile', methods=["GET"])
def profile():
	if "user_id" not in request.args:
		flash("Invalid profile", 'danger')
		return redirect(url_for('index'))
	user = Account.get_user_info(id=request.args["user_id"])
	if 'user' in session:
		cur_user = Account.get_user_info(session['user'])
		like_each_other = user['id'] in cur_user['liked_users'] and cur_user['id'] in user['liked_users']
		return render_template('profile.html', cur_user=cur_user, user=user, like_each_other=like_each_other)
	else:
		return render_template('profile.html', user=user)


@app.route('/chat', methods=["GET"])
def chat():
	recipient = Account.get_user_info(id=request.args["recipient_id"])
	if not recipient:
		flash("Wrong user id", 'danger')
		return redirect(url_for('index'))
	user = Account.get_user_info(session["user"])
	return render_template('chat.html', cur_user=user, recipient=recipient)


@app.route('/registration', methods=["POST"])
def registration():
	errors = Account.registration(request.form)
	return jsonify(errors)


@app.route('/login', methods=["POST"])
def login():
	errors = Account.login(request.form)
	return jsonify(errors)


@app.route('/logout', methods=["GET"])
def logout():
	if "user" in session:
		flash("You successfully logged out!", 'success')
		session.pop("user", None)
	else:
		flash("You should log in first, to be able to log out!", 'danger')
	return redirect(url_for('index'))


@app.route('/confirmation', methods=["GET"])
def confirmation():
	if Account.confirmation(request.args["login"], request.args["token"]):
		flash("Your E-mail was successfully confirmed!", 'success')
	else:
		flash("Something went wrong. Try again!", 'danger')
	return redirect(url_for('index'))


@app.route('/reset', methods=["POST"])
def reset():
	errors = Account.reset(request.form, action=request.form["action"])
	return jsonify(errors)


@app.route('/change_profile_info', methods=["POST"])
def change():
	try:
		Account.change(request.form, request.files)
	except Exception as e:
		if type(e).__name__ == "KeyError":
			flash("You haven't set some values", 'danger')
		else:
			flash(str(e), 'danger')
	else:
		flash("Your profile's info was successfully updated", 'success')
	return redirect(url_for('settings'))


@app.route('/like_user', methods=["GET"])
def like_user():
	try:
		Account.like_user(request.args['like_owner'], request.args['liked_user'], request.args['unlike'])
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unlike': request.args.get('unlike')})


# Chat
@app.route('/send_message/<recipient_id>', methods=["GET", "POST"])
def send_message(recipient_id):
	if not recipient_id:
		return "Error"
	Chat.send_message(request.form["sender_id"], recipient_id, request.form["text"])
	return "Success"


@app.route('/get_messages', methods=["GET"])
def get_messages():
	if 'sender_id' not in request.args or 'recipient_id' not in request.args:
		return jsonify([])
	messages = Chat.get_messages(request.args['sender_id'], request.args['recipient_id'])
	return jsonify(messages, default=str)


# Notifications
@app.route('/send_notification', methods=["GET"])
def send_notification():
	try:
		Notif.send_notification(request.args['sender_id'], request.args['message'])
		return jsonify({'success': True})
	except KeyError:
		return jsonify({'success': False})


@app.route('/get_notifications', methods=["GET"])
def get_notifications():
	try:
		notifications = Notif.get_notifications(request.args['user_id'])
		return jsonify({'success': True, 'notifications': notifications})
	except KeyError:
		return jsonify({'success': False})


# Files
@app.route('/uploads/<userdir>/<filename>')
@app.route('/uploads/<filename>')
def uploaded_file(filename, userdir=None):
	if userdir:
		return send_from_directory(f"../{app.config['UPLOAD_FOLDER']}/{userdir}", filename)
	return send_from_directory(f"../{app.config['UPLOAD_FOLDER']}", filename)

# todo Create Gps positioning
# todo Create Fame Rating
