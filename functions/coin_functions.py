import requests
import os
import json
import asyncio
from dotenv import load_dotenv
import ccxt.async_support as ccxt

load_dotenv()


async def get_last_price(coin: str, currency: str = 'USD'):
    try:
        exchange = ccxt.binance()
        ticker = await exchange.fetch_ticker(f'{coin.upper()}/USDT')
        await exchange.close()
        return 200, ticker['last']
    except Exception as e:
        await exchange.close()
        return 404, ""


async def get_bid_price(coin: str, currency: str = 'USD'):
    try:
        exchange = ccxt.binance()
        ticker = await exchange.fetch_ticker(f'{coin.upper()}/USDT')
        await exchange.close()
        return 200, ticker['bid']
    except Exception as e:
        await exchange.close()
        return 404, ""


async def get_ask_price(coin: str, currency: str = 'USD'):
    try:
        exchange = ccxt.binance()
        ticker = await exchange.fetch_ticker(f'{coin.upper()}/USDT')
        await exchange.close()
        return 200, ticker['ask']
    except Exception as e:
        await exchange.close()
        return 404, ""
