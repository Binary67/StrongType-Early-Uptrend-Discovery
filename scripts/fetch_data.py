import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Callable, List, Optional


class DailyOhlcvLoader:
    """Load OHLCV bars either from yfinance or a CSV file with caching."""

    def __init__(self, source: str = "yfinance", data_dir: str = "data") -> None:
        self.Source = source
        self.DataDir = Path(data_dir)
        self.DataDir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, ticker: str, start: str, end: str, interval: str) -> Path:
        file_name = f"{ticker}_{start}_{end}_{interval}.csv"
        return self.DataDir / file_name

    def _validate_dataframe(self, df: pd.DataFrame, start: str, end: str, interval: str) -> None:
        """Basic sanity checks on the returned DataFrame."""
        if df.empty:
            raise ValueError("Returned DataFrame is empty")
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError("DataFrame index must be DatetimeIndex")
        if not df.index.is_monotonic_increasing:
            raise ValueError("DataFrame index must be sorted and unique")
        # Simple missing-bar check
        expected_range = pd.date_range(start=start, end=end, freq=interval)
        missing = expected_range.difference(df.index)
        if not missing.empty:
            raise ValueError(f"Missing bars detected: {missing[:3]} ...")
        # Ensure float dtype for numerical columns
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    def load(self, ticker: str, start: str, end: str, interval: str = "1d", csv_path: Optional[str] = None) -> pd.DataFrame:
        cache_path = self._cache_path(ticker, start, end, interval)
        if cache_path.exists():
            df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            self._validate_dataframe(df, start, end, interval)
            return df

        if self.Source == "yfinance":
            df = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
        elif self.Source == "csv":
            if csv_path is None:
                raise ValueError("csv_path must be provided when source='csv'")
            df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        else:
            raise ValueError(f"Unsupported source: {self.Source}")

        self._validate_dataframe(df, start, end, interval)
        df.to_csv(cache_path)
        return df


class FeatureMatrixBuilder:
    """Combine OHLCV data and indicator columns into a single DataFrame."""

    def __init__(self, indicator_functions: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None) -> None:
        self.IndicatorFunctions = indicator_functions or []

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        features = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        for func in self.IndicatorFunctions:
            features[func.__name__] = func(df)
        return features
