from flask import Flask, render_template, request, session, redirect, json
import pickle
import numpy as np
import pyrebase
import sys
print(sys.version)
# Load the model from the file
with open('ARIMA_VP.pkl', 'rb') as f:
    model_vp = pickle.load(f)

with open('ARIMA_AH.pkl', 'rb') as f:
    model_ah = pickle.load(f)

with open('ARIMA_FP.pkl', 'rb') as f:
    model_fp = pickle.load(f)

app = Flask(__name__,static_folder='static')

config = {
    'apiKey': "AIzaSyBixtA4v5mvxKvaTU61iq9Fr2Ln2OWlf3o",
    'authDomain': "tomatocare-78e23.firebaseapp.com",
    'projectId': "tomatocare-78e23",
    'storageBucket': "tomatocare-78e23.appspot.com",
    'messagingSenderId': "437959910172",
    'appId': "1:437959910172:web:dab8c80225929289dd90d9",
    'databaseURL' : "",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app.secret_key='secret'

# @app.route('/')
# def default_route():
#     return render_template('login.html')

@app.route('/')
def home_route():
    return render_template('index.html')


@app.route('/', methods=['POST', 'GET'])
def login():
    if "user" in session:
        return redirect('/index')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return redirect('/index')
        except:
            return 'Failed to login'
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if "user" in session:
        return redirect('/login')

    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user['idToken'])
            session['user'] = email
            return redirect('/login')
        except Exception as e:
            error = str(e)
            return render_template('signup.html', error=error)
    return render_template('signup.html')


@app.route('/index')
def index():
    if "user" not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)