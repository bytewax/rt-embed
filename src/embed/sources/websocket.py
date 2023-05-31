import os
import json

from bytewax.inputs import DynamicInput, StatelessSource
from websocket import create_connection

ALPACA_API_KEY = os.getenv("API_KEY")
ALPACA_API_SECRET = os.getenv("API_SECRET")


class AlpacaSource(StatelessSource):
    def __init__(self, worker_tickers):
        self.worker_tickers = worker_tickers

        self.ws = create_connection("wss://stream.data.alpaca.markets/v1beta1/news")
        print(self.ws.recv())
        if not ALPACA_API_KEY and not ALPACA_API_SECRET:
            raise "No API KEY or API SECRET, please save as environment variables before continuing"
        self.ws.send(
            json.dumps(
                {"action": "auth", "key": f"{API_KEY}", "secret": f"{API_SECRET}"}
            )
        )
        print(self.ws.recv())
        self.ws.send(json.dumps({"action": "subscribe", "news": self.worker_tickers}))
        print(self.ws.recv())

    def next(self):
        return self.ws.recv()


class AlpacaNewsInput(DynamicInput):
    def __init__(self, tickers):
        self.tickers = tickers

    def build(self, worker_index, worker_count):
        prods_per_worker = int(len(self.tickers) / worker_count)
        worker_tickers = self.tickers[
            int(worker_index * prods_per_worker) : int(
                worker_index * prods_per_worker + prods_per_worker
            )
        ]
        return AlpacaSource(worker_tickers)
