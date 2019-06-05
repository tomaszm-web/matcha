# -*- coding: utf-8 -*-
from flask import render_template
from app import app
from .database import Database

@app.route('/')
@app.route('/index')
def index():
	db = Database()
	return render_template("index.html")
