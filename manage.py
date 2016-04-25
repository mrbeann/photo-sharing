#coding=utf-8
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Group, Photo
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask import render_template
from flask import render_template, redirect, request, url_for, flash,redirect,current_app
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from werkzeug import secure_filename
import os
from forms import LoginForm, RegistrationForm
import time as Time
ISOTIMEFORMAT='%Y%m%d%H%M%S'

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Group=Group, Photo=Photo)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/personal')
@login_required
def personal():
    p = Photo.query.filter_by(owner_id=current_user.id).all()
    pic_list = [(i.name,i.content,i.address) for i in p] 
    return render_template('personal.html', pic_list=pic_list) 
     
@app.route('/class')
@login_required
def classes():
    p = Photo.query.filter_by(group_id=current_user.group_id).all()
    pic_list = [(i.name,i.time,i.content,i.address) for i in p] 
    return render_template('class.html',group=Group.query.filter_by(name=current_user.group_id).first(),pic_list=pic_list)    
   
@app.route('/snapshot')
@login_required
def snapshot():
    return render_template('snapshot.html')  
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)  

@app.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))
    return render_template('register.html', form=form)  

@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html',type=request.args.get('type'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
           
@app.route('/personal/upload', methods=['GET', 'POST'])
@login_required
def personal_upload_file():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        content = request.form['content']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #filename=file.filename
            #file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            
            file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(Time.strftime(ISOTIMEFORMAT))+filename))
            from PIL import Image
            img = Image.open(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(Time.strftime(ISOTIMEFORMAT))+filename))
            img.resize((400,400), Image.ANTIALIAS).save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(Time.strftime(ISOTIMEFORMAT))+filename))
            photo = Photo(address=os.path.join('uploads/', str(Time.strftime(ISOTIMEFORMAT))+filename),
                    name=title,
                    content =  content,
                    time = None,
                    owner_id=current_user.id
                    )
            db.session.add(photo)
            db.session.commit()
            flash('upload successful!')
    p = Photo.query.filter_by(owner_id=current_user.id).all()
    pic_list = [(i.name,i.content,i.address) for i in p] 
    return render_template('personal.html', pic_list=pic_list) 
        
@app.route('/class/upload', methods=['GET', 'POST'])
@login_required
def class_upload_file():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        times = request.form['time']
        content = request.form['content']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #filename=file.filename
            #file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(Time.strftime(ISOTIMEFORMAT))+filename))
            from PIL import Image
            img = Image.open(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(Time.strftime(ISOTIMEFORMAT))+filename))
            img.resize((200,200), Image.ANTIALIAS).save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(Time.strftime(ISOTIMEFORMAT))+filename))
            
            photo = Photo(address=os.path.join('uploads/', str(Time.strftime(ISOTIMEFORMAT))+filename),
                    name=title,
                    content =  content,
                    time = times,
                    owner_id=current_user.id,
                    group_id=current_user.group_id
                    )
            db.session.add(photo)
            db.session.commit()
            flash('upload successful!')
    p = Photo.query.filter_by(group_id=current_user.group_id).all()
    pic_list = [(i.name,i.time,i.content,i.address) for i in p] 
    return render_template('class.html',group=Group.query.filter_by(name=current_user.group_id).first(),pic_list=pic_list)    
   
if __name__ == '__main__':
    manager.run()

#test account usr:1@1.com    pwd:123