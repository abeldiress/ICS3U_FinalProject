from flask import Flask, render_template
import pyrebase

app = Flask(__name__)

config = {}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@app.route('/')
def home():
    return render_template('signup.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
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


app.run(port=4000, debug=True)
