from binance.um_futures import UMFutures
import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.PublicData as PublicData
from pybit.unified_trading import HTTP
from typing import Optional, Union, Dict, List
import okx.Account as Account
import asyncio
import time


class exchanges_API:
    @staticmethod
    def get_time_now() -> str:
        return time.strftime("%H:%M:%S")

    @staticmethod
    def format_time_now() -> str:
        t = exchanges_API.get_time_now()
        return f"Час оновлення: {t}\n\n"

    @staticmethod
    def format_query(s: str) -> str:
        return s.lower().replace(" ", "")

    @staticmethod
    def format_token_contract_info(
        exchange: str, symb: str, min_qty: str, max_qty: str, step_qty: str
    ) -> str:
        return (
            f"Інформація про {symb} {exchange} контракт:\n"
            f"  Мінімальний обсяг: {min_qty}\n"
            f"  Максимальний обсяг: {max_qty}\n"
            f"  Розрядність: {step_qty}"
        )

    def __init__(
        self,
        BINANCE_KEYS: Dict[str, str],
        BYBIT_KEYS: Dict[str, str],
        OKX_KEYS: Dict[str, str],
    ):
        self.binance_client = UMFutures(
            key=BINANCE_KEYS["api_key"], secret=BINANCE_KEYS["api_secret"]
        )
        self.bybit_client = HTTP(
            api_key=BYBIT_KEYS["api_key"], api_secret=BYBIT_KEYS["api_secret"]
        )
        self.okx_trade_client = Trade.TradeAPI(
            OKX_KEYS["api_key"],
            OKX_KEYS["api_secret"],
            OKX_KEYS["passphrase"],
            False,
            "0",
        )
        self.okx_market_client = MarketData.MarketAPI(flag="0")
        self.okx_public_client = PublicData.PublicAPI(flag="0")
        self._symb = ""
        self._exchanges = []

    @property
    def symbol(self) -> str:
        return self._symb

    @symbol.setter
    def symbol(self, new_symbol: str) -> None:
        self._symb = new_symbol

    @property
    def exchanges(self) -> List[str]:
        return self._exchanges

    @exchanges.setter
    def exchanges(self, new_exchanges: List[str]) -> None:
        self._exchanges = new_exchanges

    def clean_info(self) -> None:
        self._exchanges = []
        self._symb = ""

    def is_enough_info(self) -> bool:
        return bool(self._symb) and bool(len(self._exchanges))

    def get_binance_contract_info(self) -> str:
        symbol = self._symb
        assets = self.binance_client.exchange_info()["symbols"]

        for asset in assets:
            if asset["symbol"] == f"{symbol}USDT":
                contract_info = asset["filters"][2]
                return self.format_token_contract_info(
                    "binance",
                    symbol,
                    contract_info["minQty"],
                    contract_info["maxQty"],
                    contract_info["stepSize"],
                )

    def get_bybit_contract_info(self) -> str:
        symbol = self._symb
        contract_info = self.bybit_client.get_instruments_info(
            category="linear", symbol=f"{symbol}USDT"
        )["result"]["list"][0]["lotSizeFilter"]

        return self.format_token_contract_info(
            "bybit",
            symbol,
            contract_info["minOrderQty"],
            contract_info["maxOrderQty"],
            contract_info["qtyStep"],
        )

    def get_okx_contract_info(self) -> str:
        symbol = self._symb
        contract_info = self.okx_public_client.get_instruments(
            instType="SWAP", instId=f"{symbol}-USDT-SWAP"
        )["data"][0]

        return self.format_token_contract_info(
            "okx",
            symbol,
            contract_info["minSz"],
            contract_info["maxLmtSz"],
            contract_info["lotSz"],
        )

    def one_contract_info(self, exchange: str) -> str:
        if self.format_query(exchange) == "binance":
            return self.get_binance_contract_info()
        elif self.format_query(exchange) == "bybit":
            return self.get_bybit_contract_info()
        elif self.format_query(exchange) == "okx":
            return self.get_okx_contract_info()

    def get_contracts_info(self) -> str:
        return (
            f"Інформація про контракти токенів на біржах:\n"
            f"{self.format_time_now()}"
            f"{self.one_contract_info(self._exchanges[0])}\n\n"
            f"{self.one_contract_info(self._exchanges[1])}"
        )

    def get_binance_prices(self) -> List[float]:
        symbol = self._symb
        prices = self.binance_client.depth(f"{symbol}USDT", **{"limit": 5})
        return prices["asks"][0][0], prices["bids"][0][0]

    def get_bybit_prices(self) -> List[float]:
        symbol = self._symb
        prices = self.bybit_client.get_orderbook(
            category="linear", symbol=f"{symbol}USDT"
        )["result"]
        return prices["a"][0][0], prices["b"][0][0]

    def get_okx_prices(self) -> List[float]:
        symbol = self._symb
        prices = self.okx_market_client.get_orderbook(instId=f"{symbol}-USDT-SWAP")[
            "data"
        ][0]
        return prices["asks"][0][0], prices["bids"][0][0]

    def get_one_prices(self, exchange: str):
        symbol = self._symb
        if self.format_query(exchange) == "binance":
            max_price, min_price = self.get_binance_prices()
        elif self.format_query(exchange) == "bybit":
            max_price, min_price = self.get_bybit_prices()
        elif self.format_query(exchange) == "okx":
            max_price, min_price = self.get_okx_prices()

        return (
            f"Токен {symbol} на біржі {exchange}:\n"
            f"  (LONG) Купляєте токен за {max_price} USDT ({max_price} USDT -> 1 {symbol})\n"
            f"  (SHORT) Продаєте токен за {min_price} USDT (1 {symbol} -> {min_price} USDT)"
        )

    def get_prices(self):
        return (
            f"Інформація про ціни токена на різних біржах:\n"
            f"{self.format_time_now()}"
            f"{self.get_one_prices(self._exchanges[0])}\n\n"
            f"{self.get_one_prices(self._exchanges[1])}"
        )

    def place_binance_order(self, qty: float, side: str) -> dict:
        params = {
            "symbol": f"{self._symb}USDT",
            "side": "SELL" if side == "short" else "BUY",
            "type": "MARKET",
            "quantity": qty,
        }
        order = self.binance_client.new_order(**params)
        return order

    def place_bybit_order(self, qty: float, side: str) -> dict:
        order = self.bybit_client.place_order(
            category="linear",
            symbol=f"{self._symb}USDT",
            side="Sell" if side == "short" else "Buy",
            orderType="Market",
            qty=qty,
        )
        return order

    def place_okx_order(self, qty: float, side: str) -> dict:
        order = self.okx_trade_client.place_order(
            instId=f"{self._symb}-USDT-SWAP",
            tdMode="cross",
            side="sell" if side == "short" else "buy",
            ordType="market",
            sz=qty,
        )
        return order

    async def place_order(self, qty: float, side: str, exchange: str) -> dict:
        if self.format_query(exchange) == "binance":
            order = self.place_binance_order(qty, side)
        elif self.format_query(exchange) == "bybit":
            order = self.place_bybit_order(qty, side)
        elif self.format_query(exchange) == "okx":
            order = self.place_okx_order(qty, side)

        return order

    async def place_orders(
        self, qty: float, parts: int, long_side_exchange: str
    ) -> List[dict]:
        short_side_exchange = self._exchanges[
            1 - self._exchanges.index(long_side_exchange)
        ]

        loop = asyncio.get_event_loop()
        tasks = []

        for i in range(parts):
            tasks.append(
                loop.run_in_executor(
                    None, self.place_order, qty, "long", long_side_exchange
                )
            )
            tasks.append(
                loop.run_in_executor(
                    None, self.place_order, qty, "short", short_side_exchange
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
