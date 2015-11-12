# -*- coding: utf-8 -*-

from flask import (render_template, flash, redirect, url_for, request, g,
                   session, make_response)
from app import app, db, Server, base, Filter
from config import MAX_SEARCH_RESULTS
from models import (User, Department, Hardware, Software, Admin, History,
                    HType, HFeature, Note)
from forms import (SearchForm, UserForm, DepartmentForm, HardwareForm,
                   SoftwareForm, LoginForm, ReportForm, STATUSES)
from functools import wraps
import ldap
import md5
import re


PLURALS = {
    'user': 'users',
    'department': 'departments',
    'software': 'software_items',
    'hardware': 'hardware_items'
}

BUTTONS = {'department': {'Add user': '/users/new/',
                          'Add hardware': '/hardware/new/',
                          'Add software': '/software/new/'},
           'user': {'Add hardware': '/hardware/new/'},
           'hardware': {'Add software': '/software/new/',
                        'Add note': '#'},
           'software': {}}

Scope = ldap.SCOPE_SUBTREE


def create_csv(department):
    result = {}
    lines = []
    lines.append('{}\nName,Type,Model, Serial, INum\n'.format(department))
    h_query = HType.query.all()
    h_types = {h_type.id: h_type.name for h_type in h_query}

    for user in department.all_users:
        result[str(user)] = ['{}, {}, {}, {}'.format(
            str(h_types[item.hardware_type]),
            str(item.model), str(item.serial),
            str(item.inum))
            for item in user.hardware_items]
    users = sorted(result.keys())
    users.append(users.pop(0))

    for user in users:
        line = '{}\n,{}\n'.format(user, '\n,'.join(result[user]))
        lines.append(line)
        csv = ''.join(lines)

    return csv


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
                 template_list='base_list.html',
                 template_edit='base_edit.html',
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
        self.entity_url_view = self.name + '_view'
        self.template_list = template_list
        self.template_edit = template_edit
        self.template_view = template_view
        self.url_param = url_param

        if self.name in BUTTONS:
            self.buttons = BUTTONS[self.name]
        else:
            self.buttons = {}

        if self.url_param:
            self.entity_url_edit = url_for(self.entity_url_edit,
                                           url_parameter=self.url_param)
            self.entity_url_view = url_for(self.entity_url_view,
                                           url_parameter=self.url_param)

    def _save_data(self, base_data, form):
        changed = False
        if not hasattr(base_data, 'view_name') or self.check_changes(base_data,
                                                                     form):
            changed = True
        for a, b in form.data.items():
            setattr(base_data, a, b)
        if changed:
            base_data.view_name = self.create_name(base_data, self.model)

        db.session.add(base_data)
        db.session.commit()

    def check_changes(self, basedata, form):
        return basedata.name != form.name.data

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
                        self.model.__name__, self.url_param.encode('utf-8')))
        else:
            base_data = self.model()
        return base_data

    def _save_validated_form(self, form):
        base_data = self._get_base_data()
        if not request.values.get('submitted') == 'Cancel':
            self._save_data(base_data, form)
        if request.values.get('submitted') == 'Save & New':
            return self.entity_url_new
        elif request.values.get('submitted') == 'Delete':
            self._delete_data(base_data)
        return base_data.get_view_path()

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
                '_base_data': base_data
                })

    def _prepare_base_view(self, order=None):
        base_data = self._get_base_data()
        return ('template', self.template_view, {
            'page_name': self.name_display,
            '_base_data': base_data,
            'order': order,
            'buttons': self.buttons
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
        if ('location' in request.values and
                len(request.values['location']) > 0):
            form = UserForm()
            view_name = request.values['location'].split('/')[-2]
            form.department_id.data = Department.query.filter(
                Department.view_name == view_name).first().id
            return render_template(self.template_edit,
                                   data={'page_name': self.name_display,
                                         'add_item_url': self.entity_url_new,
                                         'form': form})
        else:
            return super(UserEntity, self).base_new()

    def _prepare_base_view(self, order=None):
        order = (('name',), ('surname',), ('login',), ('department', 1))
        rzlt = super(UserEntity, self)._prepare_base_view(order)
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])
        return rzlt

    def get_blocks(self, result):
        user_software = []
        for item in result['_base_data'].hardware_items.all():
            user_software += item.software_items.all()

        return {
            'Computers': result['_base_data'].computers.order_by(
                'view_name').all(),
            'Notebooks': result['_base_data'].notebooks.order_by(
                'view_name').all(),
            'Monitors': result['_base_data'].monitors.order_by(
                'view_name').all(),
            'Upses': result['_base_data'].upses.order_by(
                'view_name').all(),
            'Software': user_software
        }

    def create_name(self, base_data, model):
        return entity_uniq_name('{} {}'.format(base_data.surname,
                                               base_data.name), model)

    def check_changes(self, basedata, form):
        return (basedata.name != form.name.data or
                basedata.surname != form.surname.data)

    def _delete_data(self, base_data):
        self.from_user_to_department(base_data)
        base_data.is_active = False
        db.session.add(base_data)
        db.session.commit()

    def from_user_to_department(self, base_data):
        new_user_id = User.query.filter(
            User.did == base_data.department_id).first().id
        for item in base_data.hardware_items.all():
            item.user_id = new_user_id
            db.session.add(item)
        db.session.commit()

    def _save_data(self, base_data, form):
        if form.department_id.data != base_data.department_id:
            self.from_user_to_department(base_data)
        super(UserEntity, self)._save_data(base_data, form)


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

    def _prepare_base_view(self, order=None):
        order = (('name', ),)
        rzlt = super(DepartmentEntity, self)._prepare_base_view(order)
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])

        return rzlt

    def get_blocks(self, result):
        user_software = []
        for item in result['_base_data'].hardware_items.all():
            user_software += item.software_items.all()

        return {
            'Users': result['_base_data'].users.order_by('view_name').all(),
            'Computers': result['_base_data'].computers.order_by(
                'view_name').all(),
            'Notebooks': result['_base_data'].notebooks.order_by(
                'view_name').all(),
            'Monitors': result['_base_data'].monitors.order_by(
                'view_name').all(),
            'Upses': result['_base_data'].upses.order_by('view_name').all(),
            'Scanners': result['_base_data'].scanners.order_by(
                'view_name').all(),
            'Printers': result['_base_data'].printers.order_by(
                'view_name').all(),
            'Servers': result['_base_data'].servers.order_by(
                'view_name').all(),
            'VOIP': result['_base_data'].voip.order_by(
                'view_name').all(),
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
    def get_hardware_types(self):
        htypes = HType.query.all()
        htypes_dict = {}
        for ht in htypes:
            htypes_dict[int(ht.id)] = [f.name for f in ht.features]

        return htypes_dict

    def _prepare_base_edit(self):
        result = super(HardwareEntity, self)._prepare_base_edit()
        if result[0] != 'redirect':
            result = list(result)
            result[2]['hardware_types'] = self.get_hardware_types()
            result = tuple(result)
        return result

    def base_new(self):
        form = HardwareForm()
        if 'location' in request.values:
            location = request.values['location'].split('/')
            view_name = request.values['location'].split('/')[-2]

            if location[-4] == 'departments':
                form.department_id.data = Department.query.filter(
                    Department.view_name == view_name).first().id
                form.user_id.data = User.query.filter(
                    User.did == form.department_id.data).first().id
            elif location[-4] == 'users':
                form.user_id.data = User.query.filter(
                    User.view_name == view_name).first().id
                form.department_id.data = User.query.filter(
                    User.view_name == view_name).first().department_id

        return render_template(
            self.template_edit,
            data={'page_name': self.name_display,
                  'add_item_url': self.entity_url_new,
                  'form': form,
                  'hardware_types': self.get_hardware_types()
                  })

    def _save_data(self, base_data, form):
        h_id = Hardware.query.filter(Hardware.id == base_data.id).first()
        user = User.query.filter(User.id == form.user_id.data).first()
        # admin = Admin.query.filter(Admin.id == session['admin_id']).first()
        form.department_id.data = user.department_id
        if form.model.data == '':
            form.model.data = 'Noname'

        if h_id:
            if h_id.user_id != form.user_id.data:
                admin_id = session['admin_id']
                record = History(form.user_id.data, h_id.id, admin_id)

                db.session.add(record)
                db.session.commit()
            super(HardwareEntity, self)._save_data(base_data, form)
        else:
            super(HardwareEntity, self)._save_data(base_data, form)
            hardware_id = Hardware.query.order_by('id desc').first().id
            record = History(form.user_id.data, hardware_id,
                             session['admin_id'])
            db.session.add(record)
            db.session.commit()

    def _prepare_base_view(self, order=None):
        order = (('hardware_type',), ('model',), ('name',), ('inum',),
                 ('department', 1))
        rzlt = super(HardwareEntity, self)._prepare_base_view(order)
        if rzlt[0] == 'template':
            rzlt[2]['blocks'] = self.get_blocks(rzlt[2])
            h_type = rzlt[2]['_base_data'].hardware_type
            if h_type not in (1, 2):
                rzlt[2]['buttons'] = {}
        return rzlt

    def get_blocks(self, result):
        return {'Software': result['_base_data'].software_items.order_by(
            'view_name').all()}

    def _delete_data(self, base_data):
        for item in base_data.software_items.all():
            item.comp_id = Hardware.query.filter(
                Hardware.did == base_data.user.department_id).first().id
            db.session.add(item)
            db.session.commit()
        base_data.state = 0
        db.session.add(base_data)
        db.session.commit()


class SoftwareEntity(BaseEntity):
    def base_new(self):
        if 'location' in request.values:
            location = request.values['location'].split('/')
            form = SoftwareForm()
            view_name = request.values['location'].split('/')[-2]
            if location[-4] == 'departments':
                form.comp_id.data = Hardware.query.filter(
                    Hardware.did == Department.query.filter(
                        Department.view_name == view_name
                    ).first().id).first().id
                form.department_id.data = Department.query.filter(
                    Department.view_name == view_name).first().id

            elif location[-4] == 'hardware':
                form.department_id.data = Hardware.query.filter(
                    Hardware.view_name == view_name).first().department_id
                form.comp_id.data = Hardware.query.filter(
                    Hardware.view_name == view_name).first().id

            return render_template(self.template_edit,
                                   data={'page_name': self.name_display,
                                         'add_item_url': self.entity_url_new,
                                         'form': form})

        return super(SoftwareEntity, self).base_new()

    def _prepare_base_view(self, order=None):
        order = (('name',), ('hardware', 1))
        return super(SoftwareEntity, self)._prepare_base_view(order)

    def _prepare_base_edit(self):
        rzlt = super(SoftwareEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template' and hasattr(rzlt[2]['_base_data'],
                                             'hardware'):
            rzlt[2]['form'].department_id.data = rzlt[2][
                '_base_data'].hardware.department_id
        return rzlt

    def create_name(self, base_data, model):
        soft_counter = db.session.query(db.func.max(model.id)).scalar()
        soft_counter = soft_counter + 1 if soft_counter else 1

        return entity_uniq_name('software_item_{}'.format(soft_counter), model)

    def _delete_data(self, base_data):
        base_data.is_active = False
        db.session.add(base_data)
        db.session.commit()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.path != '/logout/':
            session['next_url'] = str(request.path.encode('utf-8'))
        else:
            session['next_url'] = '/index'

        if hasattr(g, 'user') and g.user:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrapper


@app.before_request
def before_request():
    if 'admin_id' in session:

        g.user = Admin.query.filter_by(id=session['admin_id']).first()
    else:
        g.user = None

    g.search_form = SearchForm()


@app.context_processor
def menu_items():
    return dict(menu_items=Department.query.order_by('name').all())


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()

        password = md5.new(form.password.data).hexdigest()
        session['admin_id'] = Admin.query.filter_by(email=email,
                                                    password=password).first()
        if session['admin_id']:
            session['admin_id'] = session['admin_id'].id
            session['next_url'] = '/index'
            return redirect(session['next_url'])

        try:
            l = ldap.initialize(Server)
            l.simple_bind_s(email, form.password.data)
            l.set_option(ldap.OPT_REFERRALS, 0)

            r = l.search(base, Scope, Filter.format(email), ["displayName"])
            Type, user = l.result(r, 60)
            Name, Attrs = user[0]
            if 'displayName' in Attrs:
                displayName = Attrs['displayName'][0]
                admin = Admin.query.filter_by(email=email).first()
                if not admin:
                    admin = Admin()
                    admin.email = form.email.data
                    admin.name = admin.email.split('.')[0].capitalize()
                    admin.surname = admin.email.split(
                        '.')[1].capitalize().split('@')[0]
                admin.password = password
                db.session.add(admin)
                db.session.commit()

                session['admin_id'] = admin.id
                return redirect(url_for('index'))

        except ldap.INVALID_CREDENTIALS:
            flash('Login or password error')
        except ldap.LDAPError, e:
            flash('LDAP-server error', e)
    return render_template('login.html',
                           title='Sign in',
                           form=form)


@app.route('/logout/')
@login_required
def logout():
    g.user = None
    session['admin_id'] = None
    return redirect(session['next_url'])


@app.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
def search_results(query):
    users = User.query.whoosh_search(
        query,
        MAX_SEARCH_RESULTS).filter(
        User.did == None).all()
    departments = Department.query.whoosh_search(
        query,
        MAX_SEARCH_RESULTS).all()
    software = Software.query.whoosh_search(
        query,
        MAX_SEARCH_RESULTS).all()
    hardware = Hardware.query.whoosh_search(
        query,
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
@login_required
def index():
    return render_template('index.html')


@app.route('/users/disabled/')
@login_required
def disabled_users():
    base_data = User.query.filter(User.is_active != 1).order_by(
        User.view_name).all()
    return render_template("base_list.html",
                           base_data=base_data,
                           page_name="Disabled users")


@app.route('/hardware/disabled/')
@login_required
def disabled_hardware():
    base_data = Hardware.query.filter(Hardware.state != 1
                                      ).order_by('name').all()
    return render_template("base_list.html",
                           base_data=base_data,
                           page_name="Disabled")


@app.route('/hardware/disabled/computers/')
@login_required
def disabled_computers():
    type_comp = HType.query.filter(HType.name == 'Desktop').first().id
    type_nbk = HType.query.filter(HType.name == 'Notebook').first().id
    base_data = Hardware.query.filter((Hardware.state != 1) & (
        (Hardware.hardware_type == type_comp) |
        (Hardware.hardware_type == type_nbk))
    ).order_by('name').all()
    return render_template("base_list.html",
                           base_data=base_data,
                           page_name="Disabled computers")


@app.route('/hardware/disabled/monitors/')
@login_required
def disabled_monitors():
    type_mon = HType.query.filter(HType.name == 'Monitor').first().id
    base_data = Hardware.query.filter(
        (Hardware.state != 1) & (Hardware.hardware_type == type_mon)
    ).order_by('name').all()
    return render_template("base_list.html",
                           base_data=base_data,
                           page_name="Disabled computers")


@app.route('/departments/')
@login_required
def departments():
    depart = BaseEntity('department', template_edit='base_edit.html')
    return depart.base_list()


@app.route('/departments/new/', methods=['GET', 'POST'])
@login_required
def department_new():
    depart = DepartmentEntity('department')
    return depart.base_new()


@app.route('/departments/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def department_edit(url_parameter):
    depart = DepartmentEntity('department',
                              template_edit='base_edit.html',
                              url_param=url_parameter)
    try:
        return depart.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/departments/view/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def department_view(url_parameter):
    depart = DepartmentEntity('department',
                              url_param=url_parameter)
    try:
        return depart.base_view()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/')
@login_required
def users():
    users = UserEntity('user')
    return users.base_list(
        'surname',
        '(self.model.did == None) & (self.model.is_active == 1)')


@app.route('/users/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def user_edit(url_parameter):
    users = UserEntity('user',
                       template_edit='base_edit.html',
                       url_param=url_parameter)
    try:
        return users.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/view/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def user_view(url_parameter):
    users = UserEntity('user',
                       url_param=url_parameter)
    try:
        return users.base_view()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/new/', methods=['GET', 'POST'])
@login_required
def user_new():
    users = UserEntity('user')
    return users.base_new()


@app.route('/hardware/')
@login_required
def hardware_items():
    hard = HardwareEntity('hardware', template_edit='base_edit.html')
    return hard.base_list(
        'view_name',
        '(self.model.did == None) & (self.model.state == 1)')


@app.route('/hardware/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def hardware_edit(url_parameter):
    hard = HardwareEntity('hardware',
                          template_edit='base_edit.html',
                          url_param=url_parameter)
    try:
        return hard.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/hardware/view/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def hardware_view(url_parameter):
    hard = HardwareEntity('hardware', url_param=url_parameter)
    try:
        return hard.base_view()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/hardware/new/', methods=['GET', 'POST'])
@login_required
def hardware_new():
    hard = HardwareEntity('hardware')
    return hard.base_new()


@app.route('/software/')
@login_required
def software_items():
    soft = SoftwareEntity('software')
    return soft.base_list('name')


@app.route('/software/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def software_edit(url_parameter):
    soft = SoftwareEntity('software', url_param=url_parameter)
    try:
        return soft.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/software/view/<url_parameter>/', methods=['GET', 'POST'])
@login_required
def software_view(url_parameter):
    soft = SoftwareEntity('software', url_param=url_parameter)
    try:
        return soft.base_view()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/software/new/', methods=['GET', 'POST'])
@login_required
def software_new():
    soft = SoftwareEntity('software')
    return soft.base_new()


@app.route('/reports/', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportForm()
    if form.validate_on_submit():
        if form.department.data != 100:
            department = Department.query.filter(Department.id ==
                                                 form.department.data).first()
            csv = create_csv(department)
        else:
            csv = '\n'.join(sorted([create_csv(department)
                            for department in Department.query.all()]))
        response = make_response(csv)
        response.headers[
            'Content-Disposition'] = "attachment; filename=report.csv"
        return response

    return render_template('reports.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
