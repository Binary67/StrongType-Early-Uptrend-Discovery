import os
import sys
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DataDownloader import YFinanceDownloader


def test_download_with_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    config_path = tmp_path / "config.yaml"
    config_path.write_text("Ticker: TEST")

    df = pd.DataFrame(
        {"Close": [1, 2, 3]},
        index=pd.date_range("2020-01-01", periods=3),
    )

    def fake_download(*args, **kwargs):
        fake_download.called = True
        return df

    monkeypatch.setattr(yf, "download", fake_download)
    downloader = YFinanceDownloader(
        StartDate="2020-01-01",
        EndDate="2020-01-03",
        Interval="1d",
        ConfigPath=str(config_path),
    )
    data1 = downloader.DownloadWithCache(str(cache_dir))
    assert fake_download.called
    cache_file = cache_dir / "TEST_20200101_20200103_1d.csv"
    assert cache_file.is_file()
    assert not data1.empty

    def fail_download(*args, **kwargs):
        raise AssertionError("Should use cache")

    monkeypatch.setattr(yf, "download", fail_download)
    data2 = downloader.DownloadWithCache(str(cache_dir))
    assert data2.equals(data1)
