#!/usr/bin/env python3
"""
    batman.app
    ~~~~~~~~~~

    Web application for visualizing the health effects of bitter gourd and yam
    compounds, based on our results from text mining PubMed articles.

    :copyright: © 2018 by Jonathan Feenstra.
    :license: MIT, see LICENSE for more details.
"""

__version__ = '0.2'


from functools import wraps

from flask import (flash, Flask, redirect, render_template, request, session,
                   url_for)
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, PasswordField, StringField, validators
from wtforms.fields.html5 import EmailField


app = Flask(__name__)
app.config.from_pyfile('config.py')
mysql = MySQL(app)


def is_logged_in(f):
    """Check if the user is logged in."""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login required', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index():
    """Render the 'home.html' template."""
    return render_template('home.html')


@app.route('/about')
def about():
    """Render the 'about.html' template."""
    return render_template('about.html')


@app.route('/search')
def search():
    """Render the 'search.html' template."""
    return render_template('search.html')


@app.route('/help')
def help():
    """Render the 'help.html' template."""
    return render_template('help.html')


@app.route('/contact')
def contact():
    """Render the 'contact.html' template."""
    return render_template('contact.html')


@app.route('/pacman')
def pacman():
    """Render the 'pacman.html' template."""
    return render_template('pacman.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Render the 'register.html' template and handle its POST-requests."""
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()
        user_data = cur.execute('''SELECT * FROM user WHERE email = %s''',
                                [email])
        if user_data > 0:
            cur.close()
            error = 'Email already taken'
            return render_template('register.html', error=error)
        else:
            cur.execute('''INSERT INTO users(name, email, password)
                        VALUES(%s, %s, %s)''', (name, email, password))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful', 'success')
            return redirect(url_for('index'))
        cur.close()
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Render the 'login.html' template and handle its POST-requests."""
    if request.method == 'POST':
        email = request.form['email']
        entered_password = request.form['password']
        cur = mysql.connection.cursor()
        user_data = cur.execute('''SELECT * FROM user WHERE email = %s''',
                                [email])
        cur.close()
        if user_data > 0:
            data = user_data.fetchone()
            password = data['password']
            if sha256_crypt.verify(entered_password, password):
                session['logged_in'] = True
                session['email'] = email
                session['name'] = data['name']
                flash('Login successful', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid password.'
                return render_template('login.html', error=error)
        else:
            error = 'Invalid email.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    """Log out the user and redirect to 'index'."""
    session.clear()
    flash('Logout successful', 'success')
    return redirect(url_for('index'))


@app.route('/shutdown')
def shutdown_server():
    """Shut down the hosted server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return 'server shutdown'


class RegisterForm(Form):
    """Form for user registration."""
    name = StringField('Full name', [validators.Length(min=1, max=50)])
    email = EmailField('Email', [validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm password')


if __name__ == '__main__':
    app.run()
