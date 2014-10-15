import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))


CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

#db path
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

STATIC_FOLDER = 'static'
ITEM_IMAGE_FOLDER = STATIC_FOLDER + '/item_images'
