from flask import Flask
from flask import request, render_template, make_response, session, flash, url_for
from flask_session import Session
from flask import jsonify

from uuid import uuid4
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
    session["logged-at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return redirect(url_for('home'))

@app.route('/sender/dashboard', methods=["GET"])
def show_dashboard():
    username = session.get("username")
    if not username:
        flash("Log in first!")
        return redirect(url_for("login_form"))
    else:
        return render_template('dashboard.html')

@app.route('/label', methods=["GET"])
def get_labels():
    username = session.get("username")
    if not username:
        return error("Log in to get labels", 401)
    label_ids = db.smembers(f"user:{username}:labels")
    label_ids = list(label_ids)
    
    for i, id in enumerate(label_ids):
        label_ids[i] = id.decode('utf-8')
    
    labels = []
    for id in label_ids:
        label = {}
        label['id'] = id
        label['name'] = db.hget(f"label:{id}", "name").decode('utf-8')
        label['receiver'] = db.hget(f"label:{id}", "receiver").decode('utf-8')
        label['size'] = db.hget(f"label:{id}", "size").decode('utf-8')
        label['target'] = db.hget(f"label:{id}", "target").decode('utf-8')
        labels.append(label)
    response_body = {}
    response_body['labels'] = labels
    return jsonify(response_body), 200
    # TODO: Body

@app.route('/label', methods=["POST"])
def add_label():
    username = session.get("username")
    if not username:
        return error("Log in to add labels", 401)
    creating_user = session['username']
    id = str(uuid4())
    name = request.form.get("name")
    receiver = request.form.get("receiver")
    size = request.form.get("size")
    target = request.form.get("target")
    db.hset(f"label:{id}", "name", name)
    db.hset(f"label:{id}", "receiver", receiver)
    db.hset(f"label:{id}", "size", size)
    db.hset(f"label:{id}", "target", target)
    db.sadd(f"user:{creating_user}:labels", id)
    return "Label created", 201


@app.route('/label/<label_id>', methods=["DELETE"])
def delete_label(label_id):
    username = session.get("username")
    if not username:
        return error("Log in to delete labels", 401)
    if not db.sismember(f"user:{username}:labels", label_id):
        return error(f"No such label for user {username}", 403)
    db.delete(f"label:{label_id}")
    db.srem(f"user:{username}:labels", label_id)
    return "Label deleted correctly", 200

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
