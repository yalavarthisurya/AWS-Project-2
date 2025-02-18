from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'users.db')

# SQLite setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT UNIQUE, password TEXT, firstname TEXT, lastname TEXT, email TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    email = request.form['email']

    # Validate registration details
    if not validate_registration(username, password, email):
        return redirect(url_for('index'))

    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",
                  (username, password, firstname, lastname, email))
        conn.commit()
        conn.close()

        return redirect(url_for('profile', username=username))
    except sqlite3.IntegrityError:
        flash('Username already exists. Please choose another one.')
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['login_username']
    password = request.form['login_password']

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))
    else:
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user:
        return render_template('userprofile.html', user=user)
    else:
        flash('User not found.')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

def validate_registration(username, password, email):
    if len(password) < 6 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        flash('Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, and one number.')
        return False
    if not valid_email(email):
        flash('Invalid email format. Please try again.')
        return False
    return True

def valid_email(email):
    return '@' in email and '.' in email

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
