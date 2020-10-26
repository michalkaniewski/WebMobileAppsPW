from flask import Flask, request, render_template

app = Flask(__name__)
supported_languages = ["pl", "cz", "es", "en-gb", "en"]

@app.route('/sender/sign-up')
def register_form():
    return render_template("register-form.html")

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
