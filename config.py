import os


class Config(object):
	# Определяет, включен ли режим отладки
	# В случае если включен, flask будет показывать
	# подробную отладочную информацию. Если выключен -
	# - 500 ошибку без какой либо дополнительной информации.
	DEBUG = False
	# данных, например cookies.
	print(os.getenv('MYSQL_HOST'))
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'ABSOLUTELY SECRET'
	ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

	MYSQL_HOST = os.environ.get('MYSQL_HOST')
	MYSQL_USER = os.environ.get('MYSQL_USER')
	MYSQL_DB = os.environ.get('MYSQL_DB')
	MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
	MYSQL_SCHEMA = os.path.join(ROOT_PATH, 'matcha.sql')

	# Email sender configuration
	MAIL_SERVER = "smtp.googlemail.com"
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	# In google account settings allow access for unauthorized apps
	MAIL_USERNAME = os.environ.get('GMAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')

	# administrator
	ADMIN = os.environ.get('GMAIL_USERNAME')

	# Upload folder
	UPLOAD_FOLDER = "uploads"

	# PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)


class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
