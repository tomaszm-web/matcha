import MySQLdb
import MySQLdb.cursors


class Database:
	def __init__(self, app):
		self.con = None
		self.app = app
		self.connect()

	def connect(self):
		host = self.app.config['MYSQL_HOST']
		db = self.app.config['MYSQL_DB']
		user = self.app.config['MYSQL_USER']
		password = self.app.config['MYSQL_PASSWORD']
		try:
			self.con = MySQLdb.connect(host=host, db=db, user=user, password=password,
									   cursorclass=MySQLdb.cursors.DictCursor)
		except MySQLdb.OperationalError as e:
			exit(f"MySql Connection Error. Cannot run app.\n{str(e)}")
		except TypeError:
			exit(f"MySQL Connection Error. Some environment variables are wrong!")

	def query(self, sql, values=None, to_close=True):
		try:
			cur = self.con.cursor()
		except MySQLdb.OperationalError:
			self.connect()
			cur = self.con.cursor()
		try:
			cur.execute(sql, values)
			self.con.commit()
			if cur and to_close:
				cur.close()
			return cur
		except Exception:
			self.con.rollback()

	def get_row(self, sql, values=None):
		cur = self.query(sql, values, to_close=False)
		if not cur:
			return None
		res = cur.fetchone()
		cur.close()
		return res

	def get_all_rows(self, sql, values=None):
		cur = self.query(sql, values, to_close=False)
		if not cur:
			return None
		res = cur.fetchall()
		cur.close()
		return res

	def get_row_num(self, sql, values=None):
		cur = self.query(sql, values, to_close=False)
		if not cur:
			return None
		res = cur.rowcount
		cur.close()
		return res
