# -*- coding: utf-8 -*-
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def hello_world():
	return render_template("index.html", username="fads")
