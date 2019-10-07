import os


class Config(object):
	# Определяет, включен ли режим отладки
	# В случае если включен, flask будет показывать
	# подробную отладочную информацию. Если выключен -
	# - 500 ошибку без какой либо дополнительной информации.
	DEBUG = False
	# данных, например cookies.
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'ABSOLUTELY SECRET'

	MYSQL_HOST = os.environ.get('MYSQL_HOST')
	MYSQL_USER = os.environ.get('MYSQL_USER')
	MYSQL_DB = os.environ.get('MYSQL_DB')
	MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

	# Email sender configuration
	MAIL_SERVER = "smtp.googlemail.com"
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	# In google account settings allow access for unauthorized apps
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	# administrator list
	ADMINS = ["evgeny.ocheredko@gmail.com"]

	# Upload folder
	UPLOAD_FOLDER = "uploads"

	# Google Maps Key
	GOOGLEMAPS_KEY = "AIzaSyALTJ_4VStfdn39CkEBeyybal3FaxANm60"

	# PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)


class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
