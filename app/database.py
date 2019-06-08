import pymysql


class Database:
	def __init__(self, app):
		self.con = pymysql.connect(host=app.config["DB_HOST"], user=app.config["DB_USER"], password=app.config["DB_PASSWORD"], db=app.config["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)

	def create_tables(self):
		return self.con

	def query(self, sql, values=None):
		cur = self.con.cursor()
		cur.execute(sql, values)
		self.con.commit()
		return cur
