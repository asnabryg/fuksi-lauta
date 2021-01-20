from flask_sqlalchemy import SQLAlchemy
from os import getenv, urandom
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = urandom(16).hex()
db = SQLAlchemy(app)
