from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from forms import UserForm, DepartmentForm, HardwareForm, SoftwareForm
from models import User, Department, Hardware, Software

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/departments')
def departments():
	cnt = Department.query.count()
	if cnt == 0:
		return redirect('/departments/new')
	departments = Department.query.all()
	return render_template('departments.html',
		dep = departments)


@app.route('/departments/<department>', methods=['GET', 'POST'])
def department(department):
	dep_form = DepartmentForm()
	if dep_form.validate_on_submit():
		if department != 'new':
			dep_obj = Department.query.filter(Department.name==department).first()
			if dep_obj is None:
				pass
			if dep_obj.name != dep_form.name.data:
				dep_obj.name = dep_form.name.data
		else:
			dep_obj = Department(name=dep_form.name.data)
			db.session.add(dep_obj)
		db.session.commit()	
		return redirect('/departments/{}'.format(dep_obj.name))


	if department != 'new':
		_dept = Department.query.filter(Department.name==department).first()
		if _dept is None:
			pass
		dep_form = DepartmentForm(obj=_dept)
	else:
		dep_form = DepartmentForm()
	return render_template('department_edit.html', data=dep_form)