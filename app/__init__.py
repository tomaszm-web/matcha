import os
from flask import Flask
from app.database import Database
from flask_mail import Mail
from config import DevelopmentConfig
from flask_googlemaps import GoogleMaps, Map
from flaskext.csrf import csrf


class CustomFlask(Flask):
	jinja_options = Flask.jinja_options.copy()
	jinja_options.update(dict(
		variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
		variable_end_string='%%',
	))


app = CustomFlask(__name__)
app.config.from_object(DevelopmentConfig)
GoogleMaps(app)
db = Database(app)
mail = Mail(app)
csrf(app)
from app import routes, models
