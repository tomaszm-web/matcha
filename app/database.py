import MySQLdb
import MySQLdb.cursors


class Database:
	def __init__(self, app):
		self.con = MySQLdb.connect(host=app.config["DB_HOST"], user=app.config["DB_USER"],
								   passwd=app.config["DB_PASSWORD"], db=app.config["DB_NAME"],
								   cursorclass=MySQLdb.cursors.DictCursor)
		self.cur = None

	def query(self, sql, values=None):
		self.cur.execute(sql, values)
		if sql[:5] != "SELECT":
			self.con.commit()

	def exec_query(self, sql, values):
		self.cur = self.con.cursor()
		self.query(sql, values)
		self.cur.close()

	def get_row(self, sql, values=None):
		self.cur = self.con.cursor()
		self.query(sql, values)
		res = self.cur.fetchone()
		self.cur.close()
		return res

	def get_all_rows(self, sql, values=None):
		self.cur = self.con.cursor()
		self.query(sql, values)
		res = self.cur.fetchall()
		self.cur.close()
		return res

	def get_row_num(self, sql, values=None):
		self.cur = self.con.cursor()
		self.query(sql, values)
		res = self.cur.rowcount
		self.cur.close()
		return res

	def create_tables(self):
		return self.con
