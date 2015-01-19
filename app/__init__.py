from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.permanent_session_lifetime = timedelta(seconds=600)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import models, views
