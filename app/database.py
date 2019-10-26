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
		port = int(self.app.config.get('MYSQL_PORT', 3306))
		db = self.app.config.get('MYSQL_DB')
		user = self.app.config.get('MYSQL_USER')
		password = self.app.config.get('MYSQL_PASSWORD')
		try:
			self.con = MySQLdb.connect(host=host, user=user, password=password, port=port)
		except (MySQLdb.OperationalError, TypeError) as e:
			print('MySql Connection Error. Cannot run app.')
			print('You should ensure that all environment variables are set and correct')
			exit(e)
		try:
			self.con.select_db(db)
		except MySQLdb.OperationalError:
			self.install_schema()
			self.con.select_db(db)

	def query(self, sql, **kwargs):
		"""
		:param sql: sql string
		:param kwargs: cur (if is not None, used and doesn't close after query),
					   values (to use with placeholders),
					   commit (if True, commits changes),
					   cur_class (DictCursor, etc)
		"""
		cur = kwargs.get('cur')
		values = kwargs.get('values')
		cur_class = kwargs.get('cur_class') or self.default_cursor
		try:
			if cur is None:
				with closing(self.con.cursor(cursorclass=cur_class)) as cur:
					cur.execute(sql, values)
			else:
				cur.execute(sql, values)
			if kwargs.get('commit'):
				self.con.commit()
		except MySQLdb.OperationalError:
			self.connect()
			self.query(sql, cur=cur, **kwargs)
		except Exception as e:
			self.con.rollback()
			raise Exception(e)

	def get_row(self, sql, **kwargs):
		cur_class = kwargs.get('cur_class') or self.default_cursor
		with closing(self.con.cursor(cursorclass=cur_class)) as cur:
			self.query(sql, cur=cur, **kwargs)
			return cur.fetchone()

	def get_all_rows(self, sql, **kwargs):
		cur_class = kwargs.get('cur_class') or self.default_cursor
		with closing(self.con.cursor(cursorclass=cur_class)) as cur:
			self.query(sql, cur=cur, **kwargs)
			return cur.fetchall()

	def get_row_num(self, sql, **kwargs):
		cur_class = kwargs.get('cur_class') or self.default_cursor
		with closing(self.con.cursor(cursorclass=cur_class)) as cur:
			self.query(sql, cur=cur, **kwargs)
			return cur.rowcount

	def install_schema(self):
		try:
			with closing(self.con.cursor()) as cur:
				with open(self.app.config['MYSQL_SCHEMA'], encoding='utf-8') as fd:
					commands = (line.strip() for line in fd.read().splitlines()
								if line and not line.strip().startswith('#')
								and not line.strip().startswith('--'))
					cur.execute(''.join(commands))
		except MySQLdb.ProgrammingError:
			self.con.rollback()
		finally:
			self.con.commit()
