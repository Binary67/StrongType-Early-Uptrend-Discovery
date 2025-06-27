import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DataDownloader import YFinanceDownloader


def test_yfinance_downloader_reads_config(monkeypatch, tmp_path):
    ConfigPath = tmp_path / "config.yaml"
    ConfigPath.write_text("Ticker: TEST")

    def fake_download(Ticker, start, end, interval, progress=False):
        fake_download.Params = {
            "Ticker": Ticker,
            "Start": start,
            "End": end,
            "Interval": interval,
        }
        return pd.DataFrame({"Close": [1, 2, 3]})

    monkeypatch.setattr(yf, "download", fake_download)

    Downloader = YFinanceDownloader(
        StartDate="2020-01-01",
        EndDate="2020-01-10",
        Interval="1d",
        ConfigPath=str(ConfigPath),
    )
    Data = Downloader.DownloadData()

    assert fake_download.Params["Ticker"] == "TEST"
    assert not Data.empty
