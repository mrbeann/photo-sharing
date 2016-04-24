from flask import render_template
from __init__ import app

@app.route('/')
def index():
    return render_template('/index.html')
    
@app.route('/personal')
def personal():
    return render_template('/personal.html')
