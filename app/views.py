from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from forms import UserForm, DepartmentForm, HardwareForm, SoftwareForm
from models import User, Department, Hardware, Software
from translit import transliterate

def department_uniq_name(name):
    """Creates uniq name_en for department:
    transliterates name and if such name_en exists in database
    adds underline and first free number
    """
    name_en = transliterate(name)
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


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/departments/')
def departments():
    cnt = Department.query.count()
    if cnt == 0:
        return redirect('/departments/new/')
    departments = Department.query.all()
    return render_template('departments.html',
        dep = departments)

@app.route('/departments/<department>/', methods=['GET', 'POST'])
def department(department):
    dep_form = DepartmentForm()
    if dep_form.validate_on_submit():
        dep_obj = Department.query.filter(Department.name_en==department).first()
        if dep_obj is None:
            pass
        dep_obj.name = dep_form.name.data
        if db.session.is_modified(dep_obj):
            db.session.commit()    
        return redirect('/departments/{}'.format(dep_obj.name_en))

    _dept = Department.query.filter(Department.name_en==department).first()
    if _dept is None:
        pass
    dep_form = DepartmentForm(obj=_dept)
    return render_template('department_edit.html', data=dep_form)


@app.route('/departments/new/', methods=['GET', 'POST'])
def department_new():
    dep_form = DepartmentForm()
    if dep_form.validate_on_submit():
        dep_obj = Department(
                name=dep_form.name.data,
                name_en=department_uniq_name(dep_form.name.data))
        db.session.add(dep_obj)
        db.session.commit()
        return redirect('/departments/{}'.format(dep_obj.name_en))
    else:
        dep_form = DepartmentForm()
        return render_template('department_edit.html', data=dep_form)

    
