from DataDownloader import DataDownloader
from LogManager import LogManager
from ConfigManager import ConfigManager


def SetupLogging() -> LogManager:
    """Initialize logging using :class:`LogManager`."""
    return LogManager()


def Main() -> None:
    SetupLogging()
    Config = ConfigManager()
    Params = Config.GetParams()
    Downloader = DataDownloader()
    Data = Downloader.DownloadData(
        Params["TickerSymbol"],
        Params["StartDate"],
        Params["EndDate"],
        Params["Interval"],
    )
    print(Data.head())


if __name__ == "__main__":
    Main()
