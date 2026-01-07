import time
from datetime import datetime
from strategy import MACrossoverATR
from broker import fetch_ohlc, place_market_order
from risk import price_to_pips, position_size, compute_levels

def in_session():
    now = datetime.utcnow().strftime("%H:%M")
    return "07:00" <= now <= "18:00"


def run(pair="EUR_USD", timeframe="M15", balance=10000):
    strat = MACrossoverATR()
    position_open = False

    while True:
        df = fetch_ohlc(pair, timeframe, 600)
        df = strat.generate(df)
        row = df.iloc[-1]

        if not in_session():
            time.sleep(60)
            continue

        if not position_open and row["signal"] != 0:
            sl, tp, stop_dist = compute_levels(
                row["signal"], row["close"], row["atr"], strat.atr_mult, 1.5
            )
            stop_pips = price_to_pips(pair, stop_dist)
            units = position_size(balance, 0.01, stop_pips, 0.0001)
            side = "buy" if row["signal"] == 1 else "sell"

            print(f"{side.upper()} {pair} units={units}")
            # UNCOMMENT AFTER TESTING
            # place_market_order(pair, units, side, sl, tp)
            position_open = True

        time.sleep(60)
