# --*-- coding: utf-8 --*--
import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import timedelta

# LDAP config
Server = 'ldap://10.109.0.60'
base = 'OU=IT,OU=Users,OU=GfK Ukraine,DC=gfk,DC=com'
Filter = "(&(objectClass=user)(mail={}))"
# Attrs = ["displayName"]


app = Flask(__name__)


app.config['SECRET_KEY'] = os.urandom(24)
app.permanent_session_lifetime = timedelta(seconds=3600)
app.config.from_object('config')
db = SQLAlchemy(app)
app.jinja_env.add_extension('jinja2.ext.do')

from app import models, views
