from flask import Flask, request

app = Flask(__name__)
supported_languages = ["pl", "cz", "es", "en-gb", "en"]

@app.route('/')
def index():
    lang = request.accept_languages.best_match(supported_languages)
    if lang == "pl":
        msg = "Witaj"
    elif lang == "cz":
        msg = "Ahoj"
    elif lang == "es":
        msg = "Hola"
    elif lang == "en-gb":
        msg = "Delighted to meet you"
    else:
        msg = "Howdy"
    
    return f"<h1>{msg}.</h1>"

@app.route('/secret')
def secret():
    return "No entry!", 403

@app.route('/brew/<beverage>')
def brew(beverage):
    if beverage == "coffee":
        return '''<pre>
    I am a teapot
       _...._
     .'  _ _ `.
    | ."` ^ `". _,
    \_;`"---"`|//
      |       ;/
      \_     _/
        `"""`
        </pre>''', 418
    if beverage == "beer":
        return "Silly you..." 
    if beverage == "vodka":
        return "на здоро́вье"
    if beverage == "tea":
        return "Which one? Green, red, black..."
    return "Huh?", 400
    
if __name__ == '__main__':
    app.run(threaded=True, port=5000, debug=True)