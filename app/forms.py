from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, NoneOf

class UserForm(Form):
	login = StringField('login', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
	name = StringField('name', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
	surname = StringField('surname', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
	department = SelectField('department', choices=[])


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
	department = SelectField('department', choices=[])
	user = SelectField('user', choices=[])
	state = SelectField('state', 
		choices=[(1, 'In use'),
				(2, 'Under repair'), 
				(3, 'Free'),
		])

class SoftwareForm(Form):
	name = StringField('name', validators=[DataRequired(), 
        NoneOf([''], 'cannot be empty', None)])
	comp = SelectField('comp', choices=[])
	state = SelectField('state', 
		choices=[(1, 'In use'),
				(2, 'Free'),
		])
