#-*-coding: utf-8-*-

from flask import (render_template, flash, redirect, url_for, 
    request, g, jsonify)
from app import app, db
from config import MAX_SEARCH_RESULTS
from models import User, Department, Hardware, Software
from forms import (SearchForm, UserForm, DepartmentForm, HardwareForm, 
    SoftwareForm, STATUSES, HARDWARE_TYPES)
import re


PLURALS = {
    'user': 'users',
    'department': 'departments',
    'software': 'software_items',
    'hardware': 'hardware_items'
}

BUTTONS = {'department':{'user':'/users/new/',
                        'hardware':'/hardware/new/',
                        'software':'/software/new/'},
        'user': {'hardware':'/hardware/new/',
                'software':'/software/new/'},
        'hardware': {'hardware':'/hardware/new/',
                    'software':'/software/new/'},
                    }


def replace_other_chars(string):
    """replace all not latin and not numeric chars with hyphen
    >>> replace_other_chars(u'мама мыла ramy мылом23!')
    u'ramy-23'
    """
    string = re.sub(r"((?![a-zA-Z0-9\-']).)", '-', string)
    string = re.sub(r"[\-]+", '-', string)
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
    cnt = model.query.filter(model.view_name == view_name).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = model.query.filter(model.view_name == '{}_{}'.format(
                view_name, i)).count()
        rzlt = '{}_{}'.format(view_name, i)
    else:
        rzlt = view_name
    return rzlt


class NoEntityFoundException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseEntity(object):

    """ Entity model should have fields name and view_name. 
    Second one is used for generating url"""

    def __init__(self, entity_name, url_param=None, 
                template_list='base_list.html', template_edit='base_edit.html',
                template_view='base_view.html', entity_form=None):

        self.name = entity_name.lower()
        self.name_display = entity_name.capitalize()
        self.model = globals()[self.name_display]
        self.form = (entity_form if entity_form is not None
            else self.name_display + 'Form')
        self.form = globals()[self.form]
        self.entity_url = url_for(PLURALS[self.name])
        self.entity_url_new = url_for(self.name + '_new')
        self.entity_url_edit = self.name + '_edit'
        self.template_list = template_list
        self.template_edit = template_edit
        self.template_view = template_view
        self.url_param = url_param
        
        if self.name in BUTTONS:
            self.buttons = BUTTONS[self.name]
        else:
            buttons = {}

        if self.url_param:
            self.entity_url_edit = url_for(self.entity_url_edit,
                                           url_parameter=self.url_param)

    def _save_data(self, base_data, form):
        for a, b in form.data.items():
            setattr(base_data, a, b)
        base_data.view_name = self.create_name(base_data, self.model)
        db.session.add(base_data)
        db.session.commit()

    def _delete_data(self, base_data):
        db.session.delete(base_data)
        db.session.commit()

    def create_name(self, base_data, model):
        return entity_uniq_name(base_data.name, model)


    def _get_base_data(self):
        if self.url_param is not None:
            base_data = self.model.query.filter(
                self.model.view_name == self.url_param).first()
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
        elif request.values.get('submitted') == 'Delete':
            self._delete_data(base_data)

        return self.entity_url

    def _prepare_base_edit(self):
        form = self.form()
        if form.validate_on_submit():
            return ('redirect', self._save_validated_form(form))
        base_data = self._get_base_data()
        if not form.errors:
            form = self.form(obj=base_data)

        return ('template', self.template_edit, {
                'page_name': self.name_display,
                'add_item_url': self.entity_url_new,
                'form': form,
                '_base_data': base_data,
                'buttons': self.buttons
                })

    def _prepare_base_view(self, order=None):
        base_data = self._get_base_data()
        return ('template', self.template_view, {
            'page_name': self.name_display,
            '_base_data': base_data,
            'order': order,
        })

    def base_list(self, sort_field='name', model_filter='""'):
        """generates list of entites. If the list is empty - returns new form
        to input new data"""
        cnt = self.model.query.count()

        if cnt == 0:
            return redirect(self.entity_url_new)
        base_data = self.model.query.filter(
            eval(model_filter)).order_by(sort_field).all()
        return render_template(self.template_list,
                               base_data=base_data,
                               page_name=self.name_display,
                               add_item_url=self.entity_url_new)

    def base_edit(self):
        rzlt = self._prepare_base_edit()
        if rzlt[0] == 'redirect':
            return redirect(rzlt[1])
        return render_template(rzlt[1], data=rzlt[2])

    def base_view(self):
        rzlt = self._prepare_base_view()
        return render_template(rzlt[1], data=rzlt[2])

    def base_new(self):
        form = self.form()
        if form.validate_on_submit():
            return redirect(self._save_validated_form(form))
        else:
            return render_template(self.template_edit,
                                   data={'page_name': self.name_display,
                                         'add_item_url': self.entity_url_new,
                                         'form': form})


class UserEntity(BaseEntity):

    def base_new(self):
        if request.values['location']:
            form = UserForm()
            view_name = request.values['location'].split('/')[-2]
            form.department_id.data = Department.query.filter(Department.view_name==view_name).first().id
            return render_template(self.template_edit,
                                   data={'page_name': self.name_display,
                                         'add_item_url': self.entity_url_new,
                                         'form': form})
        else:
            super(UserEntity, self).base_new()

    def _prepare_base_edit(self):
        rzlt = super(UserEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])

        return rzlt

    def _prepare_base_view(self, order=None):
        order = (('name',), ('surname',), ('login',), ('department', 1))
        self.buttons = {'computer':'/hardware/new/'}
        return super(UserEntity, self)._prepare_base_view(order)

    def get_blocks(self, result):
        user_software = []
        for item in result['_base_data'].hardware_items.all():
            user_software += item.software_items.all()
        
        return {
            'Computers': result['_base_data'].computers.order_by('view_name').all(),
            'Notebooks': result['_base_data'].notebooks.order_by('view_name').all(),
            'Monitors': result['_base_data'].monitors.order_by('view_name').all(),
            'Upses': result['_base_data'].upses.order_by('view_name').all(),
            'Software': user_software
        }

    def create_name(self, base_data, model):
        return entity_uniq_name('{} {}'.format(base_data.surname,
                                               base_data.name), model)

    def _delete_data(self, base_data):
        for item in base_data.hardware_items.all():
            new_user_id = User.query.filter(
                User.did == base_data.department_id).first().id
            item.user_id = new_user_id
            db.session.add(item)
            db.session.commit()
        super(UserEntity, self)._delete_data(base_data)


class DepartmentEntity(BaseEntity):
    def _save_data(self, base_data, form):
        super(DepartmentEntity, self)._save_data(base_data, form)
        department_id = base_data.id
        if base_data.id is None:
            department_counter = db.session.query(db.func.max(Department.id)
                                                  ).scalar()
            department_id = department_counter + 1 if department_counter else 1
        department = Department.query.get(department_id)
        u = User.query.filter(User.did == department_id).first()
        h = Hardware.query.filter(Hardware.did == department_id).first()
        if not u:
            u = User(name='',
                     department_id=department_id,
                     did=department_id)
            h = Hardware(serial=department_id,
                         inum=department_id,
                         department_id=department_id,
                         did=department_id,
                         model='--department--'
                         )
        u.view_name = '--{}--'.format(department.name)
        u.surname = '--{}--'.format(department.name)
        u.login = department.name
        h.name = '--{}--'.format(department.name)
        h.view_name = '--{}--'.format(department.name)
        db.session.add(h)
        db.session.add(u)
        db.session.commit()

    def _prepare_base_edit(self):
        rzlt = super(DepartmentEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])

        return rzlt

    def _prepare_base_view(self, order=None):
        order = (('name', ),)
        return super(DepartmentEntity, self)._prepare_base_view(order)

    def get_blocks(self, result):
        user_software = []
        for item in result['_base_data'].hardware_items.all():
            user_software += item.software_items.all()

        return {
            'Users': result['_base_data'].users.order_by('view_name').all(),
            'Computers': result['_base_data'].computers.order_by('view_name').all(),
            'Notebooks': result['_base_data'].notebooks.order_by('view_name').all(),
            'Monitors': result['_base_data'].monitors.order_by('view_name').all(),
            'Upses': result['_base_data'].upses.order_by('view_name').all(),
            'Scanners': result['_base_data'].scanners.order_by('view_name').all(),
            'Printers': result['_base_data'].printers.order_by('view_name').all(),
            'Software': user_software
        }

    def _delete_data(self, base_data):
        hardware_dept = Hardware.query.filter(
            Hardware.did == base_data.id).first()
        user_dept = User.query.filter(
            User.did == base_data.id).first()
        hardware = Hardware.query.filter(
            Hardware.department_id == user_dept.department_id).filter(
            Hardware.did == None).all()
        free_software = Software.query.filter(
            Software.comp_id == hardware_dept.id).all()

        if (len(hardware) > 0 or len(free_software) > 0 or
                len(base_data.users.all()) > 0):
            flash('Department {} is not empty. Cannot delete.'.format(
                base_data.name))
        else:
            flash('Department {} was deleted'.format(base_data.name))
            db.session.delete(hardware_dept)
            db.session.delete(user_dept)
            super(DepartmentEntity, self)._delete_data(base_data)


class HardwareEntity(BaseEntity):

    def _save_data(self, base_data, form):
        user = User.query.filter(User.id == form.user_id.data).first()
        form.department_id.data = user.department_id
        super(HardwareEntity, self)._save_data(base_data, form)

    def _prepare_base_edit(self):
        rzlt = super(HardwareEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])

        return rzlt

    def _prepare_base_view(self, order=None):
        order = (('hardware_type',), ('model',), ('name',), ('inum',),
                 ('department', 1))
        return super(HardwareEntity, self)._prepare_base_view(order)

    def get_blocks(self, result):
        return {'Software': result['_base_data'].software_items.order_by('view_name').all()}

    def _delete_data(self, base_data):
        for item in base_data.software_items.all():
            item.comp_id = Hardware.query.filter(
                Hardware.did == base_data.user.department_id).first().id
            db.session.add(item)
            db.session.commit()
        super(HardwareEntity, self)._delete_data(base_data)


class SoftwareEntity(BaseEntity):

    def _prepare_base_view(self, order=None):
        order = (('name',), ('hardware', 1))
        return super(SoftwareEntity, self)._prepare_base_view(order)

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
    users = User.query.whoosh_search(query,
                                     MAX_SEARCH_RESULTS).filter(
                                     User.did == None).all()
    departments = Department.query.whoosh_search(query,
        MAX_SEARCH_RESULTS).all()
    software = Software.query.whoosh_search(query,
        MAX_SEARCH_RESULTS).all()
    hardware = Hardware.query.whoosh_search(query,
        MAX_SEARCH_RESULTS).filter(Hardware.did == None).all()
    results = [('Users', users),
               ('Departments', departments),
               ('Software', software),
               ('Hardware', hardware)]

    return render_template('search_results.html',
                           query=query,
                           results=results)


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
    print 'Im here'
    depart = DepartmentEntity('department',
                              template_edit='base_edit.html',
                              url_param=url_parameter)
    try:
        return depart.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/')
def users():
    users = UserEntity('user', template_view='base_view.html')
    return users.base_list('surname', 'self.model.did == None')


@app.route('/users/<url_parameter>/view', methods=['GET', 'POST'])
def user_view(url_parameter):
    users = UserEntity('user',
                       template_view='base_view.html',
                       url_param=url_parameter)
    try:
        return users.base_view()
    except NoEntityFoundException:
        return render_template('404.html')


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
def hardware_items():
    hard = HardwareEntity('hardware', template_edit='base_edit.html')
    return hard.base_list('view_name', 'self.model.did == None')


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
def software_items():
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

