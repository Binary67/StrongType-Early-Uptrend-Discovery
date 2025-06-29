from DataDownloader import DataDownloader
from LogManager import LogManager
from ConfigManager import ConfigManager
from Indicator import Indicator
from GPPrimitives import GPPrimitives
from GPPopulation import GPPopulation
from DataLabel import DataLabel
import logging

from EvaluateFitness import EvaluateFitness

def SetupLogging() -> LogManager:
    """Initialize logging using :class:`LogManager`."""
    return LogManager()


def Main() -> None:
    SetupLogging()
    Config = ConfigManager()
    Params = Config.GetParams()
    Downloader = DataDownloader()
    Technicals = Indicator()
    Labeler = DataLabel(Technicals)
    Primitives = GPPrimitives(Technicals)
    PopulationGen = GPPopulation(Primitives, Config)
    Data = Downloader.DownloadData(
        Params["TickerSymbol"],
        Params["StartDate"],
        Params["EndDate"],
        Params["Interval"],
    )
    Data = Labeler.AddLabel(Data)
    # Build primitive set to ensure all primitives are registered
    Pset = Primitives.GetPrimitiveSet()
    logging.getLogger(__name__).info(
        "Primitive set ready with %d primitives",
        sum(len(V) for V in Pset.primitives.values()),
    )
    Evaluator = EvaluateFitness(Data, Primitives)
    Population = PopulationGen.Generate()
    for Formula in Population:
        Score = Evaluator.ComputeFitness(Formula)
        logging.getLogger(__name__).info("Formula %s fitness %.4f", Formula, Score)


if __name__ == "__main__":
    Main()
