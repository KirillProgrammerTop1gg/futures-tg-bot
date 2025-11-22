from config import BOT_TOKEN, BYBIT_KEYS, BINANCE_KEYS, OKX_KEYS
from exchanges_API import exchanges_API

exch_apis = exchanges_API(BINANCE_KEYS, BYBIT_KEYS, OKX_KEYS)
exch_apis.exchanges = ["bybit", "binance"]
exch_apis.symbol = "XRP"

print(exch_apis.get_prices())
print(exch_apis.get_contracts_info())
