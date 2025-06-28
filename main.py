from DataDownloader import DataDownloader
from LogManager import LogManager


def SetupLogging() -> LogManager:
    """Initialize logging using :class:`LogManager`."""
    return LogManager()


def Main() -> None:
    SetupLogging()
    Downloader = DataDownloader()
    Data = Downloader.DownloadData("AAPL", "2024-01-01", "2024-01-31", "1d")
    print(Data.head())


if __name__ == "__main__":
    Main()
