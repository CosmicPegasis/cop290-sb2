from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

def login(username, password):
    with app.app_context():
        if User.query.filter_by(name = username).first():
                if(User.query.filter_by(name = username,password = password).first()):
                    return 0 
                else:
                    return -1 
        else:
            return 1 


def sign_in(username, password):
    with app.app_context():
        if User.query.filter_by(name=username).first():
            return 1 
        else:
            new_user = User(name=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return 0 
        
print(login("Daksh97u78787878","124"))




