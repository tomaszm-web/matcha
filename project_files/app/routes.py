import os

from flask import (
	render_template,
	request,
	url_for,
	session,
	flash,
	redirect,
	send_from_directory,
	jsonify, abort, make_response)
import requests
from app.models import Account, Chat, Notification
from app import app, db, csrf_update, login_required

account = Account(db)
chat = Chat(db)
notification = Notification(db)


@app.route('/')
@app.route('/index')
@csrf_update
def index():
	if 'user' in session:
		cur_user = account.get_user_info(session["user"])
	else:
		cur_user = None
	users = account.get_all_users(user_match=cur_user)
	return render_template('index.html', users=users, cur_user=cur_user)


@app.route('/settings', methods=["GET", "POST"])
@csrf_update
@login_required
def settings():
	if request.method == "POST":
		try:
			account.change(request.form, request.files)
		except KeyError:
			flash("You haven't set some values!", 'danger')
		except Exception as e:
			flash(str(e), 'danger')
		else:
			flash("Your profile's info was successfully updated", 'success')
		return redirect(request.url)
	user = account.get_user_info(session["user"])
	return render_template('settings.html', cur_user=user)


@app.route('/profile/<int:profile_id>')
@csrf_update
def profile(profile_id):
	user = account.get_user_info(user_id=profile_id)
	if 'user' not in session:
		return render_template('profile.html', user=user)
	cur_user = account.get_user_info(session['user'])
	if user['id'] not in cur_user['checked_users'] and user['id'] != cur_user['id']:
		account.check_user(cur_user['id'], user['id'])
		notification.send(user['id'], 'check_profile', cur_user)
	return render_template('profile.html', cur_user=cur_user, user=user)


@app.route('/chat', methods=["GET"])
@csrf_update
@login_required
def chat_page():
	recipient = account.get_user_info(user_id=request.args["recipient_id"])
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
		account.login(request.form)
	except KeyError:
		error = "You haven't set some values"
		return make_response(jsonify({'success': False, 'error': error}), 203)
	except ValueError as e:
		error = str(e)
		return make_response(jsonify({'success': False, 'error': error}), 203)
	else:
		flash("You successfully logged in!", 'success')
	return make_response(jsonify({'success': True}), 202)


@app.route('/logout')
@login_required
def logout():
	flash("You successfully logged out!", 'success')
	sql = "UPDATE `users` SET online=0 WHERE id=%s"
	db.query(sql, [session['user']])
	session.pop("user", None)
	return redirect(url_for('index'))


@app.route('/confirmation', methods=["GET"])
def confirmation():
	if account.confirmation(request.args.get("login"), request.args.get("token")):
		flash("Your E-mail was successfully confirmed!", 'success')
	else:
		flash("Something went wrong. Try again!", 'danger')
	return redirect(url_for('index'))


@app.route('/reset', methods=["POST"])
def reset():
	try:
		account.reset(request.form, action=request.form["action"])
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True})


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
		cur_user = account.get_user_info(session['user']) if 'user' in session else None
		if len(request.form) > 0:
			users = account.get_all_users(cur_user, request.form)
		else:
			users = account.get_all_users(cur_user)
		return render_template('users_list.html', cur_user=cur_user, users=users)
	except Exception:
		return "Something went wrong!"


@app.route('/ajax/like_user', methods=["POST"])
def like_user_ajax():
	try:
		executioner = session['user']
		recipient = request.form['liked_user']
		unlike = request.form['unlike']
		action = account.like_user(executioner, recipient, unlike)
		notification.send(recipient, action, account.get_user_info(executioner, extended=False))
	except KeyError:
		return jsonify({'success': False, 'error': 'KeyError'})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True, 'unlike': unlike})


@app.route('/like_user', methods=["POST"])
def like_user():
	try:
		recipient = request.form.get('liked_user')
		executioner = session['user']
		action = account.like_user(executioner, recipient, request.form.get('unlike'))
		notification.send(recipient, action, account.get_user_info(executioner, extended=False))
	except Exception:
		flash("Something went wrong. Try again a bit later!", 'danger')
	return redirect(url_for('profile', user_id=request.form.get('liked_user')))


@app.route('/block_user', methods=["GET"])
def block_user():
	try:
		account.block_user(request.args['user_id'], request.args['blocked_id'], request.args['unblock'])
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unblock': request.args.get('unblock')})


@app.route('/report_user', methods=["GET"])
def report_user():
	try:
		account.report_user(request.args['user_id'], request.args['reported_id'], request.args['unreport'])
	except Exception as e:
		return jsonify({'success': False, 'error_message': str(e)})
	return jsonify({'success': True, 'unreport': request.args.get('unreport')})


# Chat
@app.route('/get_messages', methods=["GET", "POST"])
def get_messages():
	try:
		messages = chat.get_messages(request.args['sender_id'], request.args['recipient_id'])
		return jsonify({'success': True, 'messages': messages})
	except Exception as e:
		return jsonify({'success': False, 'cause': str(e)})


@app.route('/send_notification', methods=["GET"])
def send_notification():
	try:
		notification.send(request.args['sender_id'], request.args['message'], )
		return jsonify({'success': True})
	except Exception as e:
		return jsonify({'success': False, 'cause': str(e)})


@app.route('/get_notifications', methods=["GET"])
def get_notifications():
	try:
		notifications = notification.get(session['user'])
		res = make_response(jsonify(notifications), 200)
	except Exception as e:
		res = make_response(jsonify({'error': str(e)}), 404)
	return res


@app.route('/del_notification/<int:notification_id>', methods=["DELETE"])
def del_notification(notification_id):
	try:
		notification.delete(notification_id)
		res = make_response('', 204)
	except Exception as e:
		res = make_response(jsonify({'error': str(e)}), 401)
	return res


@app.before_request
def before_request():
	if request.method != "GET":
		json = request.get_json()
		token = session.get('csrf_token')
		csrf_in_json = json is not None and 'csrf_token' in json and token == json['csrf_token']
		if request.form.get('csrf_token') != token and not csrf_in_json:
			return abort(403)


# Files
@app.route('/uploads/<path:path>')
def uploaded_file(path):
	dirpath = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
	return send_from_directory(dirpath, path)


# todo Like after uploading photo
# todo Sort by params
# todo Get requests csrf