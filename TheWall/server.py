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
mysql = connectToMySQL('thewall')
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
    err = False
    email = request.form['email']
    first = request.form['first_name']
    last = request.form['last_name']
    passw = request.form['password']
    passc = request.form['passcom']
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
    query = "select id from users where email = %(email)s;"
    data = {
        'email' : request.form['email']
    }
    result = mysql.query_db(query,data)
    session.clear()
    session['id'] = result[0]['id']
    return redirect('/home')




@app.route('/login', methods=['post'])
def login():
    session['login'] = 1
    email = request.form['email']
    passw = request.form['password']
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
            session['id'] = result[0]['id']
            return redirect('/home')
    flash("Could not log you in!")
    return redirect('/')




@app.route('/home')
def success():
    if 'id' not in session:
        return redirect('/')
    query = "SELECT first_name FROM users WHERE id = %(id)s;"
    data = {
        'id' : session['id']
    }
    result = mysql.query_db(query,data)
    fname = result[0]['first_name']
    query = "SELECT CONCAT_WS(' ', users.first_name, users.last_name) as name, messages.id as message, DATE_FORMAT(messages.created_at, '%M %D %Y %l:%i %p') as created, messages.text as text, users.id as user FROM users join messages on users.id = messages.user_id;"
    resultMess = mysql.query_db(query)
    query = "SELECT CONCAT_WS(' ', users.first_name, users.last_name) as name, posts.id as comment, DATE_FORMAT(posts.created_at, '%M %D %Y %l:%i %p') as created, posts.text as text, posts.message_id as message  FROM users join posts on users.id = posts.user_id;"
    resultComm = mysql.query_db(query)
    return render_template('home.html', fname = fname, messages = reversed(resultMess), comments = resultComm)




@app.route('/logout', methods=['post'])
def loggout():
    session.clear()
    flash('You have logged out!')
    return redirect('/')




@app.route('/message', methods=['post'])
def message():
    if len(request.form['messagebox'])<1:
        return redirect('/home')
    query = "INSERT INTO messages (text, user_id, created_at, updated_at) VALUES (%(text)s, %(user_id)s, NOW(), NOW());"
    data = {
            'text': request.form['messagebox'],
            'user_id' : session['id']
    }
    mysql.query_db(query, data)
    return redirect('/home')




@app.route('/comment', methods=['post'])
def comment():
    if len(request.form['commentbox'])<1:
        return redirect('/home')
    query = "INSERT INTO posts (text, user_id, message_id, created_at, updated_at) VALUES (%(text)s, %(user_id)s, %(message_id)s, NOW(), NOW());"
    data = {
            'text': request.form['commentbox'],
            'user_id' : session['id'],
            'message_id' : request.form['message_id']
    }
    mysql.query_db(query, data)
    return redirect('/home')




@app.route('/delete', methods=['post'])
def delete():
    message = request.form['message_id']
    print('banananas')
    query = "DELETE FROM thewall.messages where id = %(message)s;"
    data = {
            'message': message
    }
    mysql.query_db(query, data)
    return redirect('/home')




if __name__ == "__main__":
    app.run(debug=True)