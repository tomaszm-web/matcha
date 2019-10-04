import os


class Config(object):
	# Определяет, включен ли режим отладки
	# В случае если включен, flask будет показывать
	# подробную отладочную информацию. Если выключен -
	# - 500 ошибку без какой либо дополнительной информации.
	DEBUG = False
	# данных, например cookies.
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'ABSOLUTELY SECRET'

	DB_HOST = "remotemysql.com"
	DB_USER = "EbumYmCv3K"
	DB_PASSWORD = "8tdbKY8Vct"
	DB_NAME = "EbumYmCv3K"

	# Email sender configuration
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = os.environ.get('MAIL_PORT')
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	# administrator list
	ADMINS = ["evgeny.ocheredko@gmail.com"]

	# Upload folder
	UPLOAD_FOLDER = "uploads"

	# Google Maps Key
	GOOGLEMAPS_KEY = "AIzaSyAjzkW8XWRsKcQhs7hcY-Rc7wPSSSIQVQM"

	# PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)


class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
