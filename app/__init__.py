from flask import Flask

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


app = CustomFlask(__name__)
app.config["host"] = "remotemysql.com"
app.config["user"] = "EbumYmCv3K"
app.config["password"] = "8tdbKY8Vct"
app.config["db"] = "EbumYmCv3K"

from app import routes