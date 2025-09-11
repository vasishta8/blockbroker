import pymongo, os
from dotenv import load_dotenv
import ccxt.async_support as ccxt
from cryptography.fernet import Fernet

load_dotenv()
ENCRYPTION_KEY = os.getenv("FERNET_ENCRYPTION_KEY").encode() 
cipher_suite = Fernet(ENCRYPTION_KEY)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
user_database = mongo_client["user_data"] 
api_keys_collection = user_database["binance_api_keys"]


def encrypt(string: str) -> str:
    return cipher_suite.encrypt(string.encode()).decode()


def decrypt(encrypted_string: str) -> str:
    return cipher_suite.decrypt(encrypted_string.encode()).decode()


async def set_binance_api_keys(user_id: str, api_key: str, secret_key: str):
    encrypted_api_key = encrypt(api_key)
    encrypted_secret_key = encrypt(secret_key)

    user_id_query = {"user_id": user_id}
    newValues = {"$set": {"api_key": encrypted_api_key, "secret_key": encrypted_secret_key}}

    if api_keys_collection.find_one(user_id_query):
        api_keys_collection.update_one(user_id_query, newValues)
    else:
        api_keys_collection.insert_one(
            {"user_id": user_id, "api_key": encrypted_api_key, "secret_key": encrypted_secret_key})


async def create_market_buy_order(user_id: str, coin: str, amount: float):
    user_id_query = {"user_id": user_id}
    user_doc = api_keys_collection.find_one(user_id_query)

    if not user_doc or "api_key" not in user_doc:
        return (404, "API Key not found")

    try:
        decrypted_api_key = decrypt(user_doc["api_key"])
        decrypted_secret_key = decrypt(user_doc["secret_key"])
    except Exception as e:
        return (500, f"Failed to decrypt keys: {e}")

    exchange = ccxt.binance({
        'apiKey': decrypted_api_key,
        'secretKey': decrypted_secret_key 
    })
    try:
        order = await exchange.create_market_buy_order(f'{coin}/USDT', amount)
        return (200, order)
    except Exception as e:
        return (500, f"Failed to create order: {e}")
    finally:
        await exchange.close()


async def create_limit_buy_order(user_id: str, coin: str, amount: float, price: float):
    user_id_query = {"user_id": user_id}
    user_doc = api_keys_collection.find_one(user_id_query)

    if not user_doc or "api_key" not in user_doc or "secret_key" not in user_doc:
        return (404, "Key not found")

    try:
        decrypted_api_key = decrypt(user_doc["api_key"])
        decrypted_secret_key = decrypt(user_doc["secret_key"])
    except Exception as e:
        return (500, f"Failed to decrypt API key: {e}")

    exchange = ccxt.binance({
        'apiKey': decrypted_api_key,
        'secretKey': decrypted_secret_key
    })
    try:
        order = await exchange.create_order(f'{coin}/USDT', 'limit', 'buy', amount, price)
        return (200, order)
    except Exception as e:
        return (500, f"Failed to create order: {e}")
    finally:
        await exchange.close()
