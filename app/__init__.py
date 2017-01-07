import os

from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask_mail import Mail
from threading import Thread

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

auth = HTTPBasicAuth()

app_errors = {
    'NotFound': {
        'message': 'The object you are looking for was not found.',
    },
    'UnexpectedError': {
        'message': 'Something unexpected happened.',
    },
    'Unauthorized': {
        'message': 'You are not authorized to access this area.',
    }
}

api = Api(app, errors=app_errors)

from app.models import tables
from app.controllers import users, books, notification

@manager.command
def admin(mail):
    adm = tables.User.query.filter_by(name='admin').first()
    if adm is None:
        adm = tables.User(name='admin',password='admin',email=mail,admin=2)
        adm.hash_password('admin')
        db.session.add(adm)
        db.session.commit()
        print("Admin created!")
    else:
        print("Admin already exists!")

@manager.command
def notify():
    # Starts a thread for daily notification about one-day
    # deadlines and three days for returning books
    notification_ = Thread(target=notification.email)

    # When it is necessary to make a migrate or an upgrade comment this line
    notification_.start()
