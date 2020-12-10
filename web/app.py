from flask import Flask
from flask import request, render_template, make_response, session, flash, url_for
from flask_session import Session
from flask import jsonify
import requests

from uuid import uuid4
from datetime import datetime
from datetime import timedelta

from redis import Redis
import jwt

from os import getenv
from dotenv import load_dotenv

from bcrypt import hashpw, gensalt, checkpw
import logging

load_dotenv()
db = Redis(host=getenv("REDIS_HOST"), port=getenv("REDIS_PORT"), db=getenv("REDIS_NUM"), password=getenv("REDIS_PASS"))
SESSION_TYPE='redis'
SESSION_REDIS=db
app = Flask(__name__)
app.config.from_object(__name__)
ses = Session(app)
logging.basicConfig(level=logging.INFO)
ws_host = getenv("WS_HOST")

def is_user(username):
    return db.hexists(f"user:{username}", "password")

def save_user(email, username, password):
    salt = gensalt(5)
    password = password.encode()
    hashed = hashpw(password, salt)
    db.hset(f"user:{username}", "password", hashed)
    db.hset(f"user:{username}", "email", email)
    
    return True

def verify_user(username, password):
    password = password.encode()
    hashed = db.hget(f"user:{username}", "password")
    if not hashed:
        print(f"ERROR: No password for {username}")
        return False
    return checkpw(password, hashed)

def error(msg, status=400):
    return make_response({"status":"error", "message":msg}, status)

def redirect(url, status=302):
    response = make_response('', status)
    response.headers['Location'] = url
    return response

def generate_jwt():
    username = session.get("username")
    if not username:
        return ""
    exp = datetime.utcnow() + timedelta(minutes=10)
    token_bytes = jwt.encode({'username': username, 'usertype': 'sender', 'exp': exp}, getenv("JWT_SECRET"), algorithm='HS256')
    return token_bytes.decode()

@app.route('/sender/register')
def register_form():
    return render_template("register-form.html")

@app.route('/sender/register', methods=['POST'])
def register():
    username = request.form.get('username')
    if not username:
        flash("Nie podano nazwy użytkownika")
    
    email = request.form.get('email')
    if not email:
        flash("Nie podano e-maila")
    
    password = request.form.get('password')
    if not password:
        flash("Nie podano hasła")
    
    password2 = request.form.get('password2')
    if password != password2:
        flash("Podane hasła nie są zgodne")
        return redirect(url_for('register_form'))
    
    print(username, password, email)
    if username and email and password:
        if is_user(username):
            flash(f"Login {username} jest zajęty")
            return redirect(url_for('register_form'))
        success = save_user(email, username, password)
        if not success:
            flash("Wystąpił problem przy rejestracji nowego użytkownika")
            return redirect(url_for('register_form'))
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
        flash("Brak loginu/hasła")
        return redirect(url_for('login_form'))
    if not verify_user(username, password):
        flash("Nieprawidłowe dane logowania")
        return redirect(url_for('login_form'))
    flash(f"Witaj {username}!")
    session["username"] = username
    session["logged-at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    token = generate_jwt()
    logging.info(f"LOGGED IN, token {token}")
    return redirect(url_for('home'))

@app.route('/sender/dashboard', methods=["GET"])
def show_dashboard():
    username = session.get("username")
    if not username:
        flash("Aby przejść dalej zaloguj się!")
        return redirect(url_for("login_form"))
    else:
        return render_template('dashboard.html')

@app.route('/label', methods=["GET"])
def get_labels():
    username = session.get("username")
    if not username:
        return error("Log in to get labels", 401)
    headers={}
    token = generate_jwt()
    headers["Authorization"] = f"Bearer {token}"
    res = requests.get(f"{ws_host}/sender/label", headers=headers)
    return res.json(), res.status_code

@app.route('/label', methods=["POST"])
def add_label():
    username = session.get("username")
    if not username:
        return error("Log in to add labels", 401)
    headers={}
    token = generate_jwt()
    headers["Authorization"] = f"Bearer {token}"
    res = requests.post(f"{ws_host}/sender/label", headers=headers, data=request.form)
    return res.text, res.status_code


@app.route('/label/<label_id>', methods=["DELETE"])
def delete_label(label_id):
    username = session.get("username")
    if not username:
        return error("Log in to delete labels", 401)
    headers={}
    token = generate_jwt()
    headers["Authorization"] = f"Bearer {token}"
    res = requests.delete(f"{ws_host}/sender/label/{label_id}", headers=headers)
    return res.text, res.status_code

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
