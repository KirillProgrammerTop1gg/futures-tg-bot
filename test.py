from config import BOT_TOKEN, BYBIT_KEYS, BINANCE_KEYS, OKX_KEYS
from exchanges_API import exchanges_API

exch_apis = exchanges_API(BINANCE_KEYS, BYBIT_KEYS, OKX_KEYS)

print(exch_apis.get_binance_info("XRP"))
print(exch_apis.get_bybit_info("XRP"))
