from dateutil.relativedelta import relativedelta
from jugaad_data.nse import stock_df
import pandas as pd
from datetime import datetime

def calculate_rsi(data, period=14):
    data['Delta'] = data['CLOSE'] - data['PREV. CLOSE']
    gains = data['Delta'].apply(lambda x: max(0, x))
    losses = -(data['Delta'].apply(lambda x: min(0, x)))
    data['AvgGain'] = gains.rolling(window=period, min_periods=3).mean()
    data['AvgLoss'] = losses.rolling(window=period, min_periods=3).mean()
    data['RS'] = data['AvgGain'] / data['AvgLoss']
    data['RSI'] = 100 - (100 / (1 + data['RS']))

    return data

def get_stock_data(valid_stocks):
    end_date = datetime.now().date()
    start_date = end_date - relativedelta(weeks = 2)
    ans_df = pd.DataFrame()
        
    for stock_symbol in valid_stocks:
        df_temp = stock_df(symbol=stock_symbol, from_date=start_date, to_date=end_date, series="EQ")
        #print(stock_symbol)
        df_temp = calculate_rsi(df_temp)
        df_temp['RSI'] = df_temp.at[df_temp['RSI'].first_valid_index(),'RSI']
        #print(df_temp['RSI'])
        ans_df = pd.concat([ans_df, df_temp.head(1)], ignore_index=True)
        
    return ans_df

def filter_out(ans_df,minCP,maxCP,minRSI,maxRSI,minAP,maxAP,minVV,maxVV):
    ans_df = ans_df[(ans_df['CLOSE'] >= int(minCP))]
    ans_df = ans_df[(ans_df['CLOSE'] <= int(maxCP))]
    ans_df = ans_df[(ans_df['RSI'] >= int(minRSI))]
    ans_df = ans_df[(ans_df['RSI'] <= int(maxRSI))]
    ans_df = ans_df[(ans_df['HIGH'] + ans_df['LOW']) / 2 >= int(minAP)]
    ans_df = ans_df[(ans_df['HIGH'] + ans_df['LOW']) / 2 <= int(maxAP)]
    ans_df = ans_df[(ans_df['VALUE'] / ans_df['VOLUME']) >= int(minVV)]
    ans_df = ans_df[(ans_df['VALUE'] / ans_df['VOLUME']) <= int(maxVV)]
    ans_df['DELTA'] = ((ans_df['CLOSE']-ans_df['OPEN'])/ans_df['OPEN'])*100
    ans_df = ans_df.drop(['SERIES', 'PREV. CLOSE', 'VWAP', '52W H', '52W L', 'Delta', 'AvgGain', 'AvgLoss',
                          'LTP', 'NO OF TRADES', 'RS', 'RSI','CLOSE','DATE','CLOSE','OPEN','VALUE','VOLUME','HIGH','LOW'], axis=1)
    
    return ans_df

def favorite_filter(favorites,ans_df):
    close_price =[]
    delta =[]
    #print(ans_df['SYMBOL'])
    #print(ans_df['SYMBOL'] == 'MARUTI')
    for stock_symbol in favorites:
        cl = round(ans_df[ans_df['SYMBOL'] == stock_symbol]['CLOSE'].iloc[0],2)
        #print(cl)
        de = round(ans_df[ans_df['SYMBOL'] == stock_symbol]['DELTA'].iloc[0],2)
        close_price = close_price +[cl]
        delta = delta+[de]
        
    return (close_price, delta)
    