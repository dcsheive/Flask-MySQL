from flask import Flask, render_template, request,session, redirect, flash
from flask_bcrypt import Bcrypt
# import the function connectToMySQL from the file mysqlconnection.py
from mysqlconnection import connectToMySQL
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'KeepItSecretKeepItSafe'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# invoke the connectToMySQL function and pass it the name of the database we're using
# connectToMySQL returns an instance of MySQLConnection, which we will store in the variable 'mysql'
mysql = connectToMySQL('friendsdb')
# now, we may invoke the query_db method
@app.route('/')
def index():
    if 'login' not in session:
        session['login'] = 0
    if 'first_name' not in session:
        session['first_name'] = ""
    if 'last_name' not in session:
        session['last_name'] = ""
    if 'email' not in session:
        session['email'] = ""
    return render_template("index.html", name1 = session['first_name'], name2 = session['last_name'], email = session['email'], login = session['login'])
@app.route('/register', methods=['POST'])
def create():
    all_emails = mysql.query_db("SELECT email FROM users")
    err = False
    email = request.form['email']
    first = request.form['first_name']
    last = request.form['last_name']
    passw = request.form['password']
    passc = request.form['passcom']
    print(all_emails)
    if email or first or last:
        session['email'] = email
        session['first_name'] = first
        session['last_name'] = last
    if len(email) < 1 or len(first) < 1 or len(last) <1 or len(passw)<1 or len(passc)<1:
        flash('All fields are required')
        err = True
    if not EMAIL_REGEX.match(email):
        flash('Please enter a valid email address')
        session['email'] = ''
        err = True
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {
        'email' : email
    }
    result = mysql.query_db(query,data)
    if result:
        flash('Email taken!')
        err = True
    if passw != passc:
        flash("Passwords must match!")
        err = True
    if len(passw) < 8 and passc and passw:
        flash("Passwords must be 8 or more characters!")
        err = True
    if not first.isalpha() and first: 
        session['first_name'] = ''
        flash("Name must not contain numbers!")
        err = True
    if not last.isalpha() and last:
        session['last_name'] = ''
        flash("Name must not contain numbers!")
        err = True
    if err==True:
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])  
    query = "INSERT INTO users (email, first_name, last_name, password, created_at, updated_at) VALUES (%(email)s, %(first_name)s, %(last_name)s, %(password)s, NOW(), NOW());"
    data = {
            'email': request.form['email'],
            'first_name' : request.form['first_name'],
            'last_name' : request.form['last_name'],
            'password' : pw_hash
           }
    mysql.query_db(query, data)
    session['registered'] = True
    session['fname'] = request.form['first_name']
    return redirect('/home')
@app.route('/login', methods=['post'])
def login():
    session['login'] = 1
    email = request.form['email']
    passw = request.form['password']
    session['registered'] = False
    if len(passw) < 1 or len(email) < 1:
        flash('You must enter email and password!')
        return redirect('/')
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {
        'email' : email
    }
    result = mysql.query_db(query,data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], passw):
            session['fname'] = result[0]['first_name']
            return redirect('/home')
    flash("Could not log you in!")
    return redirect('/')

@app.route('/home')
def success():
    registered = session['registered']
    fname = session['fname']
    session.clear()
    return render_template('home.html', registered = registered, fname = fname)
@app.route('/logout', methods=['post'])
def loggout():
    flash('You have logged out!')
    return redirect('/')
@app.route('/destroy')
def destroy():
    session.clear()
    return redirect('/')
if __name__ == "__main__":
    app.run(debug=True)