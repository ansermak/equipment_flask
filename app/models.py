from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(7), index = True, unique = True)
    name = db.Column(db.String(20), index = True)
    name_en = db.Column(db.String(41), index = True, unique=True)   
    surname = db.Column(db.String(20), index = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    hardware_items = db.relationship('Hardware', backref='user', lazy='dynamic')


    def __repr__(self):
        return '{} {}'.format(self.surname, self.name)

    def repr_list(self):
        return (('{} {}'.format(self.surname, self.name), self.name_en), (self.login, ), (self.department,'/departments/'+str(self.department)))

    def get_path(self):
        return '/users/'


class Department(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)   
    name_en = db.Column(db.String(20), index = True, unique=True)   
    users = db.relationship('User', backref='department', lazy='dynamic')
    hardware_items = db.relationship('Hardware', backref='department', lazy='dynamic')
    

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self.name, self.name_en),)

    def get_path(self):
        return '/departments/'

class Hardware(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    serial = db.Column(db.String, index = True, unique = True)
    inventory = db.Column(db.Integer, index = True, unique = True)
    name = db.Column(db.String(100))
    name_en = db.Column(db.String(100), index = True, unique=True)   
    model = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.Integer)
    software_items = db.relationship('Software', backref='hardware', lazy='dynamic')
    hardware_type = db.Column(db.Integer, index = True)

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self.name, self.name_en), (self.model, ), (self.department, '/departments/'+str(self.department)), (self.user, '/users/' + str(self.user.name_en)))

    def get_path(self):
        return '/hardware/'

class Software(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), index = True)
    name_en = db.Column(db.String(100), index = True, unique=True)   
    serial = db.Column(db.String, index = True, unique = True)
    comp_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    state = db.Column(db.Integer)

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self.name, self.name_en), (self.hardware, '/hardware/' + str(self.hardware)), (self.hardware.department, '/departments/' + str(self.hardware.department)))

    def get_path(self):
        return '/software/'

