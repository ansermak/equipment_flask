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
    
    def __repr__(self):
        return self.name

class User(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(7), index = True, unique = True)
    name = db.Column(db.String(20), index = True)
    view_name = db.Column(db.String(41), index = True, unique=True)   
    surname = db.Column(db.String(20), index = True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
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


    def __repr__(self):
        return '{} {}'.format(self.surname, self.name)

    def repr_list(self):
        # '1 'means that we want link for element to display; could be anything 
        return ((self, 1), (self.login, ), (self.department, 1))

    def get_path(self):
        return '/users/{}'.format(self.view_name)


class Department(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)   
    view_name = db.Column(db.String(20), index = True, unique=True)   
    users = db.relationship('User', backref='department', lazy='dynamic')
    hardware_items = db.relationship('Hardware', backref='department', 
        lazy='dynamic')
    computers = db.relationship('Hardware', primaryjoin="and_(\
        Department.id==Hardware.department_id, Hardware.hardware_type==1)", 
        backref='comp_odepartment', lazy='dynamic')
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
        return ((self, 1),)

    def get_path(self):
        return '/departments/{}'.format(self.view_name)

class Hardware(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    serial = db.Column(db.String, index = True, unique = True)
    inventory = db.Column(db.Integer, index = True, unique = True)
    name = db.Column(db.String(100))
    view_name = db.Column(db.String(100), index = True, unique=True)   
    model = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.Integer)
    software_items = db.relationship('Software', backref='hardware', 
        lazy='dynamic')
    hardware_type = db.Column(db.Integer, index = True)

    def repr_list(self):
        return ((self, 1), (self.model, ), (self.department, 1),
         (self.user, 1))

    def get_path(self):
        return '/hardware/{}'.format(self.view_name)

class Software(db.Model, BaseClass):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), index = True)
    view_name = db.Column(db.String(100), index = True, unique=True)   
    serial = db.Column(db.String, index = True)
    comp_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    state = db.Column(db.Integer)

    def repr_list(self):
        return ((self, 1), (self.hardware, 1), 
            (self.hardware.department, 1))

    def get_path(self):
        return '/software/{}'.format(self.view_name)

