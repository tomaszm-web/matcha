from contextlib import closing

import MySQLdb
import MySQLdb.cursors


class Database:
	def __init__(self, app):
		self.con = None
		self.app = app
		self.default_cursor = MySQLdb.cursors.Cursor
		self.connect()

	def connect(self):
		host = self.app.config.get('MYSQL_HOST')
		db = self.app.config.get('MYSQL_DB')
		user = self.app.config.get('MYSQL_USER')
		password = self.app.config.get('MYSQL_PASSWORD')
		try:
			self.con = MySQLdb.connect(host=host, user=user, password=password)
		except (MySQLdb.OperationalError, TypeError) as e:
			print('MySql Connection Error. Cannot run app.')
			print('You should ensure that all environment variables are set and correct')
			exit(e)
		try:
			self.con.select_db(db)
		except MySQLdb.OperationalError:
			self.install_schema()
			self.con.select_db(db)

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
			self.con.rollback()
			raise Exception(e)

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

	def install_schema(self):
		with closing(self.con.cursor()) as cur:
			with open(self.app.config['MYSQL_SCHEMA'], encoding='utf-8') as fd:
				commands = (line.strip() for line in fd.read().splitlines()
							if line and not line.strip().startswith('#') and not line.strip().startswith('--'))
				cur.execute(''.join(commands))
		# self.con.commit()
