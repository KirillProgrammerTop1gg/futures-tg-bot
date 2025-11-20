from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found")

BYBIT_KEYS = {
    "api_key": os.getenv("BYBIT_API_KEY"),
    "api_secret": os.getenv("BYBIT_API_SECRET"),
}

if not (BYBIT_KEYS["api_key"] and BYBIT_KEYS["api_secret"]):
    raise ValueError("BYBIT_KEYS not found")

BINANCE_KEYS = {
    "api_key": os.getenv("BINANCE_API_KEY"),
    "api_secret": os.getenv("BINANCE_API_SECRET"),
}
if not (BINANCE_KEYS["api_key"] and BINANCE_KEYS["api_secret"]):
    raise ValueError("BINANCE_KEYS not found")

OKX_KEYS = {
    "api_key": os.getenv("OKX_API_KEY"),
    "api_secret": os.getenv("OKX_API_SECRET"),
    "passphrase": os.getenv("OKX_API_PASSPHRASE"),
}
if not (OKX_KEYS["api_key"] and OKX_KEYS["api_secret"] and OKX_KEYS["passphrase"]):
    raise ValueError("OKX_KEYS not found")
