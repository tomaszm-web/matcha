import pymysql


class Database:
	def __init__(self, app):
		self.con = pymysql.connect(host=app.config["DB_HOST"], user=app.config["DB_USER"],
								   password=app.config["DB_PASSWORD"], db=app.config["DB_NAME"],
								   cursorclass=pymysql.cursors.DictCursor)
		self.cur = self.con.cursor()

	def create_tables(self):
		return self.con

	def query(self, sql, values=None):
		self.cur.execute(sql, values)
		self.con.commit()
		return self.cur

	def get_row(self, sql, values=None):
		cur = self.query(sql, values)
		return cur.fetchone()

	def get_all_rows(self, sql, values=None):
		cur = self.query(sql, values)
		return cur.fetchall()
