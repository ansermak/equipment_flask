from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, NoneOf
from app.models import Department, User, Hardware

class UserForm(Form):
    login = StringField('login', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    surname = StringField('surname', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    department_id = SelectField('department', default=0, coerce=int,  
        choices=[])

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.department_id.choices=[(0,'--choose--')] + [(i.id, i.name) for i in Department.query.order_by('name').all()]
        


class DepartmentForm(Form):
	name = StringField('name', validators=[DataRequired(), 
            NoneOf([''], 'cannot be empty', None)])

class HardwareForm(Form):
    serial = StringField('serial', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    inventory = StringField('inventory', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    model = StringField('model', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    department_id = SelectField('department', coerce=int,  
        choices=[])
    user_id = SelectField('user', choices=[], coerce=int)
    state = SelectField('state', 
            coerce=int,
            choices=[(1, 'In use'),
                        (2, 'Under repair'), 
                        (3, 'Free'),
            ])
  
    def __init__(self, *args, **kwargs):
        super(HardwareForm, self).__init__(*args, **kwargs)
        self.department_id.choices = [(0,'Choose')] + [(i.id, i.name) for i in Department.query.order_by('name').all()]
        self.user_id.choices = [(0,'Choose')] + [(i.id, i) for i in User.query.order_by('surname').all()]

class SoftwareForm(Form):
    name = StringField('name', validators=[DataRequired(), 
    NoneOf([''], 'cannot be empty', None)])
    serial = StringField('serial', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    comp_id = SelectField('comp', choices=[],coerce=int)
    state = SelectField('state', 
            coerce=int,
            choices=[(1, 'In use'),
                        (2, 'Free'),
            ])
    def __init__(self, *args, **kwargs):
        super(SoftwareForm, self).__init__(*args, **kwargs)
        self.comp_id.choices = [(0,'Choose')] + [(i.id, i.name) for i in Hardware.query.order_by('name').all()]
