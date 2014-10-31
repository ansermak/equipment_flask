from app import db

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

class User(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(7), index = True, unique = True)
    name = db.Column(db.String(20), index = True)
    name_en = db.Column(db.String(41), index = True, unique=True)   
    surname = db.Column(db.String(20), index = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    hardware_items = db.relationship('Hardware', backref='user', 
        lazy='dynamic')


    def __repr__(self):
        return '{} {}'.format(self.surname, self.name)

    def repr_list(self):
        # '1 'means that we want link for element to display; could be anything 
        return ((self, 1), (self.login, ), (self.department, 1))

    def get_path(self):
        return '/users/{}'.format(self.name_en)


class Department(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)   
    name_en = db.Column(db.String(20), index = True, unique=True)   
    users = db.relationship('User', backref='department', lazy='dynamic')
    hardware_items = db.relationship('Hardware', backref='department', 
        lazy='dynamic')
    

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self, 1),)

    def get_path(self):
        return '/departments/{}'.format(self.name_en)

class Hardware(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    serial = db.Column(db.String, index = True, unique = True)
    inventory = db.Column(db.Integer, index = True, unique = True)
    name = db.Column(db.String(100))
    name_en = db.Column(db.String(100), index = True, unique=True)   
    model = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.Integer)
    software_items = db.relationship('Software', backref='hardware', 
        lazy='dynamic')
    hardware_type = db.Column(db.Integer, index = True)

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self, 1), (self.model, ), (self.department, 1),
         (self.user, 1))

    def get_path(self):
        return '/hardware/{}'.format(self.name_en)

class Software(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), index = True)
    name_en = db.Column(db.String(100), index = True, unique=True)   
    serial = db.Column(db.String, index = True)
    comp_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    state = db.Column(db.Integer)

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self, 1), (self.hardware, 1), 
            (self.hardware.department, 1))

    def get_path(self):
        return '/software/{}'.format(self.name_en)

