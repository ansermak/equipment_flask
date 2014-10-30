from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, NoneOf
from app.models import Owner, Compware


STATUS_INUSE = 1
STATUS_REPAIR = 2
STATUS_FREE = 3

class UserForm(Form):
    fields_order = ['name', 'surname', 'login', 'parent_id']

    login = StringField('login', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    surname = StringField('surname', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    parent_id = SelectField('department', default=0, coerce=int,  
        choices=[])

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.parent_id.choices=[(0,'--choose--')] + [(i.id, i.login) \
                for i in Owner.query.filter(
                    Owner.parent_id == None).order_by('name').all()]
        
class DepartmentForm(Form):
    fields_order = ['login']
    login = StringField('name', validators=[DataRequired(), 
            NoneOf([''], 'cannot be empty', None)])

class CompwareForm(Form):
    fields_order = ['serial', 'inventory', 'model', 'name', 'owner_id', 'state']
    serial = StringField('serial', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    inventory = StringField('inventory', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    model = StringField('model', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
    owner_id = SelectField('onwer', coerce=int,  
        choices=[])
    state = SelectField('state', 
            coerce=int,
            choices=[(STATUS_INUSE, 'In use'),
                        (STATUS_REPAIR, 'Under repair'), 
                        (STATUS_FREE, 'Free'),
            ])
  
    def __init__(self, *args, **kwargs):
        super(CompwareForm, self).__init__(*args, **kwargs)
        self.owner_id.choices = [(0,'Choose')] + [(i.id, i.name) \
                for i in Owner.query.order_by('name').all()]



