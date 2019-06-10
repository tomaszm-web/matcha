# -*- coding: utf-8 -*-
from flask import (
	render_template,
	request,
	url_for,
	session,
	abort,
	flash,
	redirect
)
import secrets
import json
from app import app
from app.models import Account


@app.route('/')
@app.route('/index')
def index():
	session["csrf_token"] = secrets.token_hex(15)
	return render_template('index.html', csrf_token=session["csrf_token"])


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
		session.pop("user", None)
	return redirect(url_for('index'))


@app.route('/confirmation', methods=["GET"])
def confirmation():
	if Account.confirmation(request.args["login"], request.args["token"]):
		flash("Your E-mail was successfully confirmed. You can now log-in")
	else:
		flash("Something went wrong. Try again!")
	return redirect(url_for('index'))


@app.route('/reset', methods=["POST"])
def reset():
	errors = Account.reset(request.form, action=request.form["action"])
	return json.dumps(errors)


@app.before_request
def csrf_protect():
	if request.method == "POST":
		token = session['csrf_token']
		if not token or token != request.form.get('csrf_token'):
			abort(403)
