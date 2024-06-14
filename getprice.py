# From CoinMarketCap API

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

def main():
    print(getprice("BTCYY"))

def getprice(symbol, currency='USD'):
    symbol = symbol.upper()
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {
    # Alternatively pass one or more comma-separated cryptocurrency symbols. 
    # Example: "BTC,ETH". At least one "id" or "slug" or "symbol" is required for this request.
    
    'symbol':symbol,
    'convert': currency
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'b3028f13-8f41-4071-8d18-d7a265784995',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = response.json()
        price = data['data'][symbol][0]['quote'][currency]['price']
        return price
    except IndexError:
        return None
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
        return None

if __name__ == "__main__":
    main()