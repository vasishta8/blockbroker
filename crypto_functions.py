import requests
import os
import json
from dotenv import load_dotenv
import coinbase.wallet
from coinbase.wallet.client import Client

load_dotenv()
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')
client = Client(COINBASE_API_KEY, COINBASE_API_SECRET)


def get_spot_price(coin: str, currency: str = 'USD'):
    try:
        price = client.get_spot_price(currency_pair=f'{coin}-{currency}')
        print(price)
        return 200, price["amount"], price["base"], price["currency"]
    except coinbase.wallet.error.NotFoundError as e:
        return 404, -1, coin, currency


def get_buy_price(coin: str, currency: str = 'USD'):
    try:
        price = client.get_buy_price(currency_pair=f'{coin}-{currency}')
        print(price)
        return 200, price["amount"], price["base"], price["currency"]
    except coinbase.wallet.error.NotFoundError as e:
        print(e)
        return 404, -1, coin, currency


def get_sell_price(coin: str, currency: str = 'USD'):
    try:
        price = client.get_sell_price(currency_pair=f'{coin}-{currency}')
        print(price)
        return 200, price["amount"], price["base"], price["currency"]
    except coinbase.wallet.error.NotFoundError as e:
        return 404, -1, coin, currency
