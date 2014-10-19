#-*-coding: utf-8-*-

from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from models import User, Department, Hardware, Software
from forms import UserForm, DepartmentForm, HardwareForm, SoftwareForm
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

      

class BaseEntity():
    """ Entity model should have fields name and name_en. Second one is used for generating url"""

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

     
    def base_list(self):
        """generates list of entites. If the list is empty - returns new form
        to input new data"""
        cnt = self.model.query.count()
        if cnt == 0:
            return redirect(self.entity_url_new)
        base_data = self.model.query.all()
        return render_template(self.template_list,
                base_data=base_data,
                page_name=self.name_display,
                add_item_url=self.entity_url_new)


    def base_edit(self):
        form = self.form()
        if form.validate_on_submit():
            base_data = self.model.query.filter(
                    self.model.name_en==self.url_param).first()
            if base_data is None:
                pass #!!!
            for a,b in form.data.items():
                #if type(b) == types.IntType: a = a + '_id'
                setattr(base_data, a, b)
            if db.session.is_modified(base_data):
                db.session.commit()    

            if request.values.get('submited') == 'Save & continue editing':
                return redirect(self.entity_url_edit)
            else:
                return redirect(self.entity_url)

        base_data = self.model.query.filter(
            self.model.name_en==self.url_param).first()
        if base_data is None:
            pass #!!!
        form = self.form(obj=base_data)
        return render_template(self.template_edit,
                page_name=self.name_display,
                add_item_url=self.entity_url_new,
                data=form)


    def base_new(self):
        form = self.form()
        if form.validate_on_submit():
            base_data = self.model()
            for a,b in form.data.items():
                #if type(b) == types.IntType: a = a + '_id'
                setattr(base_data, a, b)
            base_data.name_en = entity_uniq_name(base_data.name, self.model)
            db.session.add(base_data)
            db.session.commit()
            if request.values.get('submited') == 'Save & continue editing':
                return redirect(url_for(self.entity_url_edit, url_parameter=base_data.name_en))
            else:
                return redirect(self.entity_url)
        else:
            return render_template(self.template_edit,
                page_name=self.name_display,
                add_item_url=self.entity_url_new,
                data=form)



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/departments/')
def departments():
    depart = BaseEntity('department')
    return depart.base_list()


@app.route('/departments/<url_parameter>/', methods=['GET', 'POST'])
def department_edit(url_parameter):
    depart = BaseEntity('department', url_param=url_parameter)
    return depart.base_edit()


@app.route('/departments/new/', methods=['GET', 'POST'])
def department_new():
    depart = BaseEntity('department')
    return depart.base_new()
    

@app.route('/users/')
def users():
    users = BaseEntity('user')
    return users.base_list()

@app.route('/users/<url_parameter>/', methods=['GET', 'POST'])
def user_edit(url_parameter):
    users = BaseEntity('user', url_param=url_parameter)
    return users.base_edit()


@app.route('/users/new/', methods=['GET', 'POST'])
def user_new():
    users = BaseEntity('user')
    return users.base_new()
 
@app.route('/hardware/')
def hardwares():
    hard = BaseEntity('hardware')
    return hard.base_list()

@app.route('/hardware/<url_parameter>/', methods=['GET', 'POST'])
def hardware_edit(url_parameter):
    hard = BaseEntity('hardware', url_param=url_parameter)
    return hard.base_edit()


@app.route('/hardware/new/', methods=['GET', 'POST'])
def hardware_new():
    hard = BaseEntity('hardware')
    return hard.base_new()
 

@app.route('/software/')
def softwares():
    soft = BaseEntity('software')
    return soft.base_list()

@app.route('/software/<url_parameter>/', methods=['GET', 'POST'])
def software_edit(url_parameter):
    soft = BaseEntity('software', url_param=url_parameter)
    return soft.base_edit()


@app.route('/software/new/', methods=['GET', 'POST'])
def software_new():
    soft = BaseEntity('software')
    return soft.base_new()
 
