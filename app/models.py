from app import app, db
import flask.ext.whooshalchemy as whooshalchemy
from datetime import datetime

TEMPLATE_ANCHOR = 1
TEMPLATE_IMG = 2

class BaseClass(object):
    order = [
                'Users',
                'Computers',
                'Notebooks',
                'Monitors',
                'Upses',
                'Printers',
                'Scanners',
                'Software']
    
    def __repr__(self):
        return self.name

    def get_type_image(self):
        return ''

class User(db.Model, BaseClass):
    __searchable__ = ['login', 'name', 'surname', 'view_name']

    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(7), index = True, unique = True)
    name = db.Column(db.String(20), index = True)
    view_name = db.Column(db.String(41), index = True, unique=True)   
    surname = db.Column(db.String(20), index = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    did = db.Column(db.Integer)
    hardware_items = db.relationship('Hardware', backref='user', 
        lazy='dynamic')
    computers = db.relationship('Hardware', primaryjoin="and_(\
        User.id==Hardware.user_id, Hardware.hardware_type==1)", 
        backref='comp_owner', lazy='dynamic')
    monitors = db.relationship('Hardware', primaryjoin="and_(\
        User.id==Hardware.user_id, Hardware.hardware_type==3)",
        backref="monitor_owner", lazy='dynamic')
    notebooks = db.relationship('Hardware', primaryjoin="and_(\
        User.id==Hardware.user_id, Hardware.hardware_type==2)",
        backref="notebooks_owner", lazy='dynamic')
    upses = db.relationship('Hardware', primaryjoin="and_(\
        User.id==Hardware.user_id, Hardware.hardware_type==4)",
        backref="upses_owner", lazy='dynamic')
    history_hardware = db.relationship('History', backref='hist_users',
        lazy='dynamic')


    def __repr__(self):
        return '{} {}'.format(self.surname, self.name)

    def repr_list(self):
        # '1 'means that we want link for element to display; could be anything 
        return ((self, TEMPLATE_ANCHOR), (self.login, ), (self.department, TEMPLATE_ANCHOR))

    def get_path(self):
        return '/users/{}'.format(self.view_name)

    def column_names(self):
        return(['Name', 'Login', 'Department'])

    def get_type_image(self):
        return '/static/img/user.png'

class Department(db.Model, BaseClass):
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)   
    view_name = db.Column(db.String(20), index = True, unique=True)   
    users = db.relationship('User', primaryjoin="and_(\
        Department.id==User.department_id, User.did == None)", 
        backref='department', lazy='dynamic')
    all_users = db.relationship('User', backref="own_department", 
        lazy='dynamic')
    hardware_items = db.relationship('Hardware', backref='department', 
        lazy='dynamic')
    computers = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==1)", 
        backref='comp_department', lazy='dynamic')
    monitors = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==3)",
        backref="monitor_department", lazy='dynamic')
    notebooks = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==2)",
        backref="notebooks_department", lazy='dynamic')
    upses = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==4)",
        backref="upses_department", lazy='dynamic')
    scanners = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==6)",
        backref="scanners_department", lazy='dynamic')
    printers = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==5)",
        backref="printers_department", lazy='dynamic')

    def repr_list(self):
        return ((self, TEMPLATE_ANCHOR),)

    def get_path(self):
        return '/departments/{}'.format(self.view_name)

    def column_names(self):
        return(['Name'])

class Hardware(db.Model, BaseClass):
    __searchable__ = ['inum', 'serial', 'view_name']
    types = {
        1 : 'Desktop',
        2 : 'Notebook',
        3 : 'Monitor',
        4 : 'Ups',
        5 : 'Printer',
        6 : 'Scanner',
    }

    id = db.Column(db.Integer, primary_key = True)
    serial = db.Column(db.String, index = True)
    inum = db.Column(db.String, index = True)
    name = db.Column(db.String(100), index = True)
    view_name = db.Column(db.String(100), index = True, unique=True)   
    model = db.Column(db.String(100), index = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.Integer)
    software_items = db.relationship('Software', backref='hardware', 
        lazy='dynamic')
    hardware_type = db.Column(db.Integer, index = True)
    did = db.Column(db.Integer)
    history_users = db.relationship('History', backref='hist_hardware',
        lazy='dynamic')

    def repr_list(self):
        if self.user.did is not None:
            return ((self.types[self.hardware_type], TEMPLATE_IMG ), (self, TEMPLATE_ANCHOR),
            (self.model, ), (self.user.own_department, TEMPLATE_ANCHOR),
            ('not specified', ))
        return ((self.types[self.hardware_type], TEMPLATE_IMG), (self, TEMPLATE_ANCHOR),
            (self.model, ), (self.user.own_department, TEMPLATE_ANCHOR),
            (self.user, TEMPLATE_ANCHOR))

    def get_path(self):
        return '/hardware/{}'.format(self.view_name)

    def column_names(self):
        return(['Type', 'Name', 'Model', 'Department', 'User'])

    def get_type_image(self):
        return '/static/img/{}.png'.format(self.types[self.hardware_type].lower())

class Software(db.Model, BaseClass):
    __searchable__ = ['name', 'serial']
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), index = True)
    view_name = db.Column(db.String(100), index = True, unique=True)   
    serial = db.Column(db.String, index = True)
    comp_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    state = db.Column(db.Integer)

    def repr_list(self):
        if self.hardware.did is not None:
            return ((self, TEMPLATE_ANCHOR), ('not specified',),
                (self.hardware.department, TEMPLATE_ANCHOR))

        return ((self, TEMPLATE_ANCHOR), (self.hardware, TEMPLATE_ANCHOR), 
            (self.hardware.department, TEMPLATE_ANCHOR))

    def get_path(self):
        return '/software/{}'.format(self.view_name)

    def column_names(self):
        return(['Name', 'Computer', 'Department'])

    def get_type_image(self):
        return '/static/img/software.png'


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True, unique = True)
    password = db.Column(db.String(32))

# History = db.Table('history',
#     db.Column('hardware_id', db.Integer, db.ForeignKey('hardware.id')),
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
#     )
class History(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    change_date = db.Column(db.DateTime)

    def __init__(self, user_id, hardware_id, change_date = None):
        self.user_id = user_id
        self.hardware_id = hardware_id
        if change_date is None:
            change_date = datetime.utcnow()
        self.change_date = change_date


whooshalchemy.whoosh_index(app, User)
whooshalchemy.whoosh_index(app, Department)
whooshalchemy.whoosh_index(app, Hardware)
whooshalchemy.whoosh_index(app, Software)

