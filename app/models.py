from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(7), index = True, unique = True)
    name = db.Column(db.String(20), index = True)
    name_en = db.Column(db.String(20), index = True, unique=True)   
    surname = db.Column(db.String(20), index = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    hardware_items = db.relationship('Hardware', backref='user', lazy='dynamic')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)   
    name_en = db.Column(db.String(20), index = True, unique=True)   
    users = db.relationship('User', backref='department', lazy='dynamic')
    hardware_items = db.relationship('Hardware', backref='department', lazy='dynamic')

class Hardware(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    serial = db.Column(db.Integer, index = True, unique = True)
    inventory = db.Column(db.Integer, index = True, unique = True)
    name = db.Column(db.String(100))
    name_en = db.Column(db.String(100), index = True, unique=True)   
    model = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.Integer)

class Software(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), index = True)
    name_en = db.Column(db.String(100), index = True, unique=True)   
    comp_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    state = db.Column(db.Integer)


