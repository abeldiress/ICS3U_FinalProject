from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('signup.html')


app.run(port=4000, debug=True)
