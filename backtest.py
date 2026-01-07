from strategy import MACrossoverATR
from risk import price_to_pips, position_size, compute_levels

def backtest(df, pair, balance=10000, risk_frac=0.01, pip_value=0.0001):
    strat = MACrossoverATR()
    df = strat.generate(df)

    position = 0
    entry_price = None
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]

        if position == 0 and row["signal"] != 0:
            sl, tp, stop_dist = compute_levels(
                row["signal"], row["close"], row["atr"], strat.atr_mult, 1.5
            )
            stop_pips = price_to_pips(pair, stop_dist)
            units = position_size(balance, risk_frac, stop_pips, pip_value)
            position = row["signal"] * units
            entry_price = row["close"]

        elif position != 0:
            exit_long = position > 0 and row["sma_fast"] < row["sma_slow"]
            exit_short = position < 0 and row["sma_fast"] > row["sma_slow"]

            if exit_long or exit_short:
                pnl = (row["close"] - entry_price) * position
                balance += pnl
                trades.append(pnl)
                position = 0

    return {
        "final_balance": balance,
        "trades": len(trades),
        "total_pnl": sum(trades),
        "avg_trade": sum(trades) / len(trades) if trades else 0
    }
