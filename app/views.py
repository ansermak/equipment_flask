#-*-coding: utf-8-*-

from flask import render_template, flash, redirect, session, url_for, \
    request, g
from app import app, db
from config import MAX_SEARCH_RESULTS
from models import User, Department, Hardware, Software
from forms import UserForm, DepartmentForm, HardwareForm, SoftwareForm, \
    SearchForm, STATUS_INUSE, STATUS_FREE, HARDWARE_DESKTOP, HARDWARE_UPS,\
    HARDWARE_NOTEBOOK, HARDWARE_MONITOR, HARDWARE_PRINTER, HARDWARE_SCANNER
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
    """Creates uniq view_name for entity (model of entity should have fields 
    name and view_name):
    transliterates name and if such view_name exists in database
    adds underline and first free number
    """
    view_name = replace_other_chars(name)
    cnt = model.query.filter(model.view_name==view_name).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = model.query.filter(model.view_name=='{}_{}'.format(view_name,
                i)).count()
        rzlt = '{}_{}'.format(view_name, i)
    else:
        rzlt = view_name
    return rzlt


class NoEntityFoundException(Exception):
    
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# class should be a child of object 'object' to weork with 'super' func

class BaseEntity(object):
    """ Entity model should have fields name and view_name. 
    Second one is used for generating url"""


    def __init__(self, entity_name, url_param=None, template_list=None, 
        template_edit=None, entity_form=None):
        self.name = entity_name.lower()
        self.name_display = entity_name.capitalize()
        self.model = globals()[self.name_display]
        self.form = entity_form if entity_form is not None \
            else self.name_display + 'Form' 
        self.form = globals()[self.form]
        self.entity_url = url_for(self.name + 's')
        self.entity_url_new = url_for(self.name + '_new')
        self.entity_url_edit = self.name + '_edit'
        self.template_list = template_list if template_list is not None\
            else 'base_list.html'
        self.template_edit = template_edit if template_edit is not None \
            else 'base_edit.html'
        self.url_param = url_param
        if self.url_param:
            self.entity_url_edit = url_for(self.entity_url_edit, 
                url_parameter = self.url_param)

     

    def _save_data(self, base_data, form):
        for a,b in form.data.items():
            setattr(base_data, a,b)
        if base_data.view_name is None:
            base_data.view_name = self.create_name(base_data, self.model)
        db.session.add(base_data)
        db.session.commit()

    def create_name(self, base_data, model):
        return entity_uniq_name(base_data.name, model)

    def _get_base_data(self):
        if self.url_param is not None:
            base_data = self.model.query.filter(
                    self.model.view_name==self.url_param).first()
            if base_data is None:
                raise NoEntityFoundException(
                    'no instanse of {} with view_name=="{}" found'.format(
                        self.model.__name__, self.url_param))
        else:
            base_data = self.model()
        return base_data


    def _save_validated_form(self, form):
        base_data = self._get_base_data()
        self._save_data(base_data, form)
        if request.values.get('submitted') == 'Save & new':
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
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])
            
        return rzlt

    def get_blocks(self, result):
        user_software = []          
        for item in result['_base_data'].hardware_items.all():
            user_software += item.software_items.all()

        return {
            'Computers': result['_base_data'].computers.all(),
            'Notebooks': result['_base_data'].notebooks.all(),
            'Monitors': result['_base_data'].monitors.all(),
            'Upses': result['_base_data'].upses.all(),
            'Software': user_software 
        }
        
    def create_name(self, base_data, model):
        return entity_uniq_name('{} {}'.format(base_data.surname,
            base_data.name), model)

class DepartmentEntity(BaseEntity):
    def _save_data(self, base_data, form):
        super(DepartmentEntity, self)._save_data(base_data, form)
        department_id = base_data.id
        if base_data.id is None:
            department_counter = db.session.query(db.func.max(Department.id)).scalar()
            department_id = department_counter + 1 if department_counter else 1 
        department = Department.query.get(department_id)
        u = User.query.get('surname' == '--{}--'.format(department.view_name))
        if not u:
            u = User(login = department.name, name='Department', 
                department_id = department_id)
        u.view_name = '--{}-- Department'.format(department.name)
        u.surname = '--{}--'.format(department.name)
        db.session.add(u)
        db.session.commit()


    def _prepare_base_edit(self):
        rzlt = super(DepartmentEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])

        return rzlt

    def get_blocks(self, result):
        user_software = []          
        for item in result['_base_data'].hardware_items.all():
            user_software += item.software_items.all()

        return {
            'Users': result['_base_data'].users.all(),
            'Computers': result['_base_data'].computers.all(),
            'Notebooks': result['_base_data'].notebooks.all(),
            'Monitors': result['_base_data'].monitors.all(),
            'Upses': result['_base_data'].upses.all(),
            'Scanners': result['_base_data'].scanners.all(),
            'Printers': result['_base_data'].printers.all(),
            'Software': user_software 
        }

class HardwareEntity(BaseEntity):
    def _prepare_base_edit(self):
        rzlt = super(HardwareEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])
            
        return rzlt

    def get_blocks(self, result):
        return {'Software': result['_base_data'].software_items.all()}

class SoftwareEntity(BaseEntity):
    def create_name(self, base_data, model):
        softCounter = db.session.query(db.func.max(model.id)).scalar()
        softCounter = softCounter + 1 if softCounter else 1 

        return entity_uniq_name('software_item_{}'.format(softCounter), model)

@app.before_request
def before_request():
    g.search_form = SearchForm()

@app.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
def search_results(query):
    users = User.query.whoosh_search('*{}*'.format(query), 
        MAX_SEARCH_RESULTS).all()
    departments = Department.query.whoosh_search('*{}*'.format(query), 
        MAX_SEARCH_RESULTS).all()
    software = Software.query.whoosh_search('*{}*'.format(query), 
        MAX_SEARCH_RESULTS).all()
    hardware = Hardware.query.whoosh_search('*{}*'.format(query), 
        MAX_SEARCH_RESULTS).all()
    results = [('Users', users),
        ('Departments', departments),
        ('Software', software),
        ('Hardware', hardware)]
        
    return render_template('search_results.html',
        query = query,
        results = results)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/departments/')
def departments():
    depart = BaseEntity('department', template_edit='base_edit.html')
    return depart.base_list()


@app.route('/departments/new/', methods=['GET', 'POST'])
def department_new():
    depart = DepartmentEntity('department')
    return depart.base_new()

@app.route('/departments/<url_parameter>/', methods=['GET', 'POST'])
def department_edit(url_parameter):
    depart = DepartmentEntity('department', 
            template_edit='base_edit.html',
            url_param=url_parameter)
    try:
        return depart.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')

    

@app.route('/users/')
def users():
    users = UserEntity('user', template_edit='base_edit.html')
    return users.base_list('surname')

@app.route('/users/<url_parameter>/', methods=['GET', 'POST'])
def user_edit(url_parameter):
    users = UserEntity('user', 
            template_edit='base_edit.html', 
            url_param=url_parameter)
    try:
        return users.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/new/', methods=['GET', 'POST'])
def user_new():
    users = UserEntity('user')
    return users.base_new()
 
@app.route('/hardware/')
def hardwares():
    hard = HardwareEntity('hardware', template_edit='base_edit.html')
    return hard.base_list('view_name')

@app.route('/hardware/<url_parameter>/', methods=['GET', 'POST'])
def hardware_edit(url_parameter):
    hard = HardwareEntity('hardware', 
        template_edit='base_edit.html', 
        url_param=url_parameter)
    try:
        return hard.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/hardware/new/', methods=['GET', 'POST'])
def hardware_new():
    hard = HardwareEntity('hardware')
    return hard.base_new()
 

@app.route('/software/')
def softwares():
    soft = SoftwareEntity('software')
    return soft.base_list('name')

@app.route('/software/<url_parameter>/', methods=['GET', 'POST'])
def software_edit(url_parameter):
    soft = SoftwareEntity('software', url_param=url_parameter)
    try:
        return soft.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/software/new/', methods=['GET', 'POST'])
def software_new():
    soft = SoftwareEntity('software')
    return soft.base_new()
 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
