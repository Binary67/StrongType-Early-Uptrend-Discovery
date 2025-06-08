import pandas as pd


def CalculateEma(DataSeries: pd.Series, Span: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA) for a data series."""
    return DataSeries.ewm(span=Span, adjust=False).mean()


def CalculateRsi(DataSeries: pd.Series, Period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI) for a data series."""
    Delta = DataSeries.diff()
    Gain = Delta.where(Delta > 0, 0.0)
    Loss = -Delta.where(Delta < 0, 0.0)
    AvgGain = Gain.rolling(window=Period).mean()
    AvgLoss = Loss.rolling(window=Period).mean()
    Rs = AvgGain / AvgLoss
    Rsi = 100 - (100 / (1 + Rs))
    return Rsi


def CalculateMacd(DataSeries: pd.Series,
                  FastPeriod: int = 12,
                  SlowPeriod: int = 26,
                  SignalPeriod: int = 9) -> pd.DataFrame:
    """Calculate Moving Average Convergence Divergence (MACD)."""
    EmaFast = CalculateEma(DataSeries, FastPeriod)
    EmaSlow = CalculateEma(DataSeries, SlowPeriod)
    MacdLine = EmaFast - EmaSlow
    SignalLine = CalculateEma(MacdLine, SignalPeriod)
    Histogram = MacdLine - SignalLine
    return pd.DataFrame({
        'Macd': MacdLine,
        'Signal': SignalLine,
        'Histogram': Histogram
    })
