import os
import requests

import MySQLdb
from flask import (
	render_template, request, url_for, session,
	flash, redirect, send_from_directory,
	jsonify, abort, make_response
)

from app.models import Account, Chat, Notification
from app import app, db, csrf_update, login_required


@app.route('/')
@app.route('/index')
@csrf_update
def index():
	if 'user' in session:
		user = Account(session['user'])
		if not user:
			flash('Please, fill in information about yourself', 'info')
			return redirect(url_for('settings'))
	else:
		user = None
	return render_template('index.html', cur_user=user)


@app.route('/settings', methods=["GET", "POST"])
@csrf_update
@login_required
def settings():
	user = Account(session['user'])
	if request.method == "POST":
		try:
			user.change(request.form, request.files)
		except KeyError:
			flash("You haven't set some values!", 'danger')
		except Exception as e:
			flash(f"{type(e).__name__}: {str(e)}", 'danger')
		else:
			flash("Your profile's info was successfully updated", 'success')
		return redirect(request.url)
	return render_template('settings.html', cur_user=user)


@app.route('/profile/<int:user_id>')
@csrf_update
def profile(user_id):
	user = Account(user_id)
	if not user:
		flash('No user with this id!', 'danger')
		return redirect(url_for('index'))
	if 'user' not in session:
		return render_template('profile.html', cur_user=None, user=user)

	cur_user = Account(session['user'])
	if not cur_user:
		flash('Please, fill in information about yourself', 'info')
		return redirect(url_for('settings'))
	if user == cur_user:
		return render_template('profile.html', cur_user=user, user=user)

	if user_id in cur_user.blocked:
		flash("This user was blocked by yourself. If you want to delete him from black list,"
			  "donate me 10$ for future development of this feature!", 'info')
		return redirect(url_for('index'))
	if user.id not in cur_user.visited:
		cur_user.visited = user
	return render_template('profile.html', cur_user=cur_user, user=user)


@app.route('/chat/<int:user_id>')
@csrf_update
@login_required
def chat_page(user_id):
	recipient = Account(user_id)
	if not recipient:
		flash('No user with this id!', 'danger')
		return redirect(url_for('index'))

	cur_user = Account(session["user"])
	if not cur_user:
		flash('Please, fill in information about yourself', 'info')
		return redirect(url_for('settings'))
	if user_id not in cur_user.liked or cur_user.id not in recipient.liked:
		flash("You should like each other before chatting", 'danger')
		return redirect(url_for('profile', user_id=recipient.id))

	chat = Chat(cur_user.id, recipient.id)
	return render_template('chat.html', cur_user=cur_user, user=recipient, chat=chat)


@app.route('/chat-list')
@csrf_update
@login_required
def chat_list():
	user = Account(session['user'])
	if not user:
		flash('Please, fill in information about yourself', 'info')
		return redirect(url_for('settings'))
	chats = Chat.get_chats(session['user'])
	print(chats)
	return render_template('chat-list.html', cur_user=cur_user, chats=chats)


@app.route('/register', methods=["POST"])
def registration():
	try:
		Account.register(request.form)
	except KeyError:
		res = jsonify({'success': False, 'error': "You haven't set some values"})
	except AssertionError as e:
		res = jsonify({'success': False, 'error': str(e)})
	else:
		res = jsonify({'success': True})
	return res


@app.route('/login', methods=["POST"])
def login():
	try:
		session['user'] = Account.login(request.form).id
	except KeyError:
		res = jsonify({'success': False, 'error': "You haven't set some values"})
	except AssertionError as e:
		res = jsonify({'success': False, 'error': str(e)})
	else:
		res = jsonify({'success': True})
		flash("You successfully logged in!", 'success')
	return res


@app.route('/logout')
@login_required
def logout():
	user = Account(session.pop('user'))
	user.online = 0
	flash("You successfully logged out!", 'success')
	return redirect(url_for('index'))


@app.route('/confirm_email', methods=["GET"])
def confirm_email():
	try:
		Account.confirm_email(request.args)
	except AssertionError as e:
		flash(str(e), 'danger')
	else:
		flash("Your E-mail was successfully confirmed!", 'success')
	return redirect(url_for('index'))


@app.route('/reset_password', methods=["POST"])
def reset_password():
	try:
		Account.reset_password(request.form)
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	else:
		flash("You successfully updated your password!", 'success')
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
	# try:
	cur_user = Account(session['user']) if 'user' in session else None
	if len(request.form) > 0:
		users = Account.get_all_users(cur_user, filters=request.form,
									  sort_by=request.form.get('sort_by'))
		if request.form.get('reversed') == 'on':
			users = reversed(users)
	else:
		users = Account.get_all_users(cur_user)
	return render_template('user_list.html', cur_user=cur_user, users=users)
	# except Exception as e:
	# 	return "Something went wrong! " + str(e)


@app.route('/ajax/like_user', methods=["POST"])
def like_user_ajax():
	req = request.get_json() if request.is_json else request.form
	try:
		user = Account(session['user'])
		recipient = Account(req['liked_user'])
		action = user.like_user(recipient)
		Notification.send(user, recipient, action)
	except KeyError:
		return jsonify({'success': False, 'error': 'KeyError'})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True, 'unlike': bool(action == 'unlike')})


@app.route('/like_user/<int:user_id>/', methods=["POST"])
def like_user(user_id):
	try:
		user = Account(session['user'])
		recipient = Account(user_id)
		action = user.like_user(recipient)
		if action == 'like':
			msg = "Your liked was received. If you get liked back, you'll be able to chat"
		elif action == 'like_back':
			msg = "Great! You can chat now."
		else:
			msg = "You successfully disconnected from that user."
		flash(msg, 'success')
		Notification.send(user, recipient, action)
	except Exception as e:
		flash(str(e), 'danger')
	return redirect(url_for('profile', user_id=user_id))


@app.route('/block_user/<int:user_id>', methods=["POST"])
def block_user(user_id):
	try:
		user = Account(session['user'])
		user.blocked = user_id
	except AssertionError as e:
		flash(str(e))
	except Exception as e:
		flash("Error" + str(e), 'danger')
	else:
		flash("This user was permanently banned. He won't appear anymore in your search", 'info')
	return redirect(url_for('index'))


@app.route('/report_user', methods=["POST"])
def report_user():
	req = request.get_json() if request.is_json else request.form
	try:
		user = Account(session['user'])
		user.reported = req['reported_id']
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})
	return jsonify({'success': True})


@app.route('/ajax/get_tag_list', methods=["GET"])
def get_tag_list():
	res = db.get_all_rows("SELECT name as id, name AS text FROM tags",
						  cur_class=MySQLdb.cursors.DictCursor)
	return jsonify({'success': True, 'tags': res})


@app.route('/get_notifications', methods=["GET"])
def get_notifications():
	try:
		notifications = Notification.get_notifications(session['user'])
		res = make_response(jsonify(notifications), 200)
	except Exception as e:
		res = make_response(jsonify({'error': str(e)}), 404)
	return res


@app.route('/del_notification/<int:notification_id>', methods=["DELETE"])
def del_notification(notification_id):
	try:
		notification = Notification(notification_id)
		notification.delete()
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
	dirpath = os.path.join(app.config['ROOT_PATH'], app.config['UPLOAD_FOLDER'])
	return send_from_directory(dirpath, path)
