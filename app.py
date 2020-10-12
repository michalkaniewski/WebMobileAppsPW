from flask import Flask, request

app = Flask(__name__)
supported_languages = ["pl", "cz", "es", "en-gb", "en"]

@app.route('/')
def index():
    return """
    <!doctype html>
    <head>
        <link rel="stylesheet" href="/static/main.css"></link>
    </head>
    <body>
        <h3>Witaj</h3>
        <p>Formularz</p>
        <form>
        	<input type="text"></input>
        	<input type="text"></input>
        </form>
    </body>"""
    
if __name__ == '__main__':
    app.run(threaded=True, port=5000, debug=True)
