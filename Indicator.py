import pandas as pd
from typing import Callable, Dict, List


class Indicator:
    """Provide and register technical indicator functions."""

    def __init__(self) -> None:
        self.Functions: Dict[str, Callable[..., pd.DataFrame | pd.Series]] = {}
        self._RegisterBuiltIns()

    def _RegisterBuiltIns(self) -> None:
        self.RegisterIndicator("EMA", self.EMA)
        self.RegisterIndicator("SMA", self.SMA)
        self.RegisterIndicator("MACD", self.MACD)
        self.RegisterIndicator("RSI", self.RSI)
        self.RegisterIndicator("BB", self.BB)

    def RegisterIndicator(self, Name: str, Func: Callable[..., pd.DataFrame | pd.Series]) -> None:
        """Register a custom technical indicator."""
        self.Functions[Name] = Func

    def GetIndicator(self, Name: str) -> Callable[..., pd.DataFrame | pd.Series]:
        """Retrieve a previously registered indicator function."""
        return self.Functions[Name]

    def GetRegisteredIndicators(self) -> List[str]:
        """Return a list of registered indicator names."""
        return list(self.Functions.keys())

    # --- Indicator implementations ---
    @staticmethod
    def EMA(PriceSeries: pd.Series, WindowLength: int) -> pd.Series:
        """Exponential moving average."""
        return PriceSeries.ewm(span=WindowLength, adjust=False).mean()

    @staticmethod
    def SMA(PriceSeries: pd.Series, WindowLength: int) -> pd.Series:
        """Simple moving average."""
        return PriceSeries.rolling(window=WindowLength).mean()

    @staticmethod
    def MACD(
        PriceSeries: pd.Series,
        FastPeriod: int = 12,
        SlowPeriod: int = 26,
        SignalPeriod: int = 9,
    ) -> pd.DataFrame:
        """Moving Average Convergence Divergence."""
        FastEMA = Indicator.EMA(PriceSeries, FastPeriod)
        SlowEMA = Indicator.EMA(PriceSeries, SlowPeriod)
        MACDLine = FastEMA - SlowEMA
        SignalLine = Indicator.EMA(MACDLine, SignalPeriod)
        return pd.DataFrame({"MACD": MACDLine, "Signal": SignalLine})

    @staticmethod
    def RSI(PriceSeries: pd.Series, WindowLength: int = 14) -> pd.Series:
        """Relative Strength Index."""
        Delta = PriceSeries.diff()
        Gain = Delta.clip(lower=0)
        Loss = -Delta.clip(upper=0)
        AvgGain = Gain.rolling(window=WindowLength).mean()
        AvgLoss = Loss.rolling(window=WindowLength).mean()
        RS = AvgGain / AvgLoss
        return 100 - 100 / (1 + RS)

    @staticmethod
    def BB(
        PriceSeries: pd.Series,
        WindowLength: int = 20,
        NumStdDev: float = 2.0,
    ) -> pd.DataFrame:
        """Bollinger Bands."""
        MiddleBand = Indicator.SMA(PriceSeries, WindowLength)
        StdDev = PriceSeries.rolling(window=WindowLength).std()
        UpperBand = MiddleBand + NumStdDev * StdDev
        LowerBand = MiddleBand - NumStdDev * StdDev
        return pd.DataFrame(
            {
                "UpperBand": UpperBand,
                "MiddleBand": MiddleBand,
                "LowerBand": LowerBand,
            }
        )
