import os
import requests
import pandas as pd
from .test_env import load_dotenv

load_dotenv()

API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
ENV = os.getenv("OANDA_ENV", "practice")

BASE = "https://api-fxpractice.oanda.com" if ENV == "practice" else "https://api-fxtrade.oanda.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def fetch_ohlc(pair: str, granularity="M15", count=500):
    url = f"{BASE}/v3/instruments/{pair}/candles"
    params = {"granularity": granularity, "count": count, "price": "M"}
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    candles = r.json()["candles"]
    df = pd.DataFrame([{
        "time": c["time"],
        "open": float(c["mid"]["o"]),
        "high": float(c["mid"]["h"]),
        "low": float(c["mid"]["l"]),
        "close": float(c["mid"]["c"]),
        "volume": c["volume"]
    } for c in candles])

    return df


def place_market_order(pair, units, side, sl, tp):
    url = f"{BASE}/v3/accounts/{ACCOUNT_ID}/orders"
    body = {
        "order": {
            "instrument": pair,
            "units": str(units if side == "buy" else -units),
            "type": "MARKET",
            "timeInForce": "FOK",
            "stopLossOnFill": {"price": f"{sl:.5f}"},
            "takeProfitOnFill": {"price": f"{tp:.5f}"}
        }
    }

    r = requests.post(url, headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()
