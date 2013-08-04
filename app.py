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










@app.route('/')
def main():
    print "main 123:", g.user
    return render_template('index.html')


@app.route('/item/<item_id>')
def item(item_id=None):
    print "item:", item_id
    session['item_id'] = item_id
    rv = query_db('''select * from item where item_id = ?''', [item_id], one=True)
    item_name = rv['item_name']
    item_picture_url = rv['item_picture_url']

    reviews = query_db('''
        select review.text as text, user.name as user_name,

        CASE WHEN review.size = 1 THEN 'Feels tight'
        WHEN review.size = 2 THEN 'Perfect'
        WHEN review.size = 3 THEN 'Fits wide'
        END AS size_text,

        CASE WHEN review.length = 1 THEN 'Short'
        WHEN review.length = 2 THEN 'Right'
        WHEN review.length = 3 THEN 'Long'
        END AS length_text,

        CASE WHEN review.thickness = 1 THEN 'Thin'
        WHEN review.thickness = 2 THEN 'Medium'
        WHEN review.thickness = 3 THEN 'Thick'
        END AS thickness_text,

        CASE WHEN review.quality = 1 THEN 'Cheap quality'
        WHEN review.quality = 2 THEN 'Ok'
        WHEN review.quality = 3 THEN 'High quality'
        END AS quality_text,

        CASE WHEN review.recommend = 1 THEN 'Do not recommend'
        WHEN review.recommend = 2 THEN 'Highly recommend'
        END AS recommend_text

        from user
        join
        (select * from review where item_id = ?) review
        on (user.user_id = review.user_id)''', [item_id])

    
    agg = query_db('''
        select avg(size)/3.0*100 as size, avg(length)/3.0*100 as length,
         avg(thickness)/3.0*100 as thickness, avg(quality)/3.0*100 as quality, avg(recommend)/3.0*100 as recommend
        from review where item_id = ?
        ''', [item_id])
    print "==============agg:", agg
    aggregator = {}
    aggregator['size_low'], aggregator['size_high'] = get_slider_bounds(agg[0][0])
    aggregator['length_low'], aggregator['length_high'] = get_slider_bounds(agg[0][1])
    aggregator['thickness_low'], aggregator['thickness_high'] = get_slider_bounds(agg[0][2])
    aggregator['quality_low'], aggregator['quality_high'] = get_slider_bounds(agg[0][3])
    aggregator['recommend_low'], aggregator['recommend_high'] = get_slider_bounds(agg[0][4])
    print "==============agg:", aggregator
    return render_template('item.html', item_id=item_id, item_name=item_name, item_picture_url=item_picture_url, reviews=reviews, aggregator=aggregator)

def get_slider_bounds(agg):
    low = agg - 2
    high = agg + 2
    if low < 0:
        low = 0
    if high > 100:
        high = 100
    low_str = "width:" + str(low) + "%; background:#f2f2f2"
    high_str = "width:" + str(high) + "%"
    return (low_str, high_str)

@app.route('/add_review', methods=['POST'])
def add_review():
    print 'add review heree'
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        print "form: ", request.form

        db = get_db()
        db.execute('''insert into review (item_id, user_id, date, text, size, length, thickness, quality, recommend)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    [session['item_id'],
                    session['user_id'], 
                    int(time.time()),
                    request.form['text'],
                    request.form['size'],
                    request.form['length'],
                    request.form['thickness'],
                    request.form['quality'],
                    request.form['recommend']
                    ]
                    )
        print 'boing'
        print request.form['text']
        print 'done boing'
        db.commit()
    print "*(*(* add_review done, fail"
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
