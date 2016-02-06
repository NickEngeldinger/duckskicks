import sqlite3
import os

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from werkzeug import secure_filename

# configuration
# export to ini and then import values
DATABASE = '/tmp/duckskicks.db'
DEBUG = True
SECRET_KEY = 'vnX988GH3KMv-bTN6bP#M"#iM9.9W;'
USERNAME = 'admin'
PASSWORD = 'default'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/sneakers')
def show_sneakers():
	cur = g.db.execute('select name, slug, description from sneakers order by id desc')
	sneakers = [dict(name=row[0], slug=row[1], description=row[2]) for row in cur.fetchall()]
	return render_template('sneakers.html', sneakers=sneakers)

@app.route('/add', methods=['POST'])
def add_sneaker():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into sneakers (name, slug, description) values (?, ?, ?)',
                 [request.form['name'], request.form['slug'], request.form['description']])
    g.db.commit()
    flash('New sneaker was successfully added!')
    return redirect(url_for('show_sneakers'))

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
            return redirect(url_for('show_sneakers'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_sneakers'))

@app.route('/new_sneaker')
def new_sneaker():
    return render_template('new_sneaker.html')

# DO THESE LIKE LOGIN WITH GET POST CHECKS AND USE FOR BOTH VIEW AND ACTION

@app.route('/add_image', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #return redirect(url_for('uploaded_file', filename=filename))
        flash('Image uploaded successfuly')
        return redirect(url_for('new_image'))

@app.route('/new_image')
def new_image():
    return render_template('new_image.html')    

if __name__ == "__main__":
    app.run(debug = True)