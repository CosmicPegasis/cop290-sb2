from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from jugaad_data.nse import stock_df, full_bhavcopy_raw
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import io
import json
import ast

from datetime import datetime
import time

app = Flask(__name__)
CORS(app)
# Is vulnerable to HTML Injection
@app.route("/request/query/<stock_symbol>/years/<years>")
def get_stock_years(stock_symbol: str, years: int):
    df = stock_df(symbol=stock_symbol, from_date=date.today() - relativedelta(years=int(years)),
                to_date=date.today(), series="EQ")

    return jsonify(df.to_dict())

@app.route("/request/query/<stock_symbol>/weeks/<weeks>")
def get_stock_weeks(stock_symbol: str, weeks: int):
    df = stock_df(symbol=stock_symbol, from_date=date.today() - relativedelta(weeks=int(weeks)),
                to_date=date.today(), series="EQ")

    return jsonify(df.to_dict())

@app.route("/request/query/<stock_symbol>/days/<days>")
def get_stock_days(stock_symbol: str, days: int):
    df = stock_df(symbol=stock_symbol, from_date=date.today() - relativedelta(days=int(days)),
                to_date=date.today(), series="EQ")

    return jsonify(df.to_dict())

# Planning to use in the search function
# TODO Add checking for Sundays
@app.route("/request/get_symbols/")
def get_symbols():
    symbol_list = get_symbol_list()
    s = io.StringIO(full_bhavcopy_raw(date.today() - relativedelta(days=1)))
    bhavcopy = pd.read_csv(s)
    bhavcopy.rename(columns=lambda x: x.strip(), inplace=True)
    bhavcopy = bhavcopy.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    bhavcopy = bhavcopy.set_index("SYMBOL")
    bhavcopy = bhavcopy[bhavcopy.index.isin(symbol_list)]
    bhavcopy = bhavcopy[bhavcopy.SERIES == "EQ"]
    return jsonify(bhavcopy.to_dict())


def get_symbol_list():
    return pd.read_csv('./nifty50list.csv')['Symbol'].to_dict().values()

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
        confirm_password = request.form['confirm_password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        if(' ' in username):
            flash('Username cannot contain spaces')
            return redirect(url_for('register'))
        else:
            if not any (ch.isupper() for ch in password):
                flash('Password must contain one uppercase letter')
                return redirect(url_for('register'))
            else:
                if not any(ch.islower() for ch in password):
                    flash('Password must contain one lowercase letter')
                    return redirect(url_for('register'))
                else:
                    if not any(ch.isalnum() for ch in password):
                        flash('Password must contain one special character')
                        return redirect(url_for('register'))
                    else:
                        user = User.query.filter_by(username=username).first()
                        if user:
                            flash('An account with this username already exists')
                            return redirect(url_for('register'))
                        else:
                            if(confirm_password == password):
                                new_user = User(username=username, password_hash=hashed_password)
                                db.session.add(new_user)
                                db.session.commit()
                                return redirect(url_for('index'))
                            else:
                                flash('Password does not match!')
                                return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            if('remember_me' in request.form):
                session.permanent = True
            else:
                session.permanent = False
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect Password')
            return redirect(url_for('index'))
    else:
        flash('This Username is not registered')
        return redirect(url_for('index'))

@app.route('/dashboard',methods = ['GET','POST'])
def dashboard():
    user_id = session.get('user_id')
    valid_stocks = get_symbol_list()
    

    if user_id:
        user = User.query.get(user_id)

        end_date = datetime.now().date()
        start_date = end_date - relativedelta(weeks = 2)
        valid_stocks = get_symbol_list()
        ans_df = pd.DataFrame()
        
        for stock_symbol in valid_stocks:
            
            df_temp = stock_df(symbol=stock_symbol, from_date=start_date, to_date=end_date, series="EQ")
            print(stock_symbol)
            df_temp = calculate_rsi(df_temp)
            df_temp['RSI'] = df_temp.at[df_temp['RSI'].first_valid_index(),'RSI']
            print(df_temp['RSI'])
            
            ans_df = pd.concat([ans_df, df_temp.head(1)], ignore_index=True)
        
        ans_df['DELTA'] = ((ans_df['CLOSE']-ans_df['OPEN'])/ans_df['OPEN'])*100
                
        if request.method == 'POST':
            new_favorite = request.form.get('new_favorite')
            
            
            if new_favorite in valid_stocks:
                favorites = json.loads(user.favorites) if user.favorites else []

                if(new_favorite in favorites):
                    flash('stock already exists in favorites')
                    return redirect(url_for('dashboard'))
                
                if len(favorites)>=4:
                    favorites.pop(3)
                    
                favorites.insert(0,new_favorite)
                user.favorites = json.dumps(favorites)
                db.session.commit()
            else:
                flash('stock does not exists in database')
                return redirect(url_for('dashboard'))

        if user:
            close_price =[]
            delta =[]
            
            
            favorites = ast.literal_eval(user.favorites) if user.favorites else []
            print(ans_df['SYMBOL'])
            print(ans_df['SYMBOL'] == 'MARUTI')
            for stock_symbol in favorites:
                cl = round(ans_df[ans_df['SYMBOL'] == stock_symbol]['CLOSE'].iloc[0],2)
                print(cl)
                de = round(ans_df[ans_df['SYMBOL'] == stock_symbol]['DELTA'].iloc[0],2)
                close_price = close_price +[cl]
                delta = delta+[de]
                
            
            combined_array = list(zip(close_price,delta,favorites))
            print(delta)
            print(close_price)
            return render_template('welcome.html', username=session['username'], favorites=favorites,combined_array = combined_array)

    return redirect(url_for('index'))

@app.route('/remove_favorite/<favorite>', methods=['POST'])
def remove_favorite(favorite):
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)

        if user:
            favorites = json.loads(user.favorites) if user.favorites else []

            if favorite in favorites:
                favorites.remove(favorite)
                user.favorites = json.dumps(favorites)
                db.session.commit()
            else:
                flash('This Favorite does not exists.')

    return redirect(url_for('dashboard'))

@app.route('/graph')
def graph():
    user_id = session.get('user_id')
    if user_id:
        return render_template('graph.html',username=session['username'])
    else:
        return redirect(url_for('index'))

def calculate_rsi(data, period=14):
    data['Delta'] = data['CLOSE'] - data['PREV. CLOSE']
    gains = data['Delta'].apply(lambda x: max(0, x))
    losses = -(data['Delta'].apply(lambda x: min(0, x)))
    data['AvgGain'] = gains.rolling(window=period, min_periods=3).mean()
    data['AvgLoss'] = losses.rolling(window=period, min_periods=3).mean()
    data['RS'] = data['AvgGain'] / data['AvgLoss']
    data['RSI'] = 100 - (100 / (1 + data['RS']))

    return data







@app.route('/filter', methods=['GET', 'POST'])
def filter():
    user_id = session.get('user_id')
    
    if user_id:
        minCP = request.form.get('minClosePrice', default=0)
        maxCP = request.form.get('maxClosePrice', default=4000)
        minRSI = request.form.get('minRelativeStrength', default=0)
        maxRSI = request.form.get('maxRelativeStrength', default=100)
        minAP = request.form.get('minAveragePrice', default=0)
        maxAP = request.form.get('maxAveragePrice', default=4000)
        minVV = request.form.get('minValVolRatio', default=0)
        maxVV = request.form.get('maxValVolRatio', default=100000)
        
        end_date = datetime.now().date()
        start_date = end_date - relativedelta(weeks = 2)
        valid_stocks = get_symbol_list()
        ans_df = pd.DataFrame()
        
        for stock_symbol in valid_stocks:
            len_symbol = len(stock_symbol)
            df_temp = stock_df(symbol=stock_symbol, from_date=start_date, to_date=end_date, series="EQ")
            print(stock_symbol)
            df_temp = calculate_rsi(df_temp)
            df_temp['RSI'] = df_temp.at[df_temp['RSI'].first_valid_index(),'RSI']
            print(df_temp['RSI'])
            df_temp['SYMBOL'] = stock_symbol+ (" "*(11-len_symbol))
            ans_df = pd.concat([ans_df, df_temp.head(1)], ignore_index=True)
            
        
            
        if request.method == 'POST':
            
            minCP = request.form["minClosePrice"]
            maxCP = request.form["maxClosePrice"]
            minRSI = request.form["minRelativeStrength"]
            maxRSI = request.form["maxRelativeStrength"]
            minAP = request.form["minAveragePrice"]
            maxAP = request.form["maxAveragePrice"]
            minVV = request.form["minValVolRatio"]
            maxVV = request.form["maxValVolRatio"]
            
            
            ans_df = ans_df[(ans_df['CLOSE'] >= int(minCP))]
            ans_df = ans_df[(ans_df['CLOSE'] <= int(maxCP))]
            ans_df = ans_df[(ans_df['RSI'] >= int(minRSI))]
            ans_df = ans_df[(ans_df['RSI'] <= int(maxRSI))]
            ans_df = ans_df[(ans_df['HIGH'] + ans_df['LOW']) / 2 >= int(minAP)]
            ans_df = ans_df[(ans_df['HIGH'] + ans_df['LOW']) / 2 <= int(maxAP)]
            ans_df = ans_df[(ans_df['VALUE'] / ans_df['VOLUME']) >= int(minVV)]
            ans_df = ans_df[(ans_df['VALUE'] / ans_df['VOLUME']) <= int(maxVV)]
            
            if not ans_df.empty:
                ans_df['DELTA'] = ((ans_df['CLOSE']-ans_df['OPEN'])/ans_df['OPEN'])*100
                ans_df = ans_df.drop(['SERIES', 'PREV. CLOSE', 'VWAP', '52W H', '52W L', 'Delta', 'AvgGain', 'AvgLoss',
                                      'LTP', 'NO OF TRADES', 'RS', 'RSI','CLOSE','DATE','CLOSE','OPEN','VALUE','VOLUME','HIGH','LOW'], axis=1)
                
                ans_df = ans_df.to_dict(orient='records')
                return render_template('filter.html',username=session['username'], top_4_rows=ans_df,minCP = minCP,maxCP = maxCP,minRSI = minRSI,maxRSI = maxRSI,minVV = minVV,maxVV = maxVV,minAP = minAP,maxAP = maxAP)
            else:
                return render_template('filter.html', username=session['username'],top_4_rows=None,minCP = minCP,maxCP = maxCP,minRSI = minRSI,maxRSI = maxRSI,minVV = minVV,maxVV = maxVV,minAP = minAP,maxAP = maxAP)
            
        else:
            ans_df['DELTA'] = ((ans_df['CLOSE']-ans_df['OPEN'])/ans_df['OPEN'])*100
            ans_df = ans_df.drop(['SERIES', 'PREV. CLOSE', 'VWAP', '52W H', '52W L', 'Delta', 'AvgGain', 'AvgLoss',
                                  'LTP', 'NO OF TRADES', 'RS', 'RSI','CLOSE','DATE','CLOSE','OPEN','VALUE','VOLUME','HIGH','LOW'], axis=1)
            ans_df = ans_df.to_dict(orient='records')
            print("Username:", session['username'])
            return render_template('filter.html',top_4_rows = ans_df,username=session['username'],minCP = minCP,maxCP = maxCP,minRSI = minRSI,maxRSI = maxRSI,minVV = minVV,maxVV = maxVV,minAP = minAP,maxAP = maxAP)
    else:
        return redirect(url_for('index'))
    
@app.route('/test', methods =["GET", "POST"])
def test():
    if request.method == "POST":
      
       first_name = request.form.get("fname")
        
       last_name = request.form.get("lname") 
       return "Your name is "+first_name + last_name
    return render_template("form.html")


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
