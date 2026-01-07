from dataclasses import dataclass
import pandas as pd
from indicators import sma, atr

@dataclass
class MACrossoverATR:
    fast: int = 50
    slow: int = 200
    atr_mult: float = 1.5

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["sma_fast"] = sma(df, self.fast)
        df["sma_slow"] = sma(df, self.slow)
        df["atr"] = atr(df)
        df["signal"] = 0

        long_cond = (df["sma_fast"] > df["sma_slow"]) & (df["close"] > df["sma_slow"])
        short_cond = (df["sma_fast"] < df["sma_slow"]) & (df["close"] < df["sma_slow"])

        df.loc[long_cond & (~long_cond.shift().fillna(False)), "signal"] = 1
        df.loc[short_cond & (~short_cond.shift().fillna(False)), "signal"] = -1

        return df
