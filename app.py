from flask import Flask,render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import json

# Determine if the app is running locally or in production
local_server = True

with open('config.json', 'r') as c:  
    params = json.load(c)["params"] 

app = Flask(__name__)
 # Secret key for securing sessions
app.secret_key = 'the_random_string' 

app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
  
  # Initialize SQLAlchemy for the Flask app
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

        # Hash the password
        hashed_password = generate_password_hash(password)

        # check if user exists
        exixting_user = Users.query.filter_by(email = email).first()
        if(exixting_user):
            return "Email already reg. Please login."

        # Create a new user entry for the database
        entry = Users(username=username, email = email, password = hashed_password)
        # Add and commit the new user to the database
        db.session.add(entry)
        db.session.commit()
        # Set session for the logged-in user, with username 
        session['user'] = username
        # Redirect to the dashboard
        return redirect(url_for('dashboard'))

    return render_template('login.html')  #url_for('login') translates the endpoint name (the function name in your code) to its corresponding URL path.

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        username = request.form.get('uname')
        password = request.form.get('upass')

        # Query the database for the user
        user = Users.query.filter_by(username = username).first()

        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):  # Replace with hashed password check later
            # Set session for the logged-in user
            session['user'] = user.username

            # Redirect to the dashboard
            return redirect(url_for('dashboard'))
        else:
            # Invalid credentials
            return "Invalid username or password. Please try again."
        
    return render_template('login.html')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session:  # Check if user is logged in
        username = session['user']
        return render_template('dashboard.html', username=username)

    # If no user is logged in, redirect to login page
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    session.pop('user', None)# Clear the session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)