import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from DataDownloader import DataDownloader


def SetupLogging() -> None:
    LogsPath = Path("Logs")
    LogsPath.mkdir(exist_ok=True)
    Handler = RotatingFileHandler(LogsPath / "app.log", maxBytes=1000000, backupCount=3)
    Formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    Handler.setFormatter(Formatter)
    logging.getLogger().addHandler(Handler)
    logging.getLogger().setLevel(logging.INFO)


def Main() -> None:
    SetupLogging()
    Downloader = DataDownloader()
    Data = Downloader.DownloadData("AAPL", "2024-01-01", "2024-01-31", "1d")
    print(Data.head())


if __name__ == "__main__":
    Main()
