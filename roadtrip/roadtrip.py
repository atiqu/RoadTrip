# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker

app = Flask(__name__) # create the application instance :)
Bootstrap(app)
datepicker(app)

app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'roadtrip.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('ROADTRIP_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')






@app.route('/dp')
def dp():
    return render_template("dp.html")



@app.route('/add_activity', methods=['POST'])
def add_activity():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    start_date_time = "{date} {time}".format(
        date=request.form['start_time'],
        time=request.form['start_time_select']
    )
    end_date_time = "{date} {time}".format(
        date=request.form['end_time'],
        time=request.form['end_time_select']
    )
    db.execute('insert into activities (title, text, start_time, end_time) values (?, ?, ?, ?)',
                 [
                     request.form['title'],
                     request.form['text'],
                     start_date_time,
                     end_date_time
                 ]
               )
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_activities'))

@app.route('/')
def show_activities():
    db = get_db()
    cur = db.execute('select title, text, start_time, end_time from activities order by id desc')
    activities = cur.fetchall()
    return render_template('show_activities.html', activities=activities)















@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_activities'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_activities'))
