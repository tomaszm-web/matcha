import os


class Config(object):
	# Определяет, включен ли режим отладки
	# В случае если включен, flask будет показывать
	# подробную отладочную информацию. Если выключен -
	# - 500 ошибку без какой либо дополнительной информации.
	DEBUG = False
	# данных, например cookies.
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'ABSOLUTELY SECRET'

	MYSQL_HOST = "remotemysql.com"
	MYSQL_USER = "EbumYmCv3K"
	MYSQL_PASSWORD = "8tdbKY8Vct"
	MYSQL_DB = "EbumYmCv3K"

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
	GOOGLEMAPS_KEY = "AIzaSyD13VWC5CjsfUt9vvPT6ufxjTGAXBOhhjg"

	# PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)


class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
