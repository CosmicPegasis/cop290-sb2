from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import json
app = Flask(__name__)
app.secret_key = 'your_secret_key' 


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 30)
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    favorites = db.Column(db.String)

# Initialize Database within Application Context
with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('index'))

    return render_template('register.html')

# @app.route('/forgot_password', methods=['POST'])
# def forgot_password():
#     username = request.form('username')
    

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect Password')
            return redirect(url_for('index'))
    else:
        flash('This Username is not registered')
        return redirect(url_for('index'))

@app.route('/dashboard',methods = ['Get','Post'])
def dashboard():
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)

        if request.method == 'POST':
            new_favorite = request.form.get('new_favorite')
            if new_favorite:
                favorites = json.loads(user.favorites) if user.favorites else []
                if len(favorites) < 4:
                    favorites.insert(0,new_favorite)
                    user.favorites = json.dumps(favorites)
                    db.session.commit()
                else:
                    favorites.pop(3)
                    favorites.insert(0,new_favorite)
                    user.favorites = json.dumps(favorites)
                    db.session.commit()

        if user:
        
            favorites = json.loads(user.favorites) if user.favorites else []
            
            return render_template('welcome.html', username=session['username'], favorites=favorites)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
