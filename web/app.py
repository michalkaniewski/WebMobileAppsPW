from flask import Flask
from flask import request, render_template, make_response, session, flash, url_for
from flask_session import Session
from flask import jsonify
import requests
from six.moves.urllib.parse import urlencode

from uuid import uuid4
from datetime import datetime
from datetime import timedelta

from redis import Redis
import jwt

from os import getenv
from dotenv import load_dotenv

from bcrypt import hashpw, gensalt, checkpw
import logging

from authlib.integrations.flask_client import OAuth

load_dotenv()
db = Redis(host=getenv("REDIS_HOST"), port=getenv("REDIS_PORT"), db=getenv("REDIS_NUM"), password=getenv("REDIS_PASS"))
SESSION_TYPE='redis'
SESSION_REDIS=db
app = Flask(__name__)
app.config.from_object(__name__)
ses = Session(app)
logging.basicConfig(level=logging.INFO)
ws_host = getenv("WS_HOST")

AUTH0_CALLBACK_URL = getenv("AUTH0_CALLBACK_URL")
AUTH0_CLIENT_ID = getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = getenv("AUTH0_DOMAIN")
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = getenv("AUTH0_AUDIENCE")
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

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
    logging.info(token_bytes)
    logging.info(type(token_bytes))
    return token_bytes #.decode()

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    flash(f"Witaj {userinfo['name']}!")
    session["username"] = userinfo['name']
    session["logged-at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    token = generate_jwt()
    return redirect(url_for('home'))
@app.route('/login')
def login_oauth():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


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
    params = {'returnTo': url_for('login_form', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    #return redirect(url_for('login_form'))

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

@app.route('/sender/notifications', methods=["GET"])
def notifications_page():
    username = session.get("username")
    if not username:
        flash("Aby przejść dalej zaloguj się!")
        return redirect(url_for("login_form"))
    else:
        return render_template('notifications.html')

@app.route('/notification', methods=["GET"])
def get_notifications():
    username = session.get("username")
    if not username:
        return error("Log in to get notifications", 401)
    headers={}
    token = generate_jwt()
    headers["Authorization"] = f"Bearer {token}"
    res = requests.get(f"{ws_host}/sender/notification", headers=headers)
    if res.status_code != 200:
        return res.text, res.status_code
    logging.info(res)
    logging.info(res.json())
    return res.json(), res.status_code


@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
