import os
from typing import Optional
import pandas as pd
from DataDownloader import YFinanceDownloader


class DailyOHLCVLoader:
    """Load daily OHLCV data from yfinance or CSV with caching."""

    def __init__(self, Source: str, Ticker: Optional[str] = None,
                 CsvPath: Optional[str] = None, StartDate: Optional[str] = None,
                 EndDate: Optional[str] = None) -> None:
        self.Source = Source.lower()
        self.Ticker = Ticker
        self.CsvPath = CsvPath
        self.StartDate = StartDate
        self.EndDate = EndDate
        if self.Source not in ("yfinance", "csv"):
            raise ValueError("Source must be 'yfinance' or 'csv'")
        if self.Source == "csv" and not self.CsvPath:
            raise ValueError("CsvPath required for csv source")
        if self.Source == "yfinance" and not self.Ticker:
            raise ValueError("Ticker required for yfinance source")

    def Load(self) -> pd.DataFrame:
        if self.Source == "yfinance":
            return self._LoadYFinance()
        return self._LoadCsv()

    def _LoadYFinance(self) -> pd.DataFrame:
        CachePath = self._CachePath()
        if os.path.exists(CachePath):
            DataFrame = pd.read_csv(CachePath, index_col=0, parse_dates=True)
        else:
            Downloader = YFinanceDownloader(self.Ticker, self.StartDate,
                                             self.EndDate, "1d")
            DataFrame = Downloader.DownloadData()
            os.makedirs("data", exist_ok=True)
            DataFrame.to_csv(CachePath)
        return self._PrepareData(DataFrame)

    def _LoadCsv(self) -> pd.DataFrame:
        DataFrame = pd.read_csv(self.CsvPath, index_col=0, parse_dates=True)
        return self._PrepareData(DataFrame)

    def _CachePath(self) -> str:
        SafeStart = str(self.StartDate).replace("-", "") if self.StartDate else ""
        SafeEnd = str(self.EndDate).replace("-", "") if self.EndDate else ""
        FileName = f"{self.Ticker}_{SafeStart}_{SafeEnd}_1d.csv"
        return os.path.join("data", FileName)

    def _PrepareData(self, DataFrame: pd.DataFrame) -> pd.DataFrame:
        DataFrame = DataFrame.copy()
        if "Adj Close" in DataFrame.columns:
            Factor = DataFrame["Adj Close"] / DataFrame["Close"]
            for Column in ["Open", "High", "Low", "Close"]:
                if Column in DataFrame:
                    DataFrame[Column] = DataFrame[Column] * Factor
            DataFrame.drop(columns=["Adj Close"], inplace=True)
        if not DataFrame.index.is_monotonic_increasing:
            DataFrame.sort_index(inplace=True)
        ExpectedIndex = pd.date_range(DataFrame.index.min(),
                                      DataFrame.index.max(), freq="D")
        if not ExpectedIndex.equals(DataFrame.index):
            raise ValueError("Missing daily bars detected")
        for Column in ["Open", "High", "Low", "Close", "Volume"]:
            if Column in DataFrame.columns:
                DataFrame[Column] = pd.to_numeric(DataFrame[Column], errors="coerce")
        DataFrame.dropna(inplace=True)
        return DataFrame


class FeatureMatrixBuilder:
    """Construct feature matrix with price, volume and indicators."""

    def __init__(self, DataFrame: pd.DataFrame) -> None:
        self.DataFrame = DataFrame

    def Build(self) -> pd.DataFrame:
        DataFrame = self.DataFrame.copy()
        DataFrame["Ema12"] = DataFrame["Close"].ewm(span=12, adjust=False).mean()
        DataFrame["Ema50"] = DataFrame["Close"].ewm(span=50, adjust=False).mean()
        Delta = DataFrame["Close"].diff()
        Gain = Delta.clip(lower=0)
        Loss = -Delta.clip(upper=0)
        AvgGain = Gain.rolling(window=14, min_periods=14).mean()
        AvgLoss = Loss.rolling(window=14, min_periods=14).mean()
        Rs = AvgGain / AvgLoss
        DataFrame["Rsi14"] = 100 - (100 / (1 + Rs))
        HighLow = DataFrame["High"] - DataFrame["Low"]
        HighClose = (DataFrame["High"] - DataFrame["Close"].shift()).abs()
        LowClose = (DataFrame["Low"] - DataFrame["Close"].shift()).abs()
        Tr = pd.concat([HighLow, HighClose, LowClose], axis=1).max(axis=1)
        DataFrame["Atr14"] = Tr.rolling(window=14, min_periods=14).mean()
        DataFrame.dropna(inplace=True)
        Columns = ["Open", "High", "Low", "Close", "Volume",
                   "Ema12", "Ema50", "Rsi14", "Atr14"]
        FeatureMatrix = DataFrame[Columns].astype("float64")
        return FeatureMatrix

