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
    
    return render_template('index.html')
@app.route('/add_email', methods=['POST'])
def create():
    email = request.form['email']
    if len(email) < 1:
        flash("Please enter an email address") 
        return redirect('/')
    if not EMAIL_REGEX.match(email):
        flash('Please enter a valid email address')
        return redirect('/')
    query = "INSERT INTO email (email, created_at, updated_at) VALUES (%(email)s, NOW(), NOW());"
    data = {
             'email': request.form['email']
           }
    mysql.query_db(query, data)
    return redirect('/success')
@app.route('/success')
def success():
    all_email = mysql.query_db("SELECT * FROM email")
    return render_template('success.html', email = all_email)
@app.route('/delete_email', methods=['post'])
def delete():
    query = "DELETE FROM friendsdb.email WHERE idemail = %(id)s;"
    data = {
             'id': request.form['deletethis'],
    }
    mysql.query_db(query, data)
    return redirect('/success')
if __name__ == "__main__":
    app.run(debug=True)