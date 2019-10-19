import MySQLdb
import MySQLdb.cursors


class Database:
	def __init__(self, app):
		self.con = None
		self.app = app
		self.default_cursor = MySQLdb.cursors.Cursor
		self.connect()

	def connect(self):
		host = self.app.config['MYSQL_HOST']
		db = self.app.config['MYSQL_DB']
		user = self.app.config['MYSQL_USER']
		password = self.app.config['MYSQL_PASSWORD']
		try:
			self.con = MySQLdb.connect(host=host, db=db, user=user, password=password)
		except MySQLdb.OperationalError as e:
			exit(f"MySql Connection Error. Cannot run app.\n{str(e)}")
		except TypeError:
			exit(f"MySQL Connection Error. Some environment variables are wrong!")

	def query(self, sql, values=None, to_close=True, cursorclass=None):
		cursor = cursorclass if cursorclass is not None else self.default_cursor
		try:
			cur = self.con.cursor(cursor)
			cur.execute(sql, values)
			self.con.commit()
			if cur and to_close:
				cur.close()
			return cur
		except MySQLdb.OperationalError:
			self.connect()
			self.query(sql, values, to_close, cursorclass)
		except Exception as e:
			print(str(e))
			self.con.rollback()

	def get_row(self, sql, values=None, cursorclass=None):
		cur = self.query(sql, values, to_close=False, cursorclass=cursorclass)
		if not cur:
			return None
		res = cur.fetchone()
		cur.close()
		return res

	def get_all_rows(self, sql, values=None, cursorclass=None):
		cur = self.query(sql, values, to_close=False, cursorclass=cursorclass)
		if not cur:
			return None
		res = cur.fetchall()
		cur.close()
		return res

	def get_row_num(self, sql, values=None, cursorclass=None):
		cur = self.query(sql, values, to_close=False, cursorclass=cursorclass)
		if not cur:
			return None
		res = cur.rowcount
		cur.close()
		return res
