from app import db
from sqlalchemy.orm import backref

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(7), index = True, unique = True)
    name = db.Column(db.String(20), index = True)
    surname = db.Column(db.String(20), index = True)
    parent_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
    workers = db.relationship('Owner',
                              backref=backref("department", remote_side=[id]))
    comp_items = db.relationship('Compware', backref='owner', lazy='dynamic')

    def __repr__(self):
        if self.parent_id is not None: # if None - this is department
            rzlt = '{} {}'.format(self.surname, self.name)
        else:
            rzlt  = self.login
        return rzlt

    def repr_list(self):
        if self.parent_id is not None: 
            return (('{} {}'.format(self.surname, self.name), self.login),
                (self.login, ),
                (self.department,'/departments/'+str(self.department)))
        else:
            return ((self.login, self.login),)


class Compware(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    serial = db.Column(db.String, index = True, unique = True)
    inventory = db.Column(db.Integer, index = True, unique = True)
    name = db.Column(db.String(100))
    model = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
    state = db.Column(db.Integer)
    type_ = db.Column(db.Integer) # '_' added according to pep8
    computer = db.Column(db.Integer, db.ForeignKey('compware.id'))

    def __repr__(self):
        return self.name

    def repr_list(self):
        return ((self.name, self.name), 
            (self.model, ), 
            (self.owner, '/users/' + str(self.owner.login)))


