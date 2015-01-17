from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'venividivici'
app.config.from_object('config')
db = SQLAlchemy(app)

from app import models, views
