from flask import Flask, jsonify, render_template
from datetime import date
from dateutil.relativedelta import relativedelta
from jugaad_data.nse import stock_df, full_bhavcopy_raw
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Is vulnerable to HTML Injection
@app.route("/request/query/<stock_symbol>/<years>")
def get_stock_years(stock_symbol: str, years: int):
    df = stock_df(symbol=stock_symbol, from_date=date.today() - relativedelta(years=int(years)),
                to_date=date.today(), series="EQ")

    return jsonify(df.to_dict())


# Planning to use in the search function
# TODO Add checking for Sundays
import pandas as pd
import io
@app.route("/request/get_symbols/")
def get_symbols():
    df = pd.read_csv('./nifty50list.csv')['Symbol']
    s = io.StringIO(full_bhavcopy_raw(date.today() - relativedelta(days=2)))
    bhavcopy = pd.read_csv(s)
    bhavcopy.rename(columns=lambda x: x.strip(), inplace=True)
    bhavcopy = bhavcopy.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    bhavcopy = bhavcopy.set_index("SYMBOL")
    bhavcopy = bhavcopy[bhavcopy.index.isin(df.to_dict().values())]
    bhavcopy = bhavcopy[bhavcopy.SERIES == "EQ"]
  #  print(bhavcopy.to_string())
    return jsonify(bhavcopy.to_dict())

@app.route("/")
def index():
    return render_template("graph.html")