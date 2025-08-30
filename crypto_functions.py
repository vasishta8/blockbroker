import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')


def get_price(coin_id: str):
    url = f'https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids={coin_id}'

    headers = {
        "accept": "application/json",
        "x-cg-pro-api-key": COINGECKO_API_KEY
    }

    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    try:
        return 200, response_dict[coin_id]["usd"]
    except KeyError as e:
        return 404, "The coin you requested was not found!"
