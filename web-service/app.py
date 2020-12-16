from flask import Flask, g
from flask import request, make_response
from flask import jsonify
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link

from jwt import decode
from redis import Redis
from os import getenv
from dotenv import load_dotenv
from uuid import uuid4

import logging

load_dotenv()
db = Redis(host=getenv("REDIS_HOST"), port=getenv("REDIS_PORT"), db=getenv("REDIS_NUM"), password=getenv("REDIS_PASS"))
JWT_SECRET = getenv("JWT_SECRET")
app = Flask(__name__)
HAL(app)
logging.basicConfig(level=logging.INFO)

@app.before_request
def before_request_func():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
        logging.info("Authorized: " + g.authorization.get("username"))
    except Exception as e:
        g.authorization = {}
        logging.info("Unauthorized: " + str(e))

@app.route('/courier/label', methods=["GET"])
def list_labels():
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to get labels list", 401)
    if usertype != "courier":
        return error("Resource available only for couriers", 401)
    label_ids = db.keys("label:*")
    for i, id in enumerate(label_ids):
        label_ids[i] = id.decode('utf-8')
    links=[]
    labels = []
    for id in label_ids:
        label = {}
        label['id'] = id.split(":")[1]
        label['name'] = db.hget(id, 'name').decode('utf-8')
        label['receiver'] = db.hget(id, 'receiver').decode('utf-8')
        label['size'] = db.hget(id, 'size').decode('utf-8')
        label['target'] = db.hget(id, 'target').decode('utf-8')
        labels.append(label)
        if db.hget(id, "picked").decode('utf-8') == "false":
            links.append(Link(f"label:{label['name']}:pick", f"/courier/package/{label['id']}"))
    response_body = {}
    response_body['labels'] = labels
    document = Document(data=response_body, links=links)
    return document.to_json(), 200

@app.route('/courier/package', methods=["GET"])
def get_packages():
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to get packages", 401)
    if usertype != "courier":
        return error("Resource available only for couriers", 401)
    package_ids = db.smembers(f"courier:{username}:packages")
    package_ids = list(package_ids)
    
    for i, id in enumerate(package_ids):
        package_ids[i] = id.decode('utf-8')
    links=[]
    packages = []
    for id in package_ids:
        package = {}
        package['id'] = id
        label_id = db.hget(f"package:{id}", "label_id").decode('utf-8')
        package['status'] = db.hget(f"package:{id}", "status").decode('utf-8')
        package['name'] = db.hget(f"label:{label_id}", "name").decode('utf-8')
        package['receiver'] = db.hget(f"label:{label_id}", "receiver").decode('utf-8')
        package['size'] = db.hget(f"label:{label_id}", "size").decode('utf-8')
        package['target'] = db.hget(f"label:{label_id}", "target").decode('utf-8')
        packages.append(package)
        links.append(Link(f"package:{package['name']}:changestatus", f"/courier/package/{package['id']}"))
    response_body = {}
    response_body['packages'] = packages
    document = Document(data=response_body, links=links)
    return document.to_json(), 200
    
@app.route('/courier/package/<label_id>', methods=["POST"])
def create_package(label_id):
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to add package", 401)
    if usertype != "courier":
        return error("Resource available only for couriers", 401)
    if len(db.keys(f"label:{label_id}")) == 0:
        return error(f"Cannot find label of id: {label_id}", 400)
    if db.hget(f"label:{label_id}", "picked").decode('utf-8') == "true":
        return error("Already created", 400)
    db.hset(f"label:{label_id}", "picked", "true")
    id = str(uuid4())
    db.hset(f"package:{id}", "label_id", label_id)
    db.hset(f"package:{id}", "status", "ODEBRANA")
    db.sadd(f"courier:{username}:packages", id)
    links = []
    links.append(Link('package:changestatus', f'/courier/package/{id}'))
    document = Document(data={"message": id}, links=links)
    return document.to_json(), 201

@app.route('/courier/package/<package_id>', methods=["PUT"])
def change_status(package_id):
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to add package", 401)
    if usertype != "courier":
        return error("Resource available only for couriers", 401)
    allowed_status = ["ODEBRANA", "W DRODZE", "DOSTARCZONA"]
    new_status = request.args.get('status')
    if not new_status in allowed_status:
        return error(f"Not allowed status: {new_status}", 400)
    db.hset(f"package:{package_id}", "status", new_status)
    links = []
    document = Document(data={"message": f"Status changed into {new_status}"}, links=links)
    return document.to_json(), 200

@app.route('/sender/label', methods=["GET"])
def get_labels():
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to get labels", 401)
    if usertype != "sender":
        return error("Resource available only for senders", 401)
    label_ids = db.smembers(f"user:{username}:labels")
    label_ids = list(label_ids)
    
    for i, id in enumerate(label_ids):
        label_ids[i] = id.decode('utf-8')
    links=[]
    labels = []
    for id in label_ids:
        label = {}
        label['id'] = id
        label['name'] = db.hget(f"label:{id}", "name").decode('utf-8')
        label['receiver'] = db.hget(f"label:{id}", "receiver").decode('utf-8')
        label['size'] = db.hget(f"label:{id}", "size").decode('utf-8')
        label['target'] = db.hget(f"label:{id}", "target").decode('utf-8')
        labels.append(label)
        if db.hget(f"label:{id}", "picked").decode('utf-8') == "false":
            links.append(Link(f"label:{label['id']}:delete", f"/sender/label/{id}"))
    response_body = {}
    response_body['labels'] = labels
    document = Document(data=response_body, links=links)
    return document.to_json(), 200

@app.route('/sender/label', methods=["POST"])
def add_label():
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to add labels", 401)
    if usertype != 'sender':
        return error("Resource available only for senders", 401)
    id = str(uuid4())
    name = request.form.get("name")
    receiver = request.form.get("receiver")
    size = request.form.get("size")
    target = request.form.get("target")
    if not name:
        return error("No value of name", 400)
    if not receiver:
        return error("No value of receiver", 400)
    if not size:
        return error("No value of size", 400)
    if not target:
        return error("No value of target", 400)
    db.hset(f"label:{id}", "name", name)
    db.hset(f"label:{id}", "receiver", receiver)
    db.hset(f"label:{id}", "size", size)
    db.hset(f"label:{id}", "target", target)
    db.hset(f"label:{id}", "picked", "false")
    db.sadd(f"user:{username}:labels", id)
    links = []
    links.append(Link('label:delete', f'/sender/label/{id}'))
    document = Document(data={"message": id}, links=links)
    return document.to_json(), 201

@app.route('/sender/label/<label_id>', methods=["DELETE"])
def delete_label(label_id):
    username = g.authorization.get("username")
    usertype = g.authorization.get("usertype")
    if not username:
        return error("Log in to delete labels", 401)
    if usertype != 'sender':
        return error("Resource available only for senders", 401)

    if not db.sismember(f"user:{username}:labels", label_id):
        return error(f"No such label for user {username}", 403)
    if db.hget(f"label:{label_id}", "picked").decode('utf-8') == "true":
        return error("Cannot remove picked label", 403)
    db.delete(f"label:{label_id}")
    db.srem(f"user:{username}:labels", label_id)
    document = Document(data={"message": label_id}, links=[])
    return document.to_json(), 200

@app.route('/sender', methods=["GET"])
def sender():
    links = []
    links.append(Link('label', '/sender/label'))
    document = Document(data={}, links=links)
    return document.to_json(), 200

@app.route('/courier', methods=["GET"])
def courier():
    links = []
    links.append(Link('label', '/courier/label'))
    links.append(Link('label', '/courier/package'))
    document = Document(data={}, links=links)
    return document.to_json(), 200

@app.route('/', methods=["GET"])
def info():
    links = []
    links.append(Link('sender', '/sender'))
    links.append(Link('courier', '/courier'))
    document = Document(data={}, links=links)
    return document.to_json(), 200

def error(msg, status=400):
    return make_response({"status":"error", "message":msg}, status)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)