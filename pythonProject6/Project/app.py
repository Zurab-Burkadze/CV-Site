from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'zuka112'


# SQLite3 database initialization
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Home page route
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Home page with CRUD operations for SIWI
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        siwi_text = request.form['siwi_text']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO siwis (username, siwi_text, created_at) VALUES (?, ?, ?)',
                       (session['username'], siwi_text, datetime.now()))
        conn.commit()
        conn.close()
        flash('SIWI created successfully!', 'success')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM siwis WHERE username = ? ORDER BY created_at DESC', (session['username'],))
    siwis = cursor.fetchall()
    conn.close()

    return render_template('home.html', siwis=siwis)


# Edit SIWI route
@app.route('/edit_siwi/<int:siwi_id>', methods=['GET', 'POST'])
def edit_siwi(siwi_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM siwis WHERE id = ?', (siwi_id,))
    siwi = cursor.fetchone()

    if siwi['username'] != session['username']:
        flash('You are not authorized to edit this SIWI.', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        siwi_text = request.form['siwi_text']
        cursor.execute('UPDATE siwis SET siwi_text = ? WHERE id = ?', (siwi_text, siwi_id))
        conn.commit()
        conn.close()
        flash('SIWI updated successfully!', 'success')
        return redirect(url_for('home'))

    conn.close()
    return render_template('siwi.html', siwi=siwi)


# Delete SIWI route
@app.route('/delete_siwi/<int:siwi_id>', methods=['POST'])
def delete_siwi(siwi_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM siwis WHERE id = ?', (siwi_id,))
    siwi = cursor.fetchone()

    if siwi['username'] != session['username']:
        flash('You are not authorized to delete this SIWI.', 'error')
    else:
        cursor.execute('DELETE FROM siwis WHERE id = ?', (siwi_id,))
        conn.commit()
        flash('SIWI deleted successfully!', 'success')

    conn.close()
    return redirect(url_for('home'))


# Main function to run the application
if __name__ == '__main__':
    app.run(debug=True)