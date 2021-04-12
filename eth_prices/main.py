from flask import Flask, render_template
import requests
import os

#flask run
#set COINAPI_KEY=<your api>

print(__name__)
app = Flask(__name__)

def get_price_from_coingecko():
    r = requests.get('https://api.coingecko.com/api/v3/simple/price',
                     params={'ids': 'ethereum', 'vs_currencies': 'usd'})
    coingecko_price = 'Error'
    print(r.status_code)
    if r.status_code == 200:
        coingecko_price = f" $ {r.text.split(':')[2].rstrip('}')}"
    return coingecko_price

def get_price_from_cryptocompare():
    r = requests.get('https://min-api.cryptocompare.com/data/price', params={
        'fsym':'ETH', 'tsyms': 'USD'
    })
    cryptocompare_price = 'Error'
    print(r.status_code)
    if r.status_code == 200:
        cryptocompare_price = '$ ' + r.text.split(':')[1].rstrip('}')
    return cryptocompare_price

def get_price_from_coinapi():
    r = requests.get('https://rest.coinapi.io/v1/exchangerate/ETH/USD', headers={
        'X-CoinAPI-Key': os.getenv('COINAPI_KEY')
    })
    coinapi_price = 'Error'
    if r.status_code == 200:
        coinapi_price = float(r.json()['rate'])
        coinapi_price = round(coinapi_price, 2)
    return coinapi_price

@app.route('/')
@app.route('/home')
def homepage():
    coingecko_price = get_price_from_coingecko()
    cryptocompare_price = get_price_from_cryptocompare()
    coinapi_price = get_price_from_coinapi()
    return render_template('main.html', coingecko_price=coingecko_price,
                           cryptocompare_price=cryptocompare_price, coinapi_price=coinapi_price)

if __name__ == 'main' or __name__ == '__main__':
    r = requests.get('https://api.coingecko.com/api/v3/ping')
    if r.status_code != 200:
        exit()
    print(r.text)
