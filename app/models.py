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
        return (('{}-{}'.format(self.surname, self.name), self.name_en), (self.login, self.name_en), (self.department,'/departments/'+str(self.department)))


class Department(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)   
    name_en = db.Column(db.String(20), index = True, unique=True)   
    users = db.relationship('User', backref='department', lazy='dynamic')
    hardware_items = db.relationship('Hardware', backref='department', lazy='dynamic')
    

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self.name, self.name),)

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
    software_items = db.relationship('Software', backref='comp', lazy='dynamic')

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self.name, self.name), (self.model), (self.department, '/departments/'+str(self.department)), (self.user, '/users/' + str(self.user.name_en)))

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
        return ((self.name, self.name), (self.comp, '/hardware/' + str(self.comp)), (self.comp.department, '/departments/' + str(self.comp.department)))

