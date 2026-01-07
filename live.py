import time
from loguru import logger
from .strategy import MACrossoverATR
from .broker import fetch_ohlc, place_market_order
from .risk import position_size, compute_levels

def should_trade_now(now_utc_hhmm: str, start="07:00", end="18:00"):
    return start <= now_utc_hhmm <= end

def run(pair="EUR_USD", granularity="M15", balance=10000, risk_frac=0.01, pip_value=0.0001):
    strat = MACrossoverATR()
    logger.add("logs/runtime.log", rotation="1 day")
    logger.info(f"Starting bot for {pair} {granularity}")
    position_open = False

    while True:
        try:
            df = fetch_ohlc(pair, granularity, count=600)
            sig_df = strat.generate(df)
            row = sig_df.iloc[-1]
            # Session filter
            hhmm = row["time"][11:16]  # crude UTC slice
            if not should_trade_now(hhmm):
                time.sleep(60); continue

            if not position_open and row["signal"] != 0:
                sl, tp, stop_dist = compute_levels(row["signal"], row["close"], row["atr"], strat.atr_mult, rr=1.5)
                stop_pips = stop_dist
                units = position_size(balance, risk_frac, stop_pips, pip_value)
                side = "buy" if row["signal"] == 1 else "sell"
                logger.info(f"Signal {side} units={units} price={row['close']} sl={sl} tp={tp}")
                # DEMO ONLY: log instead of placing orders until verified
                # place_market_order(pair, units, side, sl, tp)
                position_open = True

            time.sleep(60)
        except Exception as e:
            logger.exception(f"Loop error: {e}")
            time.sleep(15)