from flask import Flask,render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy

import json

local_server = True

with open('config.json', 'r') as c:  
    params = json.load(c)["params"] 

app = Flask(__name__)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:  #else to the production uri
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']

db = SQLAlchemy(app)



# class Users(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80),  nullable=False)
#     email = db.Column(db.String(20), nullable=False)
#     password = db.Column(db.String(13),nullable=False)
    

@app.route('/<user>/<u2>')
def home(user,u2):
    return f"hello {user} and {u2}"

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if('user' in session):
        return render_template("login.html")

    return render_template('login.html', params= params)


app.run(debug=True)