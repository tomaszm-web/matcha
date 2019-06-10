import os
from flask import Flask
from app.database import Database
from flask_mail import Mail
from config import DevelopmentConfig


class CustomFlask(Flask):
	jinja_options = Flask.jinja_options.copy()
	jinja_options.update(dict(
		variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
		variable_end_string='%%',
	))


app = CustomFlask(__name__)
app.config.from_object(DevelopmentConfig)
db = Database(app)
mail = Mail(app)
from app import routes, models
