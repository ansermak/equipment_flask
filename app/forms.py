# -*-coding: utf-8 -*-s
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import DataRequired, NoneOf
from app.models import Department, User, Hardware, HType


STATUSES = {
    'STATUS_INACTIVE': 0,
    'STATUS_INUSE': 1,
    'STATUS_REPAIR': 2,
    'STATUS_FREE': 3
}

IS_ACTIVE = {
    'True': 1,
    'False': 0
}


class UserForm(Form):
    fields_order = ['name', 'surname', 'login', 'department_id', 'is_active']

    login = StringField('login', validators=[DataRequired(),
                        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(),
                       NoneOf([''], 'cannot be empty', None)])
    surname = StringField('surname', validators=[DataRequired(),
                          NoneOf([''], 'cannot be empty', None)])
    did = None
    department_id = SelectField('department', coerce=int, choices=[],
                                validators=[DataRequired(),
                                NoneOf([''], 'cannot be empty', None)])
    is_active = SelectField('Enabled',
                            coerce=int,
                            choices=[(IS_ACTIVE['True'], 'Yes'),
                                     (IS_ACTIVE['False'], 'No'), ])

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.department_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
                                      for i in Department.query.order_by(
                                      'name').all()])


class DepartmentForm(Form):
    fields_order = ['name']
    name = StringField('name', validators=[DataRequired(),
                       NoneOf([''], 'cannot be empty', None)])


class HardwareForm(Form):
    fields_order = ['hardware_type',
                    'serial',
                    'inum',
                    'model',
                    'motherboard',
                    'cpu',
                    'memory',
                    'resolution',
                    'hdd',
                    'name',
                    'department_id',
                    'user_id',
                    'state']

    serial = StringField('serial')
    inum = StringField('inum')
    model = StringField('model')
    motherboard = StringField('motherboard')
    cpu = StringField('cpu')
    memory = StringField('memory')
    resolution = StringField('resolution')
    hdd = StringField('hdd')
    name = StringField('name', validators=[DataRequired(),
                       NoneOf([''], 'cannot be empty', None)])
    department_id = SelectField('department', coerce=int, choices=[],
                                validators=[DataRequired(), NoneOf([''],
                                            'cannot be empty', None)])
    user_id = SelectField('user', choices=[], coerce=int,
                          validators=[DataRequired(), NoneOf([''],
                                      'cannot be empty', None)])
    state = SelectField('state', coerce=int,
                        choices=[(STATUSES['STATUS_INUSE'], 'In use'),
                                 (STATUSES['STATUS_REPAIR'], 'Being repaired'),
                                 (STATUSES['STATUS_FREE'], 'Free'),
                                 (STATUSES['STATUS_INACTIVE'], 'Not active')])
    hardware_type = SelectField('hardware_type', coerce=int, choices=[],
                                validators=[DataRequired(),
                                NoneOf([''], 'cannot be empty', None)])

    def __init__(self, *args, **kwargs):
        super(HardwareForm, self).__init__(*args, **kwargs)
        self.department_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
                                      for i in Department.query.order_by(
                                      'name').all()])
        self.user_id.choices = ([(0, '--Choose--')] + [(i.id, i)
                                for i in User.query.order_by(
                                'surname').all()])
        # не, ну а шо робить, якщо мені потрібне третє значення
        # в кожному туполі, а фласк, розраховує що їх там тільки два ?!
        self.user_id.choices2 = ([(0, '--Choose--', -1)]
                                 + [(i.id, i, i.department_id)
                                 for i in User.query.order_by(
                                    'surname').all()])
        self.hardware_type.choices = ([(0, '--Choose--')] + [(ht.id, ht.name)
        for ht in HType.query.order_by('id').all()])


class SoftwareForm(Form):
    fields_order = ['name', 'serial', 'department_id', 'comp_id', 'state']

    name = StringField('name',
                       validators=[DataRequired(), NoneOf([''],
                                   'cannot be empty', None)])
    serial = StringField('serial')
    department_id = SelectField('department', coerce=int, choices=[],
                                validators=[DataRequired(), NoneOf([''],
                                            'cannot be empty', None)])
    comp_id = SelectField('comp', choices=[], coerce=int,
                          validators=[DataRequired(), NoneOf([''],
                                      'cannot be empty', None)])
    state = SelectField('state', coerce=int,
                        choices=[(STATUSES['STATUS_INUSE'], 'In use'),
                                 (STATUSES['STATUS_FREE'], 'Free'),
                                 (STATUSES['STATUS_INACTIVE'], 'Not active')])

    def __init__(self, *args, **kwargs):
        super(SoftwareForm, self).__init__(*args, **kwargs)
        self.comp_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
                                for i in Hardware.query.order_by(
                                'name').filter(
            (Hardware.hardware_type == None) |
            (Hardware.hardware_type == 1) |
            (Hardware.hardware_type == 2)).all()])
        self.comp_id.choices2 = ([(0, '--Choose--', -1)] + [(i.id,
                                                            i, i.department_id)
                                 for i in Hardware.query.order_by(
                                 'name').filter(
                                (Hardware.hardware_type == None) |
                                (Hardware.hardware_type == 1) |
                                (Hardware.hardware_type == 2)).all()])
        self.department_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
                                      for i in Department.query.order_by(
                                      'name').all()])


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


class LoginForm(Form):
    email = StringField('name', validators=[DataRequired(),
                        NoneOf([''], 'Can not be empty', None)])
    password = PasswordField('password', validators=[DataRequired(),
                             NoneOf([''], 'Can not be empty', None)])


class ReportForm(Form):
    department = SelectField('department', coerce=int, choices=[],
                             validators=[DataRequired(), NoneOf([''],
                                         'cannot be empty', None)])

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.department.choices = ([(0, '--Choose--')] + [(i.id, i.name)
                                   for i in Department.query.order_by(
                                   'name').all()]
                                   + [(100, 'ALL DEPARTMENTS')])
