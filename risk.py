def price_to_pips(pair: str, price_dist: float) -> float:
    if pair.endswith("JPY"):
        return price_dist / 0.01
    return price_dist / 0.0001


def position_size(balance: float, risk_frac: float, stop_pips: float, pip_value: float):
    risk_amount = balance * risk_frac
    units = risk_amount / (stop_pips * pip_value)
    return max(1, int(units))


def compute_levels(side: int, price: float, atr_value: float, atr_mult: float, rr: float):
    stop_dist = atr_mult * atr_value

    if side == 1:  # BUY
        sl = price - stop_dist
        tp = price + stop_dist * rr
    else:          # SELL
        sl = price + stop_dist
        tp = price - stop_dist * rr

    return sl, tp, stop_dist
