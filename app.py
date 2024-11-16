from flask import Flask,render_template

app = Flask(__name__)

@app.route('/<user>/<u2>')
def home(user,u2):
    return f"hello {user} and {u2}"

@app.route('/login')
def login():
    return render_template("login.html")

app.run(debug=True)