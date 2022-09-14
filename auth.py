#Blueprint is a way to organize group of related views. It is used to register with the application and registering views and other code. Fantasyproject has two blue prints - for authentication functions and blog posts functions. 
#Below is the authentication function. It is to create a work for the /auth directory.
#The Fantasyproject passes the __name__ to be defined at bp and the url_prefix is used  to prepend all the URL associated with the blueprint.
#You can always import using app.register.blueprint

import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from Fantasyproject.db import get_db



#Create a blueprint for the authorization. A blueprint is an object that allows defining application functions. 
bp = Blueprint('auth', __name__, url_prefix='/auth')

#The code below talks about how to register a view form. Basically - anything below will return an HTML form for the client to fill out. Either validate the input and create a new user or present an error message. It just shows the form that the end-customer has to fill out. 
@bp.route('/register', methods=('GET', 'POST')) #associates URL/register view and when receiving a request from /auth/register it will call the register and user the return value as response. Allows for http://127.0.0.1:5000/auth/register to exist.
def register():
    if request.method == 'POST': #used to designate and validate the input (of a user submitting a form)
        username = request.form['username'] #special type of dict mapping (both username and password)
        password = request.form['password']
        db = get_db()
        error = None

        if not username: #validate the username and password are not empty "username or password is required". It forces the end-user to input their username and password. 
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)), #the generate_password_hash is used to secure password. 
                ) #the db.execute replaces any placeholders with.
                db.commit() #Since modifying data via the db.execute (in this case hasing out the password) a db.commit is needed. 
            except db.IntegrityError: #The ssqlite3.Integrity error (db.Integrity error)occurs if username already exists (e.g. f"User {username} is already registered.")
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login")) #storing the user and is then re-directed to url_for which generates the URL for the actual login from the auth.login page. 

        flash(error) #this is just to to show that validation failed. 

    return render_template('auth/register.html') #renders the actual template that contains HTML and will show. 


#The code below follows the same pattern for the Register (above) but instead its for the actual LOGIN. In this case, the user is queried first and stored in variable for later user "user"
@bp.route('/login', methods=('GET', 'POST')) #effectively the endpoint for the login function is auth.login (since login is on the AUTH App factory.
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() #returns one per query (the fetchone() function)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password): #the check_password_hash checks for the password in the generate_password_hash function above. If compareed, they are good. 
            error = 'Incorrect password.'

        if error is None:
            session.clear() #session is a dict that stores date. When validaiton succeeds the id is stored in a new session. Effectively the id is stored in a session. They can be re-used multiple times (aka the login of the customer) 
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')




@bp.before_app_request #this specificallt registers a function that runs before the view function. Such a function is executed before each request, even if outside of a blueprint.
def load_logged_in_user(): #checks if the users "id" is stored in a sessions from the session.clear() function above. it stores it on g.user. If there is nothing on the lenght of the request g.user then it will change to None.
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()




#this is for logout from the HTML request. You need to remove the user id from the session. Then load_logged_in_user will not load any subsquent requests because of session.clear
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))




#require authentication in other views - in order to make any changes the user will need to be logged in. Hence, a decorator is used to check how each view is applied. 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login')) #the url_for generates a URL to a view based on name and arguments. The name is also called an ENDPOINT. 

        return view(**kwargs)
    return wrapped_view
#This decorator returns a new view function that wraps the original view it’s applied to. Look at the decorator above. 
#The new function checks if a user is loaded and redirects to the login page otherwise.
# If a user is loaded the original view is called and continues normally. You’ll use this decorator when writing the blog views.
#the index.html file can be loaded onto url_for('index').
#when using a blueprint the name of blueprint (auth) is prepended to the name of the function (login). Hence auth.login. 
