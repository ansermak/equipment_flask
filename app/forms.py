#-*-coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, NoneOf
from app.models import Department, User, Hardware


STATUSES = {
    'STATUS_INUSE': 1,
    'STATUS_REPAIR': 2,
    'STATUS_FREE': 3
}

HARDWARE_TYPES = {
    'HARDWARE_DESKTOP': 1,
    'HARDWARE_NOTEBOOK': 2,
    'HARDWARE_MONITOR': 3,
    'HARDWARE_UPS': 4,
    'HARDWARE_PRINTER': 5,
    'HARDWARE_SCANNER': 6
}


class UserForm(Form):
    fields_order = ['name', 'surname', 'login', 'department_id']

    login = StringField('login', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    surname = StringField('surname', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    did = None
    department_id = SelectField('department', coerce=int,
        choices=[], validators=[DataRequired(),
            NoneOf([''], 'cannot be empty', None)])

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.department_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
                for i in Department.query.order_by('name').all()])


class DepartmentForm(Form):
    fields_order = ['name']
    name = StringField('name', validators=[DataRequired(),
            NoneOf([''], 'cannot be empty', None)])


class HardwareForm(Form):
    fields_order = ['hardware_type',
        'serial',
        'inum',
        'model',
        'name',
        'department_id',
        'user_id',
        'state']

    serial = StringField('serial', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    inum = StringField('inum', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    model = StringField('model', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    name = StringField('name', validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    department_id = SelectField('department', coerce=int,
        choices=[], validators=[DataRequired(),
            NoneOf([''], 'cannot be empty', None)])
    user_id = SelectField('user', choices=[], coerce=int,
        validators=[DataRequired(),
            NoneOf([''], 'cannot be empty', None)])
    state = SelectField('state',
            coerce=int,
            choices=[(STATUSES['STATUS_INUSE'], 'In use'),
                        (STATUSES['STATUS_REPAIR'], 'Under repair'),
                        (STATUSES['STATUS_FREE'], 'Free'),
            ], validators=[DataRequired(),
            NoneOf([''], 'cannot be empty', None)])
    hardware_type = SelectField('hardware_type',
            coerce=int,
            choices=[(0, '--Choose--'),
                        (HARDWARE_TYPES['HARDWARE_DESKTOP'], 'Desktop'),
                        (HARDWARE_TYPES['HARDWARE_NOTEBOOK'], 'Notebook'),
                        (HARDWARE_TYPES['HARDWARE_MONITOR'], 'Monitor'),
                        (HARDWARE_TYPES['HARDWARE_UPS'], 'UPS'),
                        (HARDWARE_TYPES['HARDWARE_PRINTER'], 'Printer'),
                        (HARDWARE_TYPES['HARDWARE_SCANNER'], 'Scaner'),
            ], validators=[DataRequired(),
            NoneOf([''], 'cannot be empty', None)])

    def __init__(self, *args, **kwargs):
        super(HardwareForm, self).__init__(*args, **kwargs)
        self.department_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
        for i in Department.query.order_by('name').all()])
        self.user_id.choices = ([(0, '--Choose--')] + [(i.id, i)
        for i in User.query.order_by('surname').all()])
        # не, ну а шо робить, якщо мені потрібне третє значення
        # в кожному туполі, а фласк, розраховує що їх там тільки два ?!
        self.user_id.choices2 = ([(0, '--Choose--', -1)] + [(i.id, i, i.department_id)
        for i in User.query.order_by('surname').all()])



class SoftwareForm(Form):
    fields_order = ['name', 'serial', 'comp_id', 'state']

    name = StringField('name', validators=[DataRequired(),
    NoneOf([''], 'cannot be empty', None)])
    serial = StringField('serial')
    comp_id = SelectField('comp', choices=[], coerce=int,
        validators=[DataRequired(),
        NoneOf([''], 'cannot be empty', None)])
    state = SelectField('state',
            coerce=int,
            choices=[(STATUSES['STATUS_INUSE'], 'In use'),
                        (STATUSES['STATUS_FREE'], 'Free'),
            ])

    def __init__(self, *args, **kwargs):
        super(SoftwareForm, self).__init__(*args, **kwargs)
        self.comp_id.choices = ([(0, '--Choose--')] + [(i.id, i.name)
        for i in Hardware.query.order_by('name').filter(
            Hardware.hardware_type == 1 or Hardware.did is not None).all()])


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])
