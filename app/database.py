import MySQLdb
import MySQLdb.cursors
from flask import flash


class Database:
	def __init__(self, app):
		self.con = MySQLdb.connect(host=app.config["DB_HOST"], user=app.config["DB_USER"],
								   passwd=app.config["DB_PASSWORD"], db=app.config["DB_NAME"],
								   cursorclass=MySQLdb.cursors.DictCursor)
		self.cur = self.con.cursor()

	def __del__(self):
		self.cur.close()
		self.con.close()

	def query(self, sql, values=None):
		self.cur.execute(sql, values)
		if sql[:5] != "SELECT":
			self.con.commit()

	def get_row(self, sql, values=None):
		self.query(sql, values)
		res = self.cur.fetchone()
		return res

	def get_all_rows(self, sql, values=None):
		self.query(sql, values)
		res = self.cur.fetchall()
		return res

	def get_row_num(self, sql, values=None):
		self.query(sql, values)
		res = self.cur.rowcount
		return res

	def create_tables(self):
		return self.con

