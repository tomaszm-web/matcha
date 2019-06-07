import os
from flask import Flask
from .database import db


class CustomFlask(Flask):
	jinja_options = Flask.jinja_options.copy()
	jinja_options.update(dict(
		variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
		variable_end_string='%%',
	))


def create_app():
	app = CustomFlask(__name__)
	app.config.from_object(os.environ['APP_SETTINGS'])
	db.init_app(app)
	import app.routes as routes
	app.register_blueprint(routes.main_module)
	return app
