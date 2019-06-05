from app import app
import pymysql


class Database:
	def __init__(self):
		self.con = pymysql.connect(host=app.config["host"], user=app.config["user"], password=app.config["password"], db=app.config["db"], cursorclass=pymysql.cursors.DictCursor)
		self.cur = self.con.cursor()