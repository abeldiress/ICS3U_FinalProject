from flask import Flask, render_template, request, redirect, url_for, make_response
from requests import HTTPError
from datetime import datetime
import pyrebase

app = Flask(__name__)

config = {
    'apiKey': "AIzaSyA7LKeXKzL7r09GBvpVFx6uje023E2Q6BU",
    'authDomain': "ics-final-project.firebaseapp.com",
    'databaseURL': "https://ics-final-project-default-rtdb.firebaseio.com",
    'projectId': "ics-final-project",
    'storageBucket': "ics-final-project.appspot.com",
    'messagingSenderId': "337514158551",
    'appId': "1:337514158551:web:6cdae623b07b070c9f1392"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/verify')
def verify():
    if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '':
        return redirect(url_for('login'))

    email = request.cookies.get('email')
    password = request.cookies.get('password')
    user = auth.sign_in_with_email_and_password(email, password)
    if not auth.get_account_info(user['idToken'])['users'][0]['emailVerified']:
        auth.send_email_verification(user['idToken'])
        return '<h1 style="font-family: Source Sans Pro;" align="center">Your account has yet to be verified. Check your email to verify this account.</h1>'
    else:
        return redirect(url_for('matches'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        pwd = request.form['pwd']
        pwd_confirm = request.form['pwd_confirm']

        if pwd != pwd_confirm:
            return render_template('signup.html', confirmFail=True, weakPwd=False)

        try:
            user = auth.create_user_with_email_and_password(email, pwd)

            data = {'name': name, 'email': email, 'grade': 0, 'groups':[]}
            
            accountInfo = auth.get_account_info(user['idToken'])
            db.child('/users/' + accountInfo['users'][0]['localId'] + '/').push(data, user['idToken'])

            resp = make_response(redirect(url_for('verify')))
            resp.set_cookie('email', email)
            resp.set_cookie('password', pwd)
            return resp
        except Exception as err:
            print(err)
            if 'WEAK_PASSWORD' in str(err):
                return render_template('signup.html', confirmFail=False, weakPwd=True)

    return render_template('signup.html', confirmFail=False, weakPwd=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']
        try:
            user = auth.sign_in_with_email_and_password(email, pwd)
            accountInfo = auth.get_account_info(user['idToken'])

            resp = make_response(redirect(url_for('verify')))
            resp.set_cookie('email', email)
            resp.set_cookie('password', password)
            return resp
        except HTTPError as e:
            e = str(e)
            if 'EMAIL_NOT_FOUND' in e:
                return render_template('login.html', invalidPwd=True, content='This account doesn\'t exist. Try a different email or create an account.')
            elif 'INVALID_PASSWORD' in e:
                return render_template('login.html', invalidPwd=True, content='Incorrect Password. Double check and try again.')
            elif 'TOO_MANY_ATTEMPTS_TRY_LATER' in e:
                return render_template('login.html', invalidPwd=True, content='Too many unsuccessful login attempts. Please try again later.')
                    
        return redirect(url_for('verify'))
        
    try:
        email = request.cookies.get('email')
        password = request.cookies.get('password')
        user = auth.sign_in_with_email_and_password(email, password)
        return redirect(url_for('matches'))
    except:
        return render_template('login.html', invalidPwd=False)

    
@app.route('/question', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        title = request.form['email']
        txt = request.form['pwd']        
        
        if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '':
            return redirect(url_for('login'))

        email = request.cookies.get('email')
        password = request.cookies.get('password')
        user = auth.sign_in_with_email_and_password(email, password)
        
        question = {'title': title, 'txt': txt, 'name': user.name, 'date': datetime.now()}

        try:
            user = auth.sign_in_with_email_and_password(email, pwd)
            accountInfo = auth.get_account_info(user['idToken'])

            resp = make_response(redirect(url_for('verify')))
            resp.set_cookie('email', email)
            resp.set_cookie('password', password)
            return resp
        except HTTPError as e:
            e = str(e)
            if 'EMAIL_NOT_FOUND' in e:
                return render_template('login.html', invalidPwd=True, content='This account doesn\'t exist. Try a different email or create an account.')
            elif 'INVALID_PASSWORD' in e:
                return render_template('login.html', invalidPwd=True, content='Incorrect Password. Double check and try again.')
            elif 'TOO_MANY_ATTEMPTS_TRY_LATER' in e:
                return render_template('login.html', invalidPwd=True, content='Too many unsuccessful login attempts. Please try again later.')
                    
        return redirect(url_for('home'))
        
    return render_template('question.html')

app.run(port=4000, debug=True)
