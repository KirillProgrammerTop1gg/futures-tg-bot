from binance.um_futures import UMFutures
import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.PublicData as PublicData
from pybit.unified_trading import HTTP
from typing import Optional, Union, Dict, List


class exchanges_API:
    @staticmethod
    
    def __init__(
        self, BINANCE_KEYS: Dict[str], BYBIT_KEYS: Dict[str], OKX_KEYS: Dict[str]
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

    def get_binance_info(self, symb: str):
        assets = self.binance_client.exchange_info()["symbols"]

        for asset in assets:
            if asset["symbol"] == f"{symb}USDT":
                contract_info = asset["filters"][2]
                return f"BINANCE {symb} CONTRACT:\nMin Qty: {contract_info['minQty']} {symb}\nMax Qty: {contract_info['maxQty']} {symb}\nTrade Step: {contract_info['stepSize']}"

    def get_bybit_info(self, symb: str):
        contract_info = self.bybit_client.get_instruments_info(
            category="linear", symbol=f"{symb}USDT"
        )["result"]["list"][0]["lotSizeFilter"]

        return f"BYBIT {symb} CONTRACT:\nMin Qty: {contract_info['minOrderQty']} {symb}\nMax Qty: {contract_info['maxOrderQty']} {symb}\nTrade Step: {contract_info['qtyStep']}"

    def get_okx_info(self, symb: str):
        contract_info = self.okx_public_client.get_instruments(
            instType="SWAP", instId=f"{symb}-USDT-SWAP"
        )["data"][0]

        return f"OKX {symb} CONTRACT:\nMin Qty: {contract_info['minSz']} {symb}\nMax Qty: {contract_info['maxLmtSz']} {symb}\nTrade Step: {contract_info['lotSz']}"

    def exchange_info(self, exchange: str, symb: str):
        if exchange.
