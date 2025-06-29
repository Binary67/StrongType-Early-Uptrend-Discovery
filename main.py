from DataDownloader import DataDownloader
from LogManager import LogManager
from ConfigManager import ConfigManager
from Indicator import Indicator
from GPPrimitives import GPPrimitives
from GPPopulation import GPPopulation
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
    PopulationGen = GPPopulation(Primitives, Config)
    Downloader.DownloadData(
        Params["TickerSymbol"],
        Params["StartDate"],
        Params["EndDate"],
        Params["Interval"],
    )
    # Build primitive set to ensure all primitives are registered
    Pset = Primitives.GetPrimitiveSet()
    logging.getLogger(__name__).info(
        "Primitive set ready with %d primitives",
        sum(len(V) for V in Pset.primitives.values()),
    )
    PopulationGen.Generate()


if __name__ == "__main__":
    Main()
