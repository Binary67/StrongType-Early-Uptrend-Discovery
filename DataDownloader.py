import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pandas as pd
import yfinance as yf


class DataDownloader:
    """Download and cache trading data from yfinance."""

    def __init__(self, CacheDir: str = "Cache") -> None:
        self.CacheDir = Path(CacheDir)
        self.CacheDir.mkdir(parents=True, exist_ok=True)
        self.Logger = logging.getLogger(self.__class__.__name__)
        if not self.Logger.handlers:
            LogsPath = Path("Logs")
            LogsPath.mkdir(exist_ok=True)
            Handler = RotatingFileHandler(LogsPath / "data_downloader.log", maxBytes=1000000, backupCount=3)
            Formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            Handler.setFormatter(Formatter)
            self.Logger.addHandler(Handler)
            self.Logger.setLevel(logging.INFO)

    def _GetCacheFilePath(self, TickerSymbol: str, StartDate: str, EndDate: str, Interval: str) -> Path:
        FileName = f"{TickerSymbol}_{StartDate}_{EndDate}_{Interval}.csv"
        return self.CacheDir / FileName

    def DownloadData(self, TickerSymbol: str, StartDate: str, EndDate: str, Interval: str = "1d") -> pd.DataFrame:
        """Download data from yfinance with caching."""
        CacheFile = self._GetCacheFilePath(TickerSymbol, StartDate, EndDate, Interval)
        if CacheFile.exists():
            self.Logger.info("Loading data from cache: %s", CacheFile)
            Data = pd.read_csv(CacheFile, index_col=0, parse_dates=True)
            return Data

        self.Logger.info("Downloading data for %s", TickerSymbol)
        try:
            Data = yf.download(TickerSymbol, start=StartDate, end=EndDate, interval=Interval, auto_adjust=False)
        except Exception as Error:  # pragma: no cover - network error logging
            self.Logger.error("Failed to download data: %s", Error)
            raise

        if isinstance(Data.columns, pd.MultiIndex):
            Data.columns = Data.columns.droplevel(1)

        Columns = ["Open", "High", "Low", "Close", "Volume"]
        Data = Data[Columns]
        Data.to_csv(CacheFile)
        return Data
