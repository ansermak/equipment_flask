#-*-coding: utf-8-*-

from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from forms import UserForm, DepartmentForm, HardwareForm, SoftwareForm
from models import User, Department, Hardware, Software
import re

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


def department_uniq_name(name):
    """Creates uniq name_en for department:
    transliterates name and if such name_en exists in database
    adds underline and first free number
    """
    name_en = replace_other_chars(name)
    cnt = Department.query.filter(Department.name_en==name_en).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = Department.query.filter(Department.name_en=='{}_{}'.format(name_en, i)).count()
        rzlt = '{}_{}'.format(name_en, i)
    else:
        rzlt = name_en
    return rzlt

def prepare_base_object(base_obj):
    base_url = url_for(base_obj['func_list'])
    base_url_new = url_for(base_obj['func_new'])
    base_obj['base_url'] = base_url
    base_obj['base_url_new'] = base_url_new
    if 'url_parameter' in base_obj:
        base_obj['base_url_edit'] = url_for(base_obj['func_edit'], 
                url_parameter=base_obj['url_parameter'])
        

def base_list(base_obj):
    prepare_base_object(base_obj)
    cnt = base_obj['model'].query.count()
    if cnt == 0:
        return redirect(base_obj['base_url_new'])
    base_data = base_obj['model'].query.all()
    return render_template(base_obj.get('template_list', 'base_list.html'),
            base_data=base_data,
            page_name=base_obj['name'],
            add_item_url=base_obj['base_url_new'])

def base_edit(base_obj):
    prepare_base_object(base_obj)
    base_form = base_obj['base_form']()
    if base_form.validate_on_submit():
        base_data_obj = base_obj['model'].query.filter(
                base_obj['model'].name_en==base_obj['url_parameter']).first()
        if base_data_obj is None:
            pass
        for a,b in base_form.data.items():
            attr = getattr(base_data_obj, a, None)
            if attr:
                setattr(base_data_obj, a, b)
        if db.session.is_modified(base_data_obj):
            db.session.commit()    

        if request.values.get('submited') == 'Save & continue editing':
            return redirect(base_obj['base_url_edit'])
        else:
            return redirect(base_obj['base_url'])

    base_data_obj = base_obj['model'].query.filter(
        base_obj['model'].name_en==base_obj['url_parameter']).first()
    if base_data_obj is None:
        pass
    base_form = base_obj['base_form'](obj=base_data_obj)
    return render_template(base_obj.get('template_edit', 'base_edit.html'),
            page_name=base_obj['name'],
            add_item_url=base_obj['base_url_new'],
            data=base_form)

def base_new(base_obj):
    prepare_base_object(base_obj)
    base_form = base_obj['base_form']()
    if base_form.validate_on_submit():
        base_data_obj = base_obj['model']()
        for a,b in base_form.data.items():
            setattr(base_data_obj, a, b)
        base_data_obj.name_en = replace_other_chars(base_data_obj.name)
        db.session.add(base_data_obj)
        db.session.commit()
        if request.values.get('submited') == 'Save & continue editing':
            print base_obj['func_edit'], base_data_obj.name, base_data_obj.name_en
            return redirect(url_for(base_obj['func_edit'], 
                url_parameter=base_data_obj.name_en))
        else:
            return redirect(base_obj['base_url'])
    else:
        base_form = base_obj['base_form']()
        return render_template(base_obj.get('template_edit', 'base_edit.html'),
            page_name=base_obj['name'],
            add_item_url=base_obj['base_url_new'],
            data=base_form)



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/departments/')
def departments():
    dep_obj = {'model' : Department,
                'func_list' : 'departments', #function name
                'func_new' : 'department_new', #function name
                'name': 'Department'}
    return base_list(dep_obj)


@app.route('/departments/<url_parameter>/', methods=['GET', 'POST'])
def department(url_parameter):
    dep_obj = {'model' : Department,
                'base_form': DepartmentForm,
                'url_parameter': url_parameter,
                'func_list' : 'departments', #function name
                'func_new' : 'department_new', #function name
                'func_edit' : 'department',
                'name': 'Department'}
    
    return base_edit(dep_obj)


@app.route('/departments/new/', methods=['GET', 'POST'])
def department_new():
    dep_obj = {'model' : Department,
                'base_form': DepartmentForm,
                'func_list' : 'departments', #function name
                'func_new' : 'department_new', #function name
                'func_edit' : 'department',
                'name': 'Department'}

    return base_new(dep_obj)
    
