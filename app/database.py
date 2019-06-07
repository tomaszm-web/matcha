import pymysql


class Database:
	def __init__(self):
		self.con = None
		self.cur = None

	def init_app(self, app):
		self.con = pymysql.connect(host=app.config["DB_HOST"], user=app.config["DB_USER"], password=app.config["DB_PASSWORD"], db=app.config["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)
		self.cur = self.con.cursor()

	def create_tables(self):
		return self.cur


db = Database()
