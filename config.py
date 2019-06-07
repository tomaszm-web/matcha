class Config(object):
	# Определяет, включен ли режим отладки
	# В случае если включен, flask будет показывать
	# подробную отладочную информацию. Если выключен -
	# - 500 ошибку без какой либо дополнительной информации.
	DEBUG = False
	# данных, например cookies.
	SECRET_KEY = 'ABSOLUTELY SECRET'

	DB_HOST = "remotemysql.com"
	DB_USER = "EbumYmCv3K"
	DB_PASSWORD = "8tdbKY8Vct"
	DB_NAME = "EbumYmCv3K"


class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
