from flask import Flask
from flask import request, render_template, make_response, session, flash, url_for
from flask_session import Session

from datetime import datetime

from redis import Redis
db = Redis(host='redis', port=6379, db=0)

from os import getenv
from dotenv import load_dotenv

from bcrypt import hashpw, gensalt, checkpw

load_dotenv()
SESSION_TYPE='redis'
SESSION_REDIS=db
app = Flask(__name__)
app.config.from_object(__name__)
#app.secret_key = getenv('SECRET_KEY')
ses = Session(app)

def is_user(username):
    return db.hexists(f"user:{username}", "password")

def save_user(email, username, password):
    salt = gensalt(5)
    password = password.encode()
    hashed = hashpw(password, salt)
    db.hset(f"user:{username}", "password", hashed)
    return True

def verify_user(username, password):
    password = password.encode()
    hashed = db.hget(f"user:{username}", "password")
    if not hashed:
        print(f"ERROR: No password for {username}")
        return False
    return checkpw(password, hashed)

def error(msg, status=400):
    response = make_response({"status":"error", "message":msg}, status)

def redirect(url, status=302):
    response = make_response('', status)
    response.headers['Location'] = url
    return response

@app.route('/sender/register')
def register_form():
    return render_template("register-form.html")

@app.route('/sender/register', methods=['POST'])
def register():
    username = request.form.get('username')
    if not username:
        flash("No username provided")
    
    email = request.form.get('email')
    if not email:
        flash("No e-mail provided")
    
    password = request.form.get('password')
    if not password:
        flash("No password provided")
    
    password2 = request.form.get('password2')
    if password != password2:
        flash("Password doesn't match")
        return redirect(url_for('register_form'))
    
    print(username, password, email)
    if username and email and password:
        if is_user(username):
            flash(f"User {username} already registered")
            return redirect(url_for('register_form'))
        success = save_user(email, username, password)
        if not success:
            flash("A problem occured while registering new user")
        return redirect(url_for('login_form'))

@app.route('/sender/logout', methods=['GET'])
def logout():
    session.clear()
    flash("Wylogowano pomyślnie")
    return redirect(url_for('login_form'))

@app.route('/sender/login', methods=['GET'])
def login_form():
    return render_template('login-form.html')

@app.route('/sender/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        flash("Missing username and/or password")
        return redirect(url_for('login_form'))
    if not verify_user(username, password):
        flash("Bad credentials")
        return redirect(url_for('login_form'))
    flash(f"Welcome {username}!")
    session["username"] = username
    session["logged-at"] = datetime.now()
    return redirect(url_for('home'))

@app.route('/sender/dashboard', methods=["GET"])
def show_dashboard():
    username = session.get("username")
    if not username:
        flash("Log in first!")
        return redirect(url_for("login_form"))
    else:
        return render_template('dashboard.html')

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
