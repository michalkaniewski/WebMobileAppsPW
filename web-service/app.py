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
    logging.info(token)
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception:
        g.authorization = {}
    logging.info(g.authorization)

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
    db.hset(f"label:{id}", "name", name)
    db.hset(f"label:{id}", "receiver", receiver)
    db.hset(f"label:{id}", "size", size)
    db.hset(f"label:{id}", "target", target)
    db.sadd(f"user:{username}:labels", id)
    return "Label created", 201

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
    db.delete(f"label:{label_id}")
    db.srem(f"user:{username}:labels", label_id)
    return "Label deleted correctly", 200

def error(msg, status=400):
    return make_response({"status":"error", "message":msg}, status)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)