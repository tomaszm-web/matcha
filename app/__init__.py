import os
from secrets import token_hex
from functools import wraps

from flask import Flask, session, redirect, url_for, flash
from flask_socketio import SocketIO
from flask_dotenv import DotEnv

from app.database import Database
from flask_mail import Mail
from config import DevelopmentConfig


class CustomFlask(Flask):
	jinja_options = Flask.jinja_options.copy()
	jinja_options.update(dict(
		variable_start_string='%%',
		variable_end_string='%%'
	))


def csrf_update(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		session['csrf_token'] = token_hex(10)
		app.jinja_env.globals['csrf_token'] = session['csrf_token']
		return func(*args, **kwargs)

	return wrap


def login_required(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		if 'user' not in session:
			flash("You should log in first", 'danger')
			return redirect(url_for('index'))
		else:
			return func(*args, **kwargs)

	return wrap


app = CustomFlask(__name__)
config = DevelopmentConfig()
config.init_app(app)
app.config.from_object(config)
socketio = SocketIO(app)
mail = Mail(app)
db = Database(app)
from app import routes, models, sockets
