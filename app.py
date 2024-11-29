from flask import Flask,render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests ##to make HTTP requests to the API.

import json
from datetime import datetime  # Ensure datetime import for timestamp handling

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
    email = db.Column(db.String(100),unique= True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)

class UserBooks(db.Model):
    __tablename__ = 'userbooks'  # Match the table name in your database
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    start_date = db.Column(db.Date)
    status = db.Column(db.Enum('completed', 'reading'))
    bookmark_page_no = db.Column(db.Integer)
    last_read_datetime = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    # Define the relationship to the Books model
    book = db.relationship('Books', backref='user_books')

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
        session['user_id'] = entry.id
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
            session['user_id'] = user.id
            session['user'] = user.username

            # Redirect to the dashboard
            return redirect(url_for('dashboard'))
        else:
            # Invalid credentials
            return "Invalid username or password. Please try again."
        
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('user', None)# Clear the session
    return redirect(url_for('login'))

@app.route("/recommendByGenres", methods=['GET', 'POST'])
def recommendByGenres():
    # Ensure that the user is logged in before proceeding
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        genres = request.form.get('genres')  # User input
        genre_list = [genre.strip() for genre in genres.split(',')]  # Split genres

        # Initialize a list to hold recommended books
        all_books = []

        # # Loop through each genre and fetch books from the API
        for genre in genre_list:
            query_type = "subject:" #as per google api
            search_input = genre
            # Construct the query parameter
            query = f"{query_type}{search_input}"
            
            # Make an API call to get books related to the current genre
            response = requests.get(
                params['api_link'],
                params={"q": query, "key": params['api_key']} # Pass query and API key
            )
            if response.status_code == 200:# Check if the API request was successful
                data = response.json()
                # Parse and add books to the list
                books = [ # Extract relevant book details (title, author, and genre/category)
                    {
                        "title": item['volumeInfo']['title'],
                        "author": item['volumeInfo'].get('authors', ['Unknown'])[0],
                        "genre": ", ".join(item['volumeInfo'].get('categories', ['N/A'])),
                        "description": item['volumeInfo'].get('description', 'No description available'),
                        "thumbnail": item['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
                    }
                    for item in data.get('items', [])# Iterate over books in the response
                ]
                all_books.extend(books)  # Add the current genre's books to the overall list of recommendations

        # Remove duplicate books based on title
        unique_books = {book['title']: book for book in all_books}.values()

        return render_template('recommendations.html', books=unique_books)

    return render_template('recommend_form.html')

@app.route("/recommendByTitleOrAuthor", methods=['GET', 'POST'])
def recommendByTitleOrAuthor():
    # Ensure that the user is logged in before proceeding
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_input = request.form.get('search_input')  # User input
        
        # Determine whether the input is a title or an author
        query_type = "intitle:" if request.form.get('search_type') == "title" else "inauthor:"

        # Construct the query parameter
        query = f"{query_type}{search_input}"

        response = requests.get(
                params['api_link'],
                params={"q": query, "key": params['api_key']} # Pass query and API key
            )
        
        if response.status_code == 200:# Check if the API request was successful
            data = response.json()
            # Parse and add books to the list
            all_books = [ # Extract relevant book details (title, author, and genre/category)
                {
                    "title": item['volumeInfo']['title'],
                    "author": item['volumeInfo'].get('authors', ['Unknown'])[0],
                    "genre": ", ".join(item['volumeInfo'].get('categories', ['N/A'])),
                    "description": item['volumeInfo'].get('description', 'No description available'),
                    "thumbnail": item['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
                }
                for item in data.get('items', [])# Iterate over books in the response
            ]
            # here all the books fetched are unique only
            # as the search is using title or author and not by genres
            return render_template('recommendations.html', books=all_books)

        return "Error fetching data from the API. Please try again."

    return render_template('recommend_form.html')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    username = session['user']
    user_books = UserBooks.query.filter_by(user_id=user_id).all()

    # Format the book data to pass to the template
    books = [
        {
            "title": user_book.book.title,  # Access the related book's name
            "author": user_book.book.author,  # Access the related book's author
            "start_date": user_book.start_date,
            "status": user_book.status,
            "bookmark_page_no": user_book.bookmark_page_no,
            "last_read_datetime": user_book.last_read_datetime,
            "notes": user_book.notes,
        }
        for user_book in user_books
    ]

    return render_template('dashboard.html', books = books, username=username)

@app.route("/addBook", methods = ['POST', 'GET'])
def addBook():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if(request.method == 'POST'):
        title = request.form.get('title')
        author = request.form.get('author')

        # Check if the book already exists in the Books table
        book = Books.query.filter_by(title=title, author=author).first()

        if not book:
            book = Books(title = title, author = author)
            db.session.add(book)
            db.session.commit()

         # Retrieve the book_id from the Books table
        book_id = book.id

        # Check if the user already has this book in their dashboard
        user_id = session['user_id']
        user_book = UserBooks.query.filter_by(user_id=user_id, book_id=book_id).first()
        if not user_book:
            # add entry in the USerBooks table
            user_book = UserBooks(user_id=user_id, book_id=book_id, start_date=datetime.now())
            db.session.add(user_book)
            db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_book.html')

if __name__ == '__main__':
    app.run(debug=True)