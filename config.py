import os

from flask_dotenv import DotEnv


class Config(object):
	DEBUG = False

	SECRET_KEY = os.environ.get('SECRET_KEY') or 'ABSOLUTELY SECRET'
	ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
	MYSQL_SCHEMA = os.path.join(ROOT_PATH, 'mysql/matcha.sql')

	MAIL_SERVER = "smtp.googlemail.com"
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True

	UPLOAD_FOLDER = "uploads"

	@classmethod
	def init_app(cls, app):
		env = DotEnv()
		env.init_app(app, env_file=os.path.join(cls.ROOT_PATH, '.env'))
		env.alias(maps={
			'MAIL_USERNAME': 'ADMIN'
		})


class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
