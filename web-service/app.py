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
        print('Authorized: ' + str(g.authorization))
    except Error:
        print('Unauthorized: ' + e)
        g.authorization = {}
    logging.info(g.authorization)

@app.route('/label', methods=["GET"])
def get_labels():
    response_body = {}
    return jsonify(response_body), 200

def error(msg, status=400):
    return make_response({"status":"error", "message":msg}, status)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)