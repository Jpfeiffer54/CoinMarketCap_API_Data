from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import os 
from time import time
from time import sleep

pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows',None)
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
'start':'1',
'limit':'20',
'convert':'USD'
}
headers = {
'Accepts': 'application/json',
'X-CMC_PRO_API_KEY': '[API Key]',
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    #print(data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

df = pd.json_normalize(data['data'])
df['timestamp'] = pd.to_datetime('now')
#print(df)

# API pull function and data storage to csv
def api_runner():
    global df
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'20',
    'convert':'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '[API KEY]',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
     #print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    df = pd.json_normalize(data['data'])
    df['timestamp'] = pd.to_datetime('now')
    

    if not os.path.isfile(r"C:\PythonVSCode\Python Scripts\CryptoAPI.csv"):
        df.to_csv(r"C:\PythonVSCode\Python Scripts\CryptoAPI.csv",header='column_names')
    else:
        df.to_csv(r"C:\PythonVSCode\Python Scripts\CryptoAPI.csv",header=False,mode='a')
    return df

#initialize empty list
dfs = []

# api pull loop   
for i in range(24):
    df_new = api_runner()
    dfs += [df_new]
    print('API runner completed successfully')
    
    # Concatenating all the dataframes
    df = pd.concat(dfs,ignore_index=True)

    # Reodering Data into a clean Dataframe
    df2 = df.groupby('name',sort=False)[['quote.USD.percent_change_1h','quote.USD.percent_change_24h','quote.USD.percent_change_7d','quote.USD.percent_change_30d','quote.USD.percent_change_60d','quote.USD.percent_change_90d']].mean()
    df2 = df2.stack()
    df2 = df2.to_frame(name = "values")
    index = pd.Index(range(90))
    df2 = df2.reset_index()
    df2 = df2.rename(columns = {'level_1':'percent_change','values':'value'})
    df2['percent_change'] = df2['percent_change'].replace({'quote.USD.percent_change_1h':'1 Hour','quote.USD.percent_change_24h':'1 Day','quote.USD.percent_change_7d':'1 Week','quote.USD.percent_change_30d':'1 Month','quote.USD.percent_change_60d':'2 Months','quote.USD.percent_change_90d':'3 Months'})
    #print(df2)

    # percentage change graph
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.catplot(x='percent_change',y='value',data=df2, hue = 'name',kind='point',height=5,aspect=2)
    plt.show()

    df3 = df[['name','quote.USD.price', 'timestamp']]
    df3 = df3.query('name == "Bitcoin"')
    #print(df3)


    # price graph for bitcoin
    sns.set_theme(style='darkgrid')
    sns.lineplot(x='timestamp',y='quote.USD.price',data=df3)
    plt.show()
    
    sleep(3600)
