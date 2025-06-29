from DataDownloader import DataDownloader
from LogManager import LogManager
from ConfigManager import ConfigManager
from Indicator import Indicator
from GPPrimitives import GPPrimitives, PriceSeries
import logging


def SetupLogging() -> LogManager:
    """Initialize logging using :class:`LogManager`."""
    return LogManager()


def Main() -> None:
    SetupLogging()
    Config = ConfigManager()
    Params = Config.GetParams()
    Downloader = DataDownloader()
    Technicals = Indicator()
    Primitives = GPPrimitives(Technicals)
    Data = Downloader.DownloadData(
        Params["TickerSymbol"],
        Params["StartDate"],
        Params["EndDate"],
        Params["Interval"],
    )
    Close = PriceSeries(Data["Close"])
    # Build primitive set to ensure all primitives are registered
    Pset = Primitives.GetPrimitiveSet()
    logging.getLogger(__name__).info(
        "Primitive set ready with %d primitives",
        sum(len(V) for V in Pset.primitives.values()),
    )
    Ema12 = Technicals.EMA(Close.Values, 12)
    print(Ema12.tail())


if __name__ == "__main__":
    Main()
