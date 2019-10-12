import os
import requests
from flask import (
	render_template, request, url_for, session,
	flash, redirect, send_from_directory,
	jsonify, abort, make_response
)
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
		if not account.check_user_info(cur_user):
			flash('Please, fill in information about yourself', 'info')
			return redirect(url_for('settings'))
	else:
		cur_user = None
	return render_template('index.html', cur_user=cur_user)


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
			flash(f'{type(e).__name__}: {str(e)}', 'danger')
		else:
			flash("Your profile's info was successfully updated", 'success')
		return redirect(request.url)
	user = account.get_user_info(session["user"])
	return render_template('settings.html', cur_user=user)


@app.route('/profile/<int:user_id>')
@csrf_update
def profile(user_id):
	user = account.get_user_info(user_id)
	if not user:
		flash('No user with that id!', 'danger')
		return redirect(url_for('index'))
	if 'user' not in session:
		return render_template('profile.html', user=user)
	cur_user = account.get_user_info(session['user'])
	if not account.check_user_info(cur_user):
		flash('Please, fill in information about yourself', 'info')
		return redirect(url_for('settings'))
	if user_id in cur_user['blocked_users']:
		flash("This user was blocked by yourself. If you want to delete him from black list,"
			  "donate me 10$ for future development of this feature!", 'info')
		return redirect(url_for('index'))
	if user['id'] != cur_user['id'] and user['id'] not in cur_user['visited']:
		account.visit_user(cur_user['id'], user['id'])
		notification.send(user['id'], 'visit', cur_user)
	return render_template('profile.html', cur_user=cur_user, user=user)


@app.route('/chat/<int:recipient_id>')
@csrf_update
@login_required
def chat_page(recipient_id):
	recipient = account.get_user_info(recipient_id)
	if not recipient:
		flash('No user with that id!', 'danger')
		return redirect(url_for('index'))
	if not recipient:
		flash("Wrong user id", 'danger')
		return redirect(url_for('index'))
	user = account.get_user_info(session["user"])
	if not account.check_user_info(user):
		flash('Please, fill in information about yourself', 'info')
		return redirect(url_for('settings'))
	if recipient['id'] not in user['liked_users'] or user['id'] not in recipient['liked_users']:
		flash("You should like each other before chatting", 'danger')
		return redirect(url_for('profile', user_id=recipient['id']))
	return render_template('chat.html', cur_user=user, recipient=recipient)


@app.route('/chat-list')
@csrf_update
@login_required
def chat_list():
	cur_user = account.get_user_info(session['user'])
	return render_template('chat-list.html', cur_user=cur_user)


@app.route('/registration', methods=["POST"])
def registration():
	try:
		account.registration(request.form)
	except KeyError:
		res = jsonify({'success': False, 'error': "You haven't set some values"})
	except Exception as e:
		res = jsonify({'success': False, 'error': str(e)})
	else:
		res = jsonify({'success': True})
	return res


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
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True, 'address': response.json()})


@app.route('/filter_users', methods=["GET", "POST"])
def filter_users():
	try:
		cur_user = account.get_user_info(session['user']) if 'user' in session else None
		if len(request.form) > 0:
			users = account.get_all_users(cur_user, filters=request.form, sort_by=request.form.get('sort_by'))
			if request.form.get('reversed') == 'on':
				users = reversed(users)
		else:
			users = account.get_all_users(cur_user)
		return render_template('user_list.html', cur_user=cur_user, users=users)
	except Exception:
		return "Something went wrong!"


@app.route('/ajax/like_user', methods=["POST"])
def like_user_ajax():
	req = request.get_json() if request.is_json else request.form
	try:
		like_owner = session['user']
		recipient = req['liked_user']
		unlike = int(req['unlike'])
		action = account.like_user(like_owner, recipient, unlike)
		notification.send(recipient, action, account.get_user_info(like_owner, extended=False))
	except KeyError:
		return jsonify({'success': False, 'error': 'KeyError'})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True, 'unlike': bool(unlike)})


@app.route('/like_user/<int:user_id>/', methods=["POST"])
def like_user(user_id):
	try:
		like_owner = session['user']
		action = account.like_user(like_owner, user_id, int(request.form['unlike']))
		if action == 'like':
			msg = "Your liked was received. If you get liked back, you'll be able to chat"
		elif action == 'like_back':
			msg = "Great! You can chat now."
		else:
			msg = "You successfully disconnected from that user."
		flash(msg, 'success')
		notification.send(user_id, action, account.get_user_info(like_owner, extended=False))
	except Exception:
		flash("Something went wrong. Try again a bit later!", 'danger')
	return redirect(url_for('profile', user_id=user_id))


@app.route('/block_user/<int:user_id>', methods=["POST"])
def block_user(user_id):
	try:
		account.block_user(session['user'], user_id)
	except Exception as e:
		flash("Error" + str(e), 'danger')
	else:
		flash("This user was permanently banned. He won't appear anymore in your search", 'info')
	return redirect(url_for('index'))


@app.route('/report_user', methods=["POST"])
def report_user():
	req = request.get_json() if request.is_json else request.form
	try:
		account.report_user(req['user_id'], req['reported_id'], req['unreport'])
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True, 'unreport': req['unreport']})


@app.route('/ajax/get_messages', methods=["POST"])
def get_messages():
	req = request.get_json()
	try:
		messages = chat.get_messages(req['sender_id'], req['recipient_id'])
		return jsonify({'success': True, 'messages': messages})
	except KeyError:
		return jsonify({'success': False, 'error': 'KeyError'})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})


@app.route('/ajax/get_tag_list', methods=["GET"])
def get_tag_list():
	res = db.get_all_rows("SELECT name as id, name AS text FROM tags")
	return jsonify({'success': True, 'tags': res})


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
		req = request.get_json() if request.is_json else request.form
		if req.get('csrf_token') != session.get('csrf_token'):
			return abort(403)


@app.route('/uploads/<path:path>')
def uploaded_file(path):
	dirpath = os.path.join(app.config['UPLOAD_PATH'], app.config['UPLOAD_FOLDER'])
	return send_from_directory(dirpath, path)
