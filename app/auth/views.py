#coding=utf-8
from flask import render_template, redirect, request, url_for, flash,redirect,current_app
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from werkzeug import secure_filename
from . import auth
from .. import db
from ..models import User, Photo, Group
from .forms import LoginForm, RegistrationForm
import os

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    group_id=form.group.data)
        if Group.query.filter_by(name=form.group.data).first() is None:
            group = Group(name=form.group.data)
            db.session.add(group)
        else:
            pass
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

    

@auth.route('/<name>')
@login_required
def display_wall(name):
    p = Photo.query.filter_by(owner_id=current_user.id).all()
    pic_list = [i.address for i in p] 
    return render_template('auth/wall.html',name=current_user, 
    pic_list=pic_list)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
               
@auth.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #filename=file.filename
            #file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename))
            photo = Photo(address=os.path.join('/static/uploads/', filename),
                    name=file.filename,
                    owner_id=current_user.id
                    )
            db.session.add(photo)
            db.session.commit()
            flash('upload successful!')
    return render_template('auth/wall.html',name=current_user)
            #return redirect(url_for('uploaded_file',filename=filename))

@auth.route('/group', methods=['GET', 'POST'])
@login_required
def show_group():
    p = Photo.query.filter_by(group_id=current_user.group_id).all()
    pic_list = [i.address for i in p] 
    #print Group.query.filter_by(name=current_user.group_id).first()
    # notice here i use group name for id just for convience we need to improve it
    return render_template('auth/wall-g.html',
    group=Group.query.filter_by(name=current_user.group_id).first(), 
    pic_list=pic_list)
    
@auth.route('/uploadg', methods=['GET', 'POST'])
@login_required
def uploadg_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #filename=file.filename
            #file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename))
            
            photo = Photo(address=os.path.join('/static/uploads/', filename),
                    name=file.filename,
                    owner_id=current_user.id,
                    group_id=current_user.group_id
                    )
            db.session.add(photo)
            db.session.commit()
            flash('upload successful!')
    return render_template('auth/wall-g.html',
    group=Group.query.filter_by(name=current_user.group_id).first())
            #return redirect(url_for('uploaded_file',filename=filename))
                                 