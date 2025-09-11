import pymongo
import ccxt.async_support as ccxt
from cryptography.fernet import Fernet

# In a real application, load this from a secure location (e.g., environment variable, secrets manager)
# For demonstration, we'll use a fixed key.
# You can generate a key using: Fernet.generate_key()

ENCRYPTION_KEY = b'YOUR_GENERATED_ENCRYPTION_KEY_HERE='  
cipher_suite = Fernet(ENCRYPTION_KEY)

tradingClient = pymongo.MongoClient("mongodb://localhost:27017/")
tradingDb = tradingClient["tradingDatabase"]
tradingTable = tradingDb["tradingTable"]


def encrypt(string: str) -> str:
    return cipher_suite.encrypt(string.encode()).decode()


def decrypt(encrypted_string: str) -> str:
    return cipher_suite.decrypt(encrypted_string.encode()).decode()


async def set_binance_api_key(user_id: str, api_key: str):
    encrypted_api_key = encrypt(api_key)

    tradingQuery = {"user_id": user_id}
    newValues = {"$set": {"api_key": encrypted_api_key}}

    if tradingTable.find_one(tradingQuery):
        tradingTable.update_one(tradingQuery, newValues)
    else:
        tradingTable.insert_one(
            {"user_id": user_id, "api_key": encrypted_api_key})


async def create_market_buy_order(user_id: str, coin: str, amount: float):
    tradingQuery = {"user_id": user_id}
    user_doc = tradingTable.find_one(tradingQuery)

    if not user_doc or "api_key" not in user_doc:
        return (404, "API Key not found")

    try:
        decrypted_api_key = decrypt(user_doc["api_key"])
    except Exception as e:
        return (500, f"Failed to decrypt API key: {e}")

    exchange = ccxt.binance({
        'apiKey': decrypted_api_key,
        # 'secret': 'YOUR_SECRET_KEY' 
    })
    try:
        order = await exchange.create_market_buy_order(f'{coin}/USDT', amount)
        return (200, order)
    except Exception as e:
        return (500, f"Failed to create order: {e}")
    finally:
        await exchange.close()


async def create_limit_buy_order(user_id: str, coin: str, amount: float, price: float):
    tradingQuery = {"user_id": user_id}
    user_doc = tradingTable.find_one(tradingQuery)

    if not user_doc or "api_key" not in user_doc:
        return (404, "API Key not found")

    try:
        decrypted_api_key = decrypt(user_doc["api_key"])
    except Exception as e:
        return (500, f"Failed to decrypt API key: {e}")

    exchange = ccxt.binance({
        'apiKey': decrypted_api_key,
        # 'secret': 'YOUR_SECRET_KEY'
    })
    try:
        order = await exchange.create_order(f'{coin}/USDT', 'limit', 'buy', amount, price)
        return (200, order)
    except Exception as e:
        return (500, f"Failed to create order: {e}")
    finally:
        await exchange.close()
