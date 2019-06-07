from app.database import db
from flask import current_app


class Ajax:
	def registration(self, form):
		with db.cur as cur:
			sql = "INSERT INTO `users`(login, name, surname, email, password, token) VALUES(%s, %s, %s, %s, %s, %s)"
			cur.execute(sql, (
				form["login"],
				form["name"],
				form["surname"],
				form["email"],
				form["pass"],
				"228336"
			))
		db.con.commit()
