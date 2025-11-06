from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import get_user
from db import get_db

app = Flask(__name__)
app.secret_key = 'human-interactions-class'

@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user(email, password)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return  render_template('login.html')

# test login 
@app.route('/dashboard')
def dashboard():
    return render_template('base.html')




if __name__ == '__main__':
    app.run(debug=True) 