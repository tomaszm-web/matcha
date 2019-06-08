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
from app.models import Ajax


@app.route('/')
@app.route('/index')
def index():
	session["csrf_token"] = secrets.token_hex(15)
	return render_template('index.html', csrf_token=session["csrf_token"])


@app.route('/registration', methods=["POST"])
def registration():
	ajax = Ajax()
	errors = ajax.registration(request.form)
	if len(errors) == 0:
		flash("Registration is almost done! You should confirm your E-mail.")
	return json.dumps(errors)


@app.route('/confirm', methods=["GET"])
def confirmation():
	ajax = Ajax()
	redirect(url_for('index'))
	if ajax.confirmation(request.args["login"], request.args["token"]):
		flash("Your E-mail was successfully confirmed. You can now log-in")
	else:
		flash("Something went wrong. Try again!")

@app.before_request
def csrf_protect():
	if request.method == "POST":
		token = session['csrf_token']
		if not token or token != request.form.get('csrf_token'):
			abort(403)
