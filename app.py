# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash

# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        print "before request, if"
        print "before request:", session['user_id']
        print g.user
        print session['user_id']
        
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)
        print "new user:", g.user
        if g.user is None:
            session['user_id'] = -1
    else:
        print "before request, else case"




# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url










@app.route('/main')
def main():
    print "main 123:", g.user
    return render_template('index.html')


@app.route('/item/<item_id>')
def item(item_id=None):
    session['item_id'] = item_id
    rv = query_db('''select * from item where item_id = ?''', [item_id], one=True)
    item_name = rv['item_name']
    item_picture_url = rv['item_picture_url']

    reviews = query_db('''select * from review where item_id = ?''', [item_id])
    print reviews

    return render_template('item.html', item_id=item_id, item_name=item_name, item_picture_url=item_picture_url, reviews=reviews)

@app.route('/add_review', methods=['POST'])
def add_review():
    print 'add review heree'
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into review (item_id, user_id, date, text, size, length, thickness, quality, recommend)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    [session['item_id'],
                    session['user_id'], 
                    int(time.time()),
                    request.form['text'],
                    50,
                    50,
                    50,
                    50,
                    0]
                    )
        print 'boing'
        print request.form['text']
        print 'done boing'
        db.commit()
    return redirect(url_for('item', item_id=session['item_id']))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Logs the user in."""
    print "entered signin"
    if g.user:
        return redirect(url_for('main'))
    error = None
    if request.method == 'POST':
        user = query_db('''
            select * from user 
            where email = ?
            ''', 
            [request.form['email']], 
            one=True)
        if user is None:
            error = 'User does not exist!'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Password does not match!'
        else:
            print "sign in: successfully"
            session['user_id'] = user['user_id']
            g.user = user
            print g.user
            return redirect(url_for('main'))
    print "signin error:", error
    return redirect(url_for('main'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Registers the user."""
    print "entered signup"
    error = None
    if request.method == 'POST':
        print "signup1"
        if not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password'] or not request.form['password2']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        else:
            print "signup5"
            user = query_db('''
                select * from user 
                where
                email = ?
                ''', 
                [request.form['email']], 
                one=True)
            if user is not None:
                error = 'Email already exists in the database.'
            elif not request.form['gender']:
                error = 'You have to enter your gender.'
            elif not request.form['height']:
                error = 'You have to enter your height.'
            elif not request.form['top']:
                error = 'You have to enter your top size.'
            elif not request.form['bottom']:
                error = 'You have to enter your bottom size.'
            elif not request.form['bust']:
                error = 'You have to enter your bust size.'
            elif not request.form['shoe_size']:
                error = 'You have to enter your shoe size.'
            else:
                db = get_db()

                db.execute('''insert into user (email, name, pw_hash, gender, height, top, bottom, bust, shoe_size) values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  [
                  request.form['email'], 
                  request.form['name'],
                  generate_password_hash(request.form['password']),
                  request.form['gender'],
                  request.form['height'], 
                  request.form['top'], 
                  request.form['bottom'], 
                  request.form['bust'], 
                  request.form['shoe_size']
                  ])
                db.commit()
                print "signup succesfull"
                return redirect(url_for('main'))
    print "signup ERROR:", error
    return render_template('signup.html', error=error)

if __name__ == '__main__':
    init_db()
    app.run()
