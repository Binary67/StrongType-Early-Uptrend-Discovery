import logging
from pathlib import Path

from ConfigManager import ConfigManager
import pandas as pd
from LoggerSetup import LoggerSetup
from DataDownloader import YFinanceDownloader
from DataLabel import DataLabel
from DataPreprocessor import DataPreprocessor
from StrongTypeRegistry import StrongTypeRegistry
from IndicatorFactory import IndicatorFactory
from GpPrimitiveSetBuilder import GpPrimitiveSetBuilder


def main() -> None:
    LogSetup = LoggerSetup()
    LogFile = LogSetup.InitializeLogger()
    Config = ConfigManager()
    Parameters = Config.LoadConfig()
    Logger = logging.getLogger(__name__)
    Logger.info("Application started; logging to %s", LogFile)
    Logger.info("Loaded configuration: %s", Parameters)

    Downloader = YFinanceDownloader(
        StartDate="2020-01-01",
        EndDate="2020-12-31",
        Interval="1d",
    )
    try:
        Data = Downloader.DownloadWithCache()
        Logger.info(
            "Downloaded %d rows for ticker %s",
            len(Data),
            Downloader.Ticker,
        )
        if Data.empty:
            raise ValueError("Downloaded data is empty")
    except Exception as Exc:
        Logger.exception("Data download failed: %s", Exc)
        Data = pd.DataFrame(
            {
                "Open": [1.0 + 0.01 * i for i in range(20)],
                "High": [1.1 + 0.01 * i for i in range(20)],
                "Low": [0.9 + 0.01 * i for i in range(20)],
                "Close": [1.0 + 0.01 * i for i in range(20)],
                "Volume": [100 + i for i in range(20)],
            },
            index=pd.date_range("2020-01-01", periods=20, freq="D"),
        )

    Preprocessor = DataPreprocessor()
    Data = Preprocessor.ResampleTimeSeries(Data, "1D")
    Data = Preprocessor.HandleMissingValues(Data, "ffill")
    TrainDf, ValidationDf, TestDf = Preprocessor.SplitTrainTestSets(
        Data, 0.7, 0.15
    )

    Labeler = DataLabel(Data)
    LabeledData = Labeler.LabelUptrend()
    Logger.info("Labelled data with %d rows", len(LabeledData))

    Registry = StrongTypeRegistry()
    Registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    Registry.RegisterType(
        "PriceSeries",
        list,
        lambda x: all(isinstance(v, (int, float)) for v in x),
    )
    Registry.RegisterType(
        "WindowLength", int, lambda x: isinstance(x, int) and x > 0
    )
    Registry._compatibility["PriceSeries"] = {"PriceSeries", "Scalar"}
    Registry.ValidateTypeCompatibility("PriceSeries", "Scalar")
    Registry.EnforceTypeOnArgument(1.0, "Scalar")
    Logger.info("Registered types: %s", Registry.ListRegisteredTypes())

    Factory = IndicatorFactory(Registry)

    def _SimpleMovingAverage(Series: list[float], Length: int) -> float:
        return sum(Series[-Length:]) / Length

    Factory.RegisterIndicatorFunction(
        "SMA",
        _SimpleMovingAverage,
        ("PriceSeries", "WindowLength"),
        "Scalar",
    )
    Example = Factory.ComputeIndicator("SMA", ([1.0, 2.0, 3.0, 4.0], 2))
    Logger.info("Example SMA calculation: %.2f", Example)

    Builder = GpPrimitiveSetBuilder()
    PrimitiveSet = Builder.BuildPrimitiveSet(Factory, Registry)
    Builder.AddTerminalNodes(
        PrimitiveSet,
        {"Prices": ([1.0, 2.0, 3.0], "PriceSeries")},
    )
    Builder.ValidatePrimitiveSet(PrimitiveSet)
    ExportPath = Builder.ExportPrimitiveSet(PrimitiveSet, Path("Primitives"))
    Logger.info("Primitive set exported to %s", ExportPath)


if __name__ == "__main__":
    main()
