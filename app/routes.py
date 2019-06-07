# -*- coding: utf-8 -*-
from flask import (
	Blueprint,
	render_template,
	request,
	url_for,
	session,
	abort,
	current_app
)

import secrets
from app.models import db, Ajax

main_module = Blueprint('main_module', __name__, template_folder='templates')
@main_module.route('/')
@main_module.route('/index')
def index():
	session["csrf_token"] = secrets.token_hex(15)
	return render_template('index.html', csrf_token=session["csrf_token"])


@main_module.route('/registration', methods=["POST"])
def registration():
	ajax = Ajax()
	return ajax.registration(request.form)


@main_module.before_request
def csrf_protect():
	if request.method == "POST":
		token = session['csrf_token']
		if not token or token != request.form.get('csrf_token'):
			abort(403)
