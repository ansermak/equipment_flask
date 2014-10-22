#-*-coding: utf-8-*-

from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from models import User, Department, Hardware, Software
from forms import UserForm, DepartmentForm, HardwareForm, SoftwareForm, STATUS_INUSE, STATUS_FREE
import re
import types

def replace_other_chars(string):
    """replace all not latin and not numeric chars with hyphen
    >>> replace_other_chars(u'мама мыла ramy мылом23!')
    u'ramy-23'
    """
    string = re.sub(r"((?![a-zA-Z0-9\-']).)", '-', string )
    string = re.sub(r"[\-]+",'-', string)
    string = re.sub('^[-]+', '', string)
    string = re.sub('[-]+$', '', string)
    return string


def entity_uniq_name(name, model):
    """Creates uniq name_en for entity (model of entity should have fields 
    name and name_en):
    transliterates name and if such name_en exists in database
    adds underline and first free number
    """
    name_en = replace_other_chars(name)
    cnt = model.query.filter(model.name_en==name_en).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = model.query.filter(model.name_en=='{}_{}'.format(name_en, i)).count()
        rzlt = '{}_{}'.format(name_en, i)
    else:
        rzlt = name_en
    return rzlt


class NoEntityFoundException(Exception):
    
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# class should be a child of object 'object' to weork with 'super' func

class BaseEntity(object):
    """ Entity model should have fields name and name_en. 
    Second one is used for generating url"""


    def __init__(self, entity_name, url_param=None, template_list=None, template_edit=None, entity_form=None):
        self.name = entity_name.lower()
        self.name_display = entity_name.capitalize()
        self.model = globals()[self.name_display]
        self.form = entity_form if entity_form is not None else self.name_display + 'Form' 
        self.form = globals()[self.form]
        self.entity_url = url_for(self.name + 's')
        self.entity_url_new = url_for(self.name + '_new')
        self.entity_url_edit = self.name + '_edit'
        self.template_list = template_list if template_list is not None else 'base_list.html'
        self.template_edit = template_edit if template_edit is not None else 'base_edit.html'
        self.url_param = url_param
        if self.url_param:
            self.entity_url_edit = url_for(self.entity_url_edit, url_parameter = self.url_param)

     

    def _save_data(self, base_data, form):
        for a,b in form.data.items():
            setattr(base_data, a,b)
        if base_data.name_en is None:
            base_data.name_en = entity_uniq_name(base_data.name, self.model)
        db.session.add(base_data)
        db.session.commit()


    def _get_base_data(self):
        if self.url_param is not None:
            base_data = self.model.query.filter(
                    self.model.name_en==self.url_param).first()
            if base_data is None:
                raise NoEntityFoundExceotion(
                    'no instanse of {} with name_en=="{}" found'.format(
                        self.model.__name__, self.url_param))
        else:
            base_data = self.model()
        return base_data


    def _save_validated_form(self, form):
        base_data = self._get_base_data()
        self._save_data(base_data, form)
        if request.values.get('submited') == 'Save & new':
            return self.entity_url_new
        else:
            return self.entity_url


    def _prepare_base_edit(self):
        form = self.form()
        if form.validate_on_submit():
            return ('redirect', self._save_validated_form(form))
        base_data = self._get_base_data()
        if not form.errors:
            form = self.form(obj=base_data)
        return ('template', self.template_edit, {
                'page_name':self.name_display,
                'add_item_url':self.entity_url_new,
                'form':form,
                '_base_data':base_data
            })


    def base_list(self, sort_field ='name'):
        """generates list of entites. If the list is empty - returns new form
        to input new data"""
        cnt = self.model.query.count()
        
        if cnt == 0:
            return redirect(self.entity_url_new)
        base_data = self.model.query.order_by(sort_field).all()
        return render_template(self.template_list,
                base_data=base_data,
                page_name=self.name_display,
                add_item_url=self.entity_url_new)



    def base_edit(self):
        rzlt = self._prepare_base_edit()
        if rzlt[0] == 'redirect':
            return redirect(rzlt[1])
        return render_template(rzlt[1], data=rzlt[2])


    def base_new(self):
        form = self.form()
        if form.validate_on_submit():
            return redirect(self._save_validated_form(form))
        else:
            return render_template(self.template_edit,
                data={'page_name':self.name_display,
                    'add_item_url':self.entity_url_new,
                    'form':form})


class UserEntity(BaseEntity):

    def _prepare_base_edit(self):
        rzlt = super(UserEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['hard_free_in_depart'] = Hardware.query.filter(
                    Hardware.department_id == rzlt[2]['_base_data'].department_id,
                    Hardware.state == STATUS_FREE).all()
            rzlt[2]['hard_free'] = Hardware.query.filter(
                    Hardware.department_id != rzlt[2]['_base_data'].department_id,
                    Hardware.state == STATUS_FREE).all()
            rzlt[2]['soft_free'] = Software.query.filter(
                    Software.state == STATUS_FREE
                    #! on free comps
                    )
        return rzlt


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/departments/')
def departments():
    depart = BaseEntity('department')
    return depart.base_list()


@app.route('/departments/new/', methods=['GET', 'POST'])
def department_new():
    depart = BaseEntity('department')
    return depart.base_new()

@app.route('/departments/<url_parameter>/', methods=['GET', 'POST'])
def department_edit(url_parameter):
    depart = BaseEntity('department', url_param=url_parameter)
    try:
        return depart.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')

    

@app.route('/users/')
def users():
    users = BaseEntity('user', template_edit='user_edit.html')
    return users.base_list('surname')

@app.route('/users/<url_parameter>/', methods=['GET', 'POST'])
def user_edit(url_parameter):
    users = UserEntity('user', template_edit='user_edit.html', url_param=url_parameter)
    try:
        return users.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/new/', methods=['GET', 'POST'])
def user_new():
    users = BaseEntity('user', template_edit='user_edit.html')
    return users.base_new()
 
@app.route('/hardware/')
def hardwares():
    hard = BaseEntity('hardware')
    return hard.base_list('name')

@app.route('/hardware/<url_parameter>/', methods=['GET', 'POST'])
def hardware_edit(url_parameter):
    hard = BaseEntity('hardware', url_param=url_parameter)
    try:
        return hard.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/hardware/new/', methods=['GET', 'POST'])
def hardware_new():
    hard = BaseEntity('hardware')
    return hard.base_new()
 

@app.route('/software/')
def softwares():
    soft = BaseEntity('software')
    return soft.base_list('name')

@app.route('/software/<url_parameter>/', methods=['GET', 'POST'])
def software_edit(url_parameter):
    soft = BaseEntity('software', url_param=url_parameter)
    try:
        return soft.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/software/new/', methods=['GET', 'POST'])
def software_new():
    soft = BaseEntity('software')
    return soft.base_new()
 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
