#This example uses Python 2.7 and the python-request library.

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
parameters = {
  'symbol':'BTC,ETH,ADA,USDT,BNB,SOL,MATIC,XRP,USDC',
  'convert': 'TWD'
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
  for coin in ['BTC', 'ETH', 'ADA', 'USDT']:
    print(coin + " : " + str(data['data'][coin][0]['quote']['TWD']['price']))
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)