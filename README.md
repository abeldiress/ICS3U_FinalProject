# Project
This is my final project for my ICS3U course, a web app for students to help each other with their schoolwork.

# Features
The key features of the program:
- Login/Signup
- Questions Page - ask questions to everyone signed up
- Replying to questions - reply to anyone's question
- Pinning the questions into a permanent questions - keep them for later use

The questions, similar to that of social media videos, get removed at the end of the day. This feature was chosen to focus the users on the most relevant questions, and incentivise those who ask questions to choose theirs carefully.

# Installation
To use, the following packages must be installed:
- pyrebase
- flask
- requests

The following line can be inputted into your machine's terminal: `pip install pyrebase flask requests`.

# Known Bugs
There should be no apparent bugs if all the steps are followed.

# Data Structure
The biggest part of this project in terms of data is the `question` data structure, which has the following:

- `id` - unique identifier for question
- `author` - name of user who asked question
- `title` - title of question
- `question` - body text of question
- `email` - email of user (stored for bookeeping purposes)
- `date` - date it was created
- `time` - time it was created
- `resource` - boolean value determineg whether the question is part of the resources
- `replies` - list of replied containg some text, time, and author of reply

# Exaplantion for the Lack of Modularity
Looking at the code, you might see some cases of reptitive of code, such as:
`if str(request.cookies.get('email')) == 'None' or str(request.cookies.get('email')) == '': return redirect(url_for('login'))`

Although it might seem intuitive to place thse in a function and then calling such function, this is simply not possible. As all fucntions relating to webpages in Flask are utility functions, that function *must* return something. This is found in more detail here: https://flask.palletsprojects.com/en/2.1.x/api/.

# Docstrings
In most cases, the args in the docstrings will refer to the inputted HTML in the POST method in which the function is inputted. If not, I will indicate this with '(non-form)' It will also list all possible redirects in the fucntions. Docstrings will have different args/returns for GET and POST when necessary (ex: `login()`).

Also, for all Flaks utility functions, a request object is automatically passed . I mentioned it in each docstring just to acknowledge its presence.

# Support
If you encounter any unexpected errors or occurences, contact abeldiress05@gmail.com as soon as possible.

# Sources
List of my sources:
1. https://flask.palletsprojects.com/en/2.1.x/quickstart/#a-minimal-application
Starting code for Flask application.

2. https://docs.python.org/3/library/venv.html
Creation of virtual python environment.

3. https://flask.palletsprojects.com/en/1.1.x/patterns/templateinheritance/
Template inheritance for HTML file renders in Flask.

4. https://bulma.io/documentation/overview/start/
Importing the Bulma CSS framework (frontend).

5. https://github.com/thisbejim/Pyrebase
Pyrebase - A simple python wrapper for the Firebase API.

6. https://firebase.google.com/docs/auth
Firebase Authentication Documentation.

7. https://firebase.google.com/docs/database
Firebase Database Documentation.

8. https://www.tutorialspoint.com/flask/flask_cookies.htm
Cookies tutorial in Flask.