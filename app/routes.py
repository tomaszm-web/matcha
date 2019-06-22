# -*- coding: utf-8 -*-
from flask import (
	render_template,
	request,
	url_for,
	session,
	abort,
	flash,
	redirect,
	send_from_directory
)
import secrets
import json
from app import app, Map
from app.models import Account


@app.route('/')
@app.route('/index')
def index():
	session["csrf_token"] = secrets.token_hex(15)
	users = Account.get_all_users()
	if "user" in session:
		user = Account.get_user_info(session["user"])
	else:
		user = None
	return render_template('index.html', current_user=user, users=users, csrf_token=session["csrf_token"])


@app.route('/settings')
def settings():
	if "user" not in session:
		flash("You should log in to access your profile", 'danger')
		return redirect(url_for('index'))
	user = Account.get_user_info(session["user"])
	return render_template('settings.html', current_user=user, csrf_token=session["csrf_token"])


@app.route('/profile', methods=["GET"])
def profile():
	if "user_id" not in request.args:
		flash("Invalid profile", 'danger')
		return redirect(url_for('index'))
	user = Account.get_user_info(id=request.args["user_id"])
	return render_template('profile.html', user=user)


@app.route('/registration', methods=["POST"])
def registration():
	errors = Account.registration(request.form)
	return json.dumps(errors)


@app.route('/login', methods=["POST"])
def login():
	errors = Account.login(request.form)
	return json.dumps(errors)


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
	return json.dumps(errors)


@app.route('/change_profile_info', methods=["POST"])
def change():
	selected_tags = request.form.getlist("tags")
	errors = Account.change(request.form, request.files, selected_tags)
	for error in errors:
		flash(error, 'danger')
	if len(errors) == 0:
		flash("Your profile's info was successfully updated", 'success')
	return redirect(url_for('profile'))


@app.route('/like_user', methods=["GET"])
def like_user():
	Account.like_user(session["user"], request.args["liked_user"])
	return "Success"


@app.before_request
def csrf_protect():
	if request.method == "POST":
		token = session['csrf_token']
		if not token or token != request.form.get('csrf_token'):
			abort(403)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory("../" + app.config['UPLOAD_FOLDER'], filename)

# todo Create Gps positioning
# todo Create Fame Rating
