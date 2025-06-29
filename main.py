from DataDownloader import DataDownloader
from LogManager import LogManager
from ConfigManager import ConfigManager
from Indicator import Indicator


def SetupLogging() -> LogManager:
    """Initialize logging using :class:`LogManager`."""
    return LogManager()


def Main() -> None:
    SetupLogging()
    Config = ConfigManager()
    Params = Config.GetParams()
    Downloader = DataDownloader()
    Technicals = Indicator()
    Data = Downloader.DownloadData(
        Params["TickerSymbol"],
        Params["StartDate"],
        Params["EndDate"],
        Params["Interval"],
    )
    Close = Data["Close"]
    Ema12 = Technicals.EMA(Close, 12)
    print(Ema12.tail())


if __name__ == "__main__":
    Main()
