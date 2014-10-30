#-*-coding: utf-8-*-

from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from models import Owner, Compware
from forms import UserForm, CompwareForm, DepartmentForm, STATUS_INUSE, STATUS_FREE
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
    cnt = model.filter(model.name_en==name_en).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = model.filter(model.name_en=='{}_{}'.format(name_en, i)).count()
        rzlt = '{}_{}'.format(name_en, i)
    else:
        rzlt = name_en
    return rzlt


class NoEntityFoundException(Exception):
    """When we colud not find entity item in the base
    during attempt to edit it"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# class should be a child of object 'object' to work with 'super' func

class BaseEntity(object):
    """ Entity model should have fields name and name_en. 
    Second one is used for generating url"""

    def __init__(self, entity_name, display_name=None, url_param=None, 
                 template_list=None, model=None, uniq_name=None,
                 template_edit=None, entity_form=None, query=None):

        self.name = entity_name.lower()
        self.display_name = display_name if display_name is not None \
                                         else entity_name.capitalize()
        self.model = model if model is not None \
                           else globals()[self.display_name]
        self.query = query if query is not None \
                           else self.model.query
        self.form = entity_form if entity_form is not None \
                                else globals()[self.display_name + 'Form']
        self.entity_url = url_for(self.name + 's')
        self.entity_url_new = url_for(self.name + '_new')
        self.entity_url_edit = self.name + '_edit'
        self.template_list = template_list if template_list is not None \
                                           else 'base_list.html'
        self.template_edit = template_edit if template_edit is not None \
                                           else 'base_edit.html'
        self.url_param = url_param
        self.uniq_name = uniq_name if uniq_name is not None else 'name'
        if self.url_param:
            self.entity_url_edit = url_for(self.entity_url_edit, 
                                           url_parameter = self.url_param)
     

    def _save_data(self, base_data, form):
        for a,b in form.data.items():
            setattr(base_data, a,b)
        # if base_data.name_en is None:
        #     base_data.name_en = self.create_name(base_data, self.model)
        db.session.add(base_data)
        db.session.commit()


    def create_name(self, base_data, model):
        return entity_uniq_name(base_data.name, model)

    def _get_base_data(self):
        if self.url_param is not None:
            base_data = self.query.filter(
                    getattr(self.model, self.uniq_name)==self.url_param).first()
            if base_data is None:
                raise NoEntityFoundException(
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
                'page_name':self.display_name,
                'add_item_url':self.entity_url_new,
                'form':form,
                '_base_data':base_data
            })


    def base_list(self, sort_field = 'name'):
        """generates list of entites. If the list is empty - returns new form
        to input new data"""
        cnt = self.query.count()
        if cnt == 0:
            return redirect(self.entity_url_new)
        base_data = self.query.order_by(sort_field).all()
        return render_template(self.template_list,
                base_data=base_data,
                page_name=self.display_name,
                add_item_url=self.entity_url_new)



    def base_edit(self):
        rzlt = self._prepare_base_edit()
        if rzlt[0] == 'redirect':
            return redirect(rzlt[1])
        return render_template(rzlt[1], data=rzlt[2])


    def base_new(self):
        form = self.form()
        print '========================='
        print request.values
        print form
        print dir(form)
        print form.data
        print form.errors
        if form.validate_on_submit():
            return redirect(self._save_validated_form(form))
        else:
            return render_template(self.template_edit,
                data={'page_name':self.display_name,
                    'add_item_url':self.entity_url_new,
                    'form':form})


class UserEntity(BaseEntity):

    def __init__(self,url_param=None):
        template_edit='user_edit.html'
        query = Owner.query.filter(Owner.parent_id != None)
        super(UserEntity, self).__init__('user',
                model=Owner, query=query, uniq_name='login',
                url_param=url_param, template_edit=template_edit)

    def _save_electronic_items(self, el_items, status):
        n = len(el_items)
        if n != len(status): return False
        for i in range(len(el_items)):
            print el_items[i]


    def _prepare_base_edit(self):
        self._save_electronic_items(
            request.values.getlist('electronic_item'),
            request.values.getlist('status'))
        rzlt = super(UserEntity, self)._prepare_base_edit()
        if rzlt[0] == 'template':
            rzlt[2]['hard_free_in_depart'] = Compware.query.filter(
                    Compware.owner_id == rzlt[2]['_base_data'].parent_id,
                    Compware.state == STATUS_FREE).all()
            rzlt[2]['hard_free'] = Compware.query.filter(
                    Compware.owner_id != rzlt[2]['_base_data'].parent_id,
                    Compware.state == STATUS_FREE).all()
            rzlt[2]['soft_free'] = Compware.query.filter(
                    Compware.state == STATUS_FREE
                    #! on free comps
                    )
        return rzlt
    

    def _save_validated_form(self, form):
        base_data = self._get_base_data()
        self._save_data(base_data, form)
        if request.values.get('submited') == 'Save & new':
            return self.entity_url_new
        else:
            return self.entity_url

        
    def create_name(self, base_data, model):
        return entity_uniq_name('{} {}'.format(base_data.surname, base_data.name), model)


class DepartmentEntity(BaseEntity):

    def __init__(self,url_param=None):
        query = Owner.query.filter(Owner.parent_id == None)
        super(DepartmentEntity, self).__init__('department',
                model=Owner, query=query, uniq_name='login',
                url_param=url_param)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/departments/')
def departments():
    depart = DepartmentEntity()
    return depart.base_list()


@app.route('/departments/new/', methods=['GET', 'POST'])
def department_new():
    depart = DepartmentEntity()
    return depart.base_new()


@app.route('/departments/<url_parameter>/', methods=['GET', 'POST'])
def department_edit(url_parameter):
    depart = DepartmentEntity(url_param=url_parameter)
    try:
        return depart.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')

    

@app.route('/users/')
def users():
    users = UserEntity()
    return users.base_list('surname')

@app.route('/users/<url_parameter>/', methods=['GET', 'POST'])
def user_edit(url_parameter):
    users = UserEntity(url_param=url_parameter)
    try:
        return users.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/users/new/', methods=['GET', 'POST'])
def user_new():
    users = UserEntity()
    return users.base_new()
 
@app.route('/compwares/')
def compwares():
    hard = BaseEntity('compware')
    return hard.base_list('name')

@app.route('/compwares/<url_parameter>/', methods=['GET', 'POST'])
def compware_edit(url_parameter):

    hard = BaseEntity('compware', url_param=url_parameter)
    try:
        return hard.base_edit()
    except NoEntityFoundException:
        return render_template('404.html')


@app.route('/compwares/new/', methods=['GET', 'POST'])
def compware_new():
    hard = BaseEntity('compware')
    return hard.base_new()
 
 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
