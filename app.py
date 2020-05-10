from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user
import hashlib
from data.departments import Departments
from data.jobs import Jobs

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    Repeat_password = PasswordField('Пароль', validators=[DataRequired()])
    surname = StringField('surname', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    age = StringField('age', validators=[DataRequired()])
    position = StringField('position', validators=[DataRequired()])
    speciality = StringField('speciality', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm, UserMixin):
    email = EmailField('Email')
    password = PasswordField('Пароль')
    submit = SubmitField('Вход')
    regist = SubmitField('Регистрация')


class Department(FlaskForm, UserMixin):
    title = StringField('Title of department', validators=[DataRequired()])
    chief = StringField('Chief', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Department Email')
    submit = SubmitField('add')


class JobForm(FlaskForm):
    job_title = StringField('Title job', validators=[DataRequired()])
    team_leader = StringField('team_leader', validators=[DataRequired()])
    work_size = StringField('work_size', validators=[DataRequired()])
    collaborators = StringField('collaborators', validators=[DataRequired()])
    remember_me = BooleanField('is job finished?')
    submit = SubmitField('add')


class Edit_Form(FlaskForm):
    job_title = StringField('Title job', validators=[DataRequired()])
    team_leader = StringField('team_leader', validators=[DataRequired()])
    work_size = StringField('work_size', validators=[DataRequired()])
    collaborators = StringField('collaborators', validators=[DataRequired()])
    remember_me = BooleanField('is job finished?')
    submit = SubmitField('edit')


class Edit_Department(FlaskForm):
    title = StringField('Title of department', validators=[DataRequired()])
    chief = StringField('Chief', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Department Email')
    submit = SubmitField('edit')


@app.route('/delete_department/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    db_session.global_init("db/mars_explorer.sqlite")
    session = db_session.create_session()
    for depart in session.query(Departments).filter(Departments.id == id):
        if current_user.surname + " " + current_user.name == depart.chief or current_user.id == 1:
            session.delete(depart)
            session.commit()
    return redirect('/department')


@app.route('/delete_job/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_job(id):
    db_session.global_init("db/mars_explorer.sqlite")
    session = db_session.create_session()
    for job in session.query(Jobs).filter(Jobs.id == id):
        if current_user.id == job.team_leader or current_user.id == 1:
            session.delete(job)
            session.commit()
    return redirect('/')


@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
def edit_department(id):
    form = Edit_Department()
    if request.method == "POST":
        if form.submit.data:
            session = db_session.create_session()
            for dep in session.query(Departments).filter(Departments.id == id):
                if current_user.surname + " " + current_user.name == dep.chief or current_user.id == 1:
                    dep.title = form.title.data
                    dep.chief = form.chief.data
                    dep.members = form.members.data
                    dep.email = form.email.data
                    session.commit()
                    return redirect('/department')
    return render_template('editdepartment.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def log():
    form = LoginForm()
    if request.method == "POST":
        if form.regist.data:
            return redirect('/register')
        if form.submit.data:
            db_session.global_init("db/mars_explorer.sqlite")
            session = db_session.create_session()
            for user in session.query(User).all():
                if hashlib.md5(
                        str(form.password.data).encode(
                            'utf-8')).hexdigest() == user.hashed_password and form.email.data == \
                        user.email:
                    login_user(user, remember=form.submit.data)
                    return redirect('/')
    return render_template('vhod.html', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
def addjob():
    form = JobForm()
    if request.method == "POST":
        if form.submit.data:
            db_session.global_init("db/mars_explorer.sqlite")
            session = db_session.create_session()
            job = Jobs()
            job.team_leader = form.team_leader.data
            job.job = form.job_title.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            if form.remember_me.data:
                job.is_finished = 1
            else:
                job.is_finished = 0
            session.add(job)
            session.commit()
            return redirect('/')
    return render_template('/addjob.html', form=form)


@app.route('/adddepartment', methods=['GET', 'POST'])
def adddepartment():
    form = Department()
    if request.method == "POST":
        if form.submit.data:
            db_session.global_init("db/mars_explorer.sqlite")
            session = db_session.create_session()
            dep = Departments()
            dep.title = form.title.data
            dep.chief = form.chief.data
            dep.members = form.members.data
            dep.email = form.email.data
            session.add(dep)
            session.commit()
            return redirect('/department')
    return render_template('adddepart.html', form=form)


@app.route('/')
def login():
    db_session.global_init("db/mars_explorer.sqlite")
    session = db_session.create_session()
    vse = list()
    new = list()
    for job in session.query(Jobs).all():
        team_ledaer = job.team_leader
        rabota = job.job
        duration = job.work_size
        colob = job.collaborators
        end = job.is_finished
        idishnik = job.id
        for user in session.query(User).all():
            if int(user.id) == int(team_ledaer):
                z = user.name + " " + user.surname
                vse.append(rabota)
                vse.append(z)
                vse.append(str(duration) + " hours")
                vse.append(colob)
                vse.append(job.hazard_category)
                vse.append(end)
                vse.append(idishnik)
                d = vse.copy()
                new.append(d)
                vse.clear()
    return render_template('osn.html', param=new)


@app.route('/department')
def department():
    db_session.global_init("db/mars_explorer.sqlite")
    session = db_session.create_session()
    vse = list()
    new = list()
    for dep in session.query(Departments).all():
        title = dep.title
        chief = dep.chief
        members = dep.members
        email = dep.email
        vse.append(title)
        vse.append(chief)
        vse.append(members)
        vse.append(email)
        vse.append(dep.id)
        d = vse.copy()
        new.append(d)
        vse.clear()
    return render_template('departament.html', param=new)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        pasword = request.form.get('password')
        Repeat_password = request.form.get('Repeat_password')
        surname = request.form.get('surname')
        name = request.form.get('name')
        age = request.form.get('age')
        position = request.form.get('position')
        speciality = request.form.get('speciality')
        address = request.form.get('address')
        if pasword == Repeat_password:
            user = User()
            user.name = name
            user.surname = surname
            user.email = email
            user.age = age
            user.position = position
            user.speciality = speciality
            user.address = address
            user.hashed_password = hashlib.md5(pasword.encode('utf-8')).hexdigest()
            db_session.global_init("db/mars_explorer.sqlite")
            session = db_session.create_session()
            count = 0
            for user in session.query(User).filter(User.email == email):
                count += 1
            if count == 0:
                session.add(user)
                session.commit()
                return redirect('/login')
            else:
                return "Вы допустили ошибку"
        else:
            return "Пароли не совпадают"
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
    app.run(port=8080, host='127.0.0.1')
