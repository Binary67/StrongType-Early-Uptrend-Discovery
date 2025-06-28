import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import pandas as pd
from unittest.mock import patch
from tempfile import TemporaryDirectory

from DataDownloader import DataDownloader


def _CreateSampleDataFrame() -> pd.DataFrame:
    Index = pd.date_range("2024-01-01", periods=2)
    Columns = pd.MultiIndex.from_product(
        [["Adj Close", "Close", "High", "Low", "Open", "Volume"], ["AAPL"]]
    )
    Data = pd.DataFrame([
        [2, 2, 3, 1, 1, 100],
        [3, 3, 4, 2, 2, 110],
    ], index=Index, columns=Columns)
    return Data


def test_download_data_with_cache() -> None:
    SampleData = _CreateSampleDataFrame()
    with TemporaryDirectory() as TempDir:
        Downloader = DataDownloader(CacheDir=TempDir)
        with patch("yfinance.download", return_value=SampleData) as MockDownload:
            Data = Downloader.DownloadData("AAPL", "2024-01-01", "2024-01-02", "1d")
            assert MockDownload.call_count == 1
            assert list(Data.columns) == ["Open", "High", "Low", "Close", "Volume"]
        with patch("yfinance.download") as MockDownload:
            DataCached = Downloader.DownloadData(
                "AAPL", "2024-01-01", "2024-01-02", "1d"
            )
            assert MockDownload.call_count == 0
            pd.testing.assert_frame_equal(Data, DataCached, check_freq=False)
