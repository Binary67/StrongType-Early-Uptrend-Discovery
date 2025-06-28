import os
import pandas as pd
import yfinance as yf
from ConfigManager import ConfigManager

class YFinanceDownloader:
    """Download OHLCV data from yfinance based on configuration."""

    def __init__(self, StartDate: str, EndDate: str, Interval: str,
                 ConfigPath: str = "Config.yaml") -> None:
        Config = ConfigManager(ConfigPath)
        ConfigData = Config.LoadConfig()
        self.Ticker = ConfigData.get("Ticker", "AAPL")
        self.StartDate = pd.to_datetime(StartDate)
        self.EndDate = pd.to_datetime(EndDate)
        self.Interval = Interval

    def DownloadData(self):
        # For hourly data, yfinance limits the period that can be downloaded.
        # We define common hourly interval labels.
        HourlyIntervals = ['60m', '1h', 'hourly']
        if self.Interval in HourlyIntervals:
            # If the total period exceeds 2 weeks (14 days), split into 2-week segments.
            if (self.EndDate - self.StartDate).days > 14:
                DataFrames = []
                CurrentStart = self.StartDate
                while CurrentStart < self.EndDate:
                    CurrentEnd = CurrentStart + pd.Timedelta(days=14)

                    if CurrentEnd > self.EndDate:
                        CurrentEnd = self.EndDate

                    TempData = yf.download(
                        self.Ticker,
                        start=CurrentStart.strftime('%Y-%m-%d'),
                        end=CurrentEnd.strftime('%Y-%m-%d'),
                        interval=self.Interval,
                        progress=False
                    )

                    if isinstance(TempData.columns, pd.MultiIndex):
                        TempData.columns = TempData.columns.droplevel(1)

                    DataFrames.append(TempData)
                    CurrentStart = CurrentEnd

                if DataFrames:
                    FinalDf = pd.concat(DataFrames)
                    return FinalDf
                
        # For non-hourly data or periods within the 2-week limit, download directly.
        FinalDf = yf.download(
            self.Ticker,
            start=self.StartDate.strftime('%Y-%m-%d'),
            end=self.EndDate.strftime('%Y-%m-%d'),
            interval=self.Interval,
            progress=False
        )

        if isinstance(FinalDf.columns, pd.MultiIndex):
            FinalDf.columns = FinalDf.columns.droplevel(1)

        FinalDf.columns.name = None

        return FinalDf

    def DownloadWithCache(self, CacheDirectory: str = "Cache"):
        """Return data from cache or download and cache it.

        Args:
            CacheDirectory: Directory to store cached CSV files.

        Returns:
            pd.DataFrame: The OHLCV data.
        """
        os.makedirs(CacheDirectory, exist_ok=True)
        FileName = (
            f"{self.Ticker}_"
            f"{self.StartDate.strftime('%Y%m%d')}_"
            f"{self.EndDate.strftime('%Y%m%d')}_"
            f"{self.Interval}.csv"
        )
        CachePath = os.path.join(CacheDirectory, FileName)
        if os.path.isfile(CachePath):
            Data = pd.read_csv(CachePath, index_col=0, parse_dates=True)
            return Data

        Data = self.DownloadData()
        Data.to_csv(CachePath)
        return Data
