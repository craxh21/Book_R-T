from flask import Flask,render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import json

# Determine if the app is running locally or in production
local_server = True

with open('config.json', 'r') as c:  
    params = json.load(c)["params"] 

app = Flask(__name__)
app.secret_key = 'the_random_string' 

username = "regdb"
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
  
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),  nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), nullable=False)

@app.route("/")
def index():
    return "Hello"

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if(request.method == 'POST'):
       
        email = request.form.get('uemail') 
        username = request.form.get('uname')
        password = request.form.get('upass')
    
        print("Username:", username)
        print("Email:", email)
        print("Password:", password)

        # making entry
        entry = Users(username=username, email = email, password = password)
        # adding the entry
        db.session.add(entry)
        db.session.commit()
        return "User registered successfully!"
    return render_template('login.html')

@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    return "this is dashboard"

# @app.route("/login", methods = ['GET', 'POST'])
# def login():
#     if(request.method == 'POST'):
#         #handle request
#         pass
#     return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)