import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))


CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

#db path
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
#QLALCHEMY_DATABASE_URI = 'mysql://equipman:Qaz12345@10.109.0.76/app'
SQLALCHEMY_DATABASE_URI = 'mysql://equipman:Qaz12345@localhost/app'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

STATIC_FOLDER = 'static'
ITEM_IMAGE_FOLDER = STATIC_FOLDER + '/item_images'
JS_FOLDER = STATIC_FOLDER + '/js'

WHOOSH_BASE = os.path.join(basedir, 'search_db')
MAX_SEARCH_RESULTS = 50
