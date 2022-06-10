"""
Abel Diress
ICS3U-04
Flask app to ask questions about schools and reply.
"""

from flask import Flask, render_template, request, redirect, url_for, make_response
from requests import HTTPError
from datetime import datetime
import pyrebase

# inital flask app
app = Flask(__name__)
# SOurce [1]

# configuration settings for database
config = {
    'apiKey': "AIzaSyA7LKeXKzL7r09GBvpVFx6uje023E2Q6BU",
    'authDomain': "ics-final-project.firebaseapp.com",
    'databaseURL': "https://ics-final-project-default-rtdb.firebaseio.com",
    'projectId': "ics-final-project",
    'storageBucket': "ics-final-project.appspot.com",
    'messagingSenderId': "337514158551",
    'appId': "1:337514158551:web:6cdae623b07b070c9f1392"
}

# initalized connection to firebase database based on configurations above
# Source [5]
firebase = pyrebase.initialize_app(config)
# Source [6]
auth = firebase.auth()
# Source [7] - *all uses of db cite this source
db = firebase.database()

def getUser(req):
    '''
    Logs user and retireves authentication data using cookie data.
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        user: Pyrebase User
    '''
    # gets user cookies and logs them in
    # Source [8]
    email = req.cookies.get('email')
    password = req.cookies.get('password')

    # Source [6]
    user = auth.sign_in_with_email_and_password(email, password)

    return user

# logout function - destroys login cookies and redirects to login page
@app.route('/logout', methods=['GET'])
def logout():
    '''
    GET: removes cookies from user machine
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        login: Response
    '''
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('email', '')
    resp.set_cookie('password', '')
    return resp

# home function - displays recent questions
@app.route('/', methods=['GET'])
def home():
    '''
    GET: displays daily questions and responses
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        home: Response
    '''

    # checks if user is logged in, if not, redirects to login page
    if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '':
        return redirect(url_for('signup'))

    # gets all questions from database and their ids
    all_questions = list(dict(db.child('/questions').get().val()).values())
    question_ids = list(dict(db.child('/questions').get().val()).keys())

    # merges the question data with its respective id in a dictionary
    for i in range(len(all_questions)):
        all_questions[i]['id'] = question_ids[i]

    # num_of_questions is the number of questions posted today (not including those in resources)
    present_questions = []
    num_of_questions = 0

    # sifts through all questions that are not posted today or part of the resources
    for i in range(len(all_questions)):
        if all_questions[i]['resource']:
            present_questions.append(all_questions[i])
            continue

        if all_questions[i]['date'] == datetime.now().strftime('%d-%m-%y'):
            num_of_questions += 1
            present_questions.append(all_questions[i])
        
    # date in string format
    expanded_date = datetime.now().strftime('%B %d, 20%y')

    # returns home.html with all the questions, number, and date
    # Source [3]
    return render_template('home.html', questions=present_questions, num_of_questions=num_of_questions, expanded_date=expanded_date)

@app.route('/question', methods=['GET', 'POST'])
def question():
    '''
    GET: displays input form for user to enter their question
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        question: Response
    
    POST: uploads question to db and redirects to home
    Args:
        title: str
        question: str
    Returns:
        home: Response
    '''
    if request.method == 'POST':
        # extracts the data inputted by the user in the HTML
        title = request.form['title']
        question = request.form['question']        
        
        # checks if user is logged in, if not, redirects to login page
        # Source [8]
        if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '':
            return redirect(url_for('login'))

        user = getUser(request)

        # accesses user data from database
        accountInfo = auth.get_account_info(user['idToken'])
        userInfo = dict(db.child('/users/' + accountInfo['users'][0]['localId'] + '/').get(user['idToken']).val())

        name = userInfo[list(userInfo.keys())[0]]['name']
        
        # basic question data format
        question = {'title': title, 'question': question, 'name': name, 'email': user['email'], 'replies': [], 'resource': False, 'time': datetime.now().strftime('%H:%M:%S'), 'date': datetime.now().strftime('%d-%m-%y')}
        
        # uploads question to database, wiht the root being a unique, random id
        db.child('/questions/').push(question, user['idToken'])
                    
        # returns to home page
        return redirect(url_for('home'))
    return render_template('question.html')


@app.route('/reply/<question_id>', methods=['GET', 'POST'])
def reply(question_id):
    '''
    GET: displays input form for user to enter their reply
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        reply: Response
    
    POST: uploads reply to db and redirects to home
    Args:
        question_id(non-form): str
        text: str
    Returns:
        home: Response
    '''
    # checks if user is logged in, if not, redirects to login page
    if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '':
        return redirect(url_for('login'))

    user = getUser(request)

    if request.method == 'POST':
        # basic reply data format
        text = request.form['text']
        reply_response = {'user': user['email'], 'text': text, 'time': datetime.now().strftime('%H:%M:%S')}

        # gets the current list of replies, if none, creates list
        replies = db.child(f'/questions/{question_id}/replies/').get().val()
        if replies == None:
            replies = []
            
        # adds reply to list and then updates the database with new reply
        replies.append(reply_response)
        db.child(f'/questions/{question_id}/').update({'replies': replies})

        # returns with home page
        return redirect(url_for('home'))
    
    # gets question data
    question = dict(db.child(f'/questions/{question_id}/').get().val())
    return render_template('reply.html', question=question)

@app.route('/resource/<question_id>', methods=['GET'])
def addResource(question_id):
    '''
    GET: cahnges question to resource and redirects to home
    Args:
        question_id(non-form): str
        request: werkzeug.local.LocalProxy
    Returns:
        home: Response
    '''
    # changes question to resource by changing a key in its dict, then redirects to home
    db.child(f'/questions/{question_id}').update({'resource': True})
    return redirect(url_for('home'))

# verify email function
@app.route('/verify', methods=['GET'])
def verify():
    '''
    GET: checks if user verified their email, sends email if not
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        home: Response
    '''
    # checks if user is logged in, if not, redirects to login page
    if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '':
        return redirect(url_for('login'))

    user = getUser(request)

    # if not verified, informs user; if not, sends user to home page
    if not auth.get_account_info(user['idToken'])['users'][0]['emailVerified']:
        auth.send_email_verification(user['idToken'])
        return '<h1 align="center">Your account has yet to be verified. Check your email to verify this account.</h1>'
    else:
        return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    '''
    GET: displays input form for user to enter their signup info
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        verify: Response
        or
        signup: Response
    
    POST: creates user in db and auth, redirects to verify
    Args:
        username: str
        email: str
        pwd: str
        pwd_confirm: str
    Returns:
        home: Response
    '''
    if request.method == 'POST':
        # gets inputted HTML data
        name = request.form['username']
        email = request.form['email']
        pwd = request.form['pwd']
        pwd_confirm = request.form['pwd_confirm']

        # returns user to page with error if the password and confirm password are not the same
        if pwd != pwd_confirm:
            return render_template('signup.html', confirmFail=True, weakPwd=False)

        try:
            # creates user in Firebase's authentication service and saves the name in the database
            user = auth.create_user_with_email_and_password(email, pwd)
            data = {'name': name, 'email': email}
            
            # pushes user data into database with key being idToken
            accountInfo = auth.get_account_info(user['idToken'])
            db.child('/users/' + accountInfo['users'][0]['localId'] + '/').push(data, user['idToken'])

            # stores cookies and redirects to verify page
            resp = make_response(redirect(url_for('verify')))
            resp.set_cookie('email', email)
            resp.set_cookie('password', pwd)
            return resp
        except Exception as err:
            # if password does not satisfy Firebase's built-in password rules, returns to page w/ error
            if 'WEAK_PASSWORD' in str(err):
                return render_template('signup.html', confirmFail=False, weakPwd=True)

    return render_template('signup.html', confirmFail=False, weakPwd=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    GET: displays input form for user to enter their login info
    Args:
        request: werkzeug.local.LocalProxy
    Returns:
        home: Response
        or
        login: Response
    
    POST: logs user in and sends to verify
    Args:
        email: str
        pwd: str
    Returns:
        verify: Response
    '''

    if request.method == 'POST':
        # get inputted user data
        email = request.form['email']
        pwd = request.form['pwd']
        try:
            # verifies if login credntials are valid, if not, it will be caught by the try, except
            user = auth.sign_in_with_email_and_password(email, pwd)

            # saves user cookies
            resp = make_response(redirect(url_for('verify')))
            resp.set_cookie('email', email)
            resp.set_cookie('password', pwd)
            return resp
        except HTTPError as e:
            e = str(e)
            # returns user to same apge with text based on the error
            if 'EMAIL_NOT_FOUND' in e:
                return render_template('login.html', invalidPwd=True, content='This account doesn\'t exist. Try a different email or create an account.')
            elif 'INVALID_PASSWORD' in e:
                return render_template('login.html', invalidPwd=True, content='Incorrect Password. Double check and try again.')
            elif 'TOO_MANY_ATTEMPTS_TRY_LATER' in e:
                return render_template('login.html', invalidPwd=True, content='Too many unsuccessful login attempts. Please try again later.')
                    
        return redirect(url_for('verify'))
    
    # if user is already logged in, redirect to home page, if not, render the login HTML
    try:
        user = getUser(request)
        return redirect(url_for('home'))
    except:
        return render_template('login.html', invalidPwd=False)

# runs all the routing functions on a WSGI web app on port 4000
app.run(port=4000, debug=True)
# Source [1]

# Source [2] was intended to be intially used, but I removed it later from the progam but kept it in citations to show my process.